import json
import logging
import re
import unicodedata
from typing import Any, Dict
from langchain_openai import ChatOpenAI
import os

from agents.lawyer_agent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent
from agents.repair_chat_agent import run_repair_agent_with_memory 

from agents.tools.router import _get_routing_decision, _should_switch_agent
from agents.tools.orchestrator_utils import _check_explicit_triggers, _safe_json_loads, _normalize_text

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini") 

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
agent_session_state = {}
pending_switch_state: Dict[str, Dict[str, Any]] = {}

ALLOWED_AGENTS = {"lawyer", "insurance", "repair", "general", "reset"}
CONFIDENCE_THRESHOLD = 0.7

HANDOVER_MAP = {
    "repair": lambda msg, sid, ctx: run_repair_agent_with_memory(msg, sid, ctx),
    "lawyer": lambda msg, sid, ctx: handle_lawyer_request(msg, ctx),
    "insurance": lambda msg, sid, ctx: run_insurance_agent(msg, sid, ctx)
}

def _load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        return "{user_message}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

try:
    PROMPT_ROUTE = _load_template("orchestrator_route.md")
except:
    PROMPT_ROUTE = """Classify intent: lawyer, insurance, repair, general. JSON: {"agent": "...", "confidence": 0.0}"""

def _sanitize_agent(agent: Any, default: str = "general") -> str:
    if not isinstance(agent, str): return default
    agent = agent.strip().lower()
    return agent if agent in ALLOWED_AGENTS else default

def _llm_classify_switch_reply(message: str) -> str:
    """Nutzt das LLM, um zu entscheiden, ob der User den Wechsel bestätigt."""
    prompt = (
        "Der Nutzer wurde gefragt, ob er den KI-Experten wechseln möchte. "
        "Klassifiziere die Antwort des Nutzers in eine dieser Kategorien: "
        "'confirm' (ja, einverstanden), 'decline' (nein, ablehnen) oder 'neutral' (unentschlossen/andere Frage).\n\n"
        f"Antwort: '{message}'\n\n"
        "Gib NUR das Wort 'confirm', 'decline' oder 'neutral' zurück."
    )
    
    try:
        # Wir nutzen das bereits definierte llm Objekt
        resp = llm.invoke([("system", "Du bist ein präziser Klassifizierer."), ("human", prompt)])
        decision = resp.content.strip().lower()
        
        # Sicherstellen, dass nur erlaubte Werte zurückkommen
        if "confirm" in decision: return "confirm"
        if "decline" in decision: return "decline"
        return "neutral"
    except Exception as e:
        log.error(f"Fehler bei LLM-Klassifizierung: {e}")
        return "neutral"
    
def handle_general_request(user_message: str, user_name: str = None) -> Dict[str, Any]:
    sys_msg = f"Du bist der persönliche Assistent von {user_name}. Antworte kurz." if user_name else "Du bist ein Assistent. Antworte kurz."
    resp = llm.invoke([("system", sys_msg), ("human", user_message)])
    return {"response": resp.content, "structured": {"intent": "general"}}

def route_message(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    if user_context is None: user_context = {}
    user_email = user_context.get("email")
    session_id = user_context.get("session_id") or user_email or "default_session"
    user_name = user_context.get("name", "User")
    
    log.info(f"Orchestrator: '{user_message}' | Session: {session_id}")

    # 1. Manuelle Reset-Trigger
    if user_message.lower().strip() in ["stop", "abbruch", "reset", "neues thema"]:
        if session_id in agent_session_state: del agent_session_state[session_id]
        return {"response": "Gespräch zurückgesetzt. Wie kann ich helfen?", "agent": "reset", "agent_changed": True}

    # If a switch is pending, let the LLM decide whether the user confirmed.
    pending = pending_switch_state.get(session_id)
    if pending:
        decision = _llm_classify_switch_reply(user_message)
        if decision == "confirm":
            target_agent = pending.get("to_agent", "general")
            original_message = pending.get("original_message") or user_message

            pending_switch_state.pop(session_id, None)

            if target_agent != "general":
                agent_session_state[session_id] = target_agent
            else:
                agent_session_state.pop(session_id, None)

            # Process the original message under the newly selected agent
            if target_agent == "lawyer":
                user_context["session_id"] = session_id
                res = handle_lawyer_request(original_message, user_context)
                return {"response": res.get("response", ""), "structured": res.get("structured", {"intent": "lawyer"}), "agent": "lawyer", "agent_changed": True}
            if target_agent == "insurance":
                res = run_insurance_agent(original_message, session_id, user_context)
                return {"response": res.get("response", ""), "structured": res.get("structured", {"intent": "insurance"}), "agent": "insurance", "agent_changed": True}
            if target_agent == "repair":
                res = run_repair_agent_with_memory(original_message, session_id, user_context)
                return {"response": res.get("response", ""), "structured": res.get("structured", {"intent": "repair"}), "agent": "repair", "agent_changed": True}

            res = handle_general_request(original_message)
            return {"response": res.get("response", ""), "structured": res.get("structured", {"intent": "general"}), "agent": "chatbot", "agent_changed": True}

        if decision == "decline":
            pending_switch_state.pop(session_id, None)
            active = agent_session_state.get(session_id) or "chatbot"
            return {
                "response": "Alles klar – ich bleibe im aktuellen Modus. Was genau brauchst du als Nächstes?",
                "structured": {"intent": active, "switch_cancelled": True},
                "agent": active,
                "agent_changed": False,
            }

        return {
            "response": "Bitte bestätige kurz: Soll ich wirklich den Agent wechseln?",
            "structured": {"awaiting_switch_confirmation": True},
            "agent": pending.get("from_agent", "chatbot"),
            "agent_changed": False,
        }

    active_agent = agent_session_state.get(session_id)
    target_agent = "general"
    agent_changed = False

    # --- NEU: LOGIK FÜR KURZE BESTÄTIGUNGEN ---
    # Wenn wir einen aktiven Agenten haben und die Nachricht nur ein "ja/ok" ist, 
    # NICHT den Router fragen, sondern beim Agenten bleiben.
    confirmations = {"ja", "gerne", "einverstanden", "nein", "ok", "okay", "machen wir", "top", "gut"}
    is_short_text = len(user_message.split()) <= 2
    is_confirm = user_message.lower().strip().rstrip(".!?") in confirmations

    if active_agent and (is_confirm or (is_short_text and is_confirm)):
        target_agent = active_agent
        log.info(f"Kurze Bestätigung erkannt. Bleibe bei active_agent: {target_agent}")
    
    # --- BESTEHENDE ROUTING LOGIK ---
    elif active_agent:
        should_switch, new_agent, confidence = _should_switch_agent(llm, active_agent, user_message, _sanitize_agent)
        if should_switch and confidence >= CONFIDENCE_THRESHOLD:
            target_agent = new_agent
            if target_agent == "general":
                if session_id in agent_session_state: del agent_session_state[session_id]
            else:
                agent_session_state[session_id] = target_agent
            agent_changed = True
        else:
            target_agent = active_agent
    else:
        has_trigger, trigger_agent = _check_explicit_triggers(user_message)
        if has_trigger:
            # From general to specialized: switch directly without confirmation
            target_agent = trigger_agent
        else:
            routed_agent, confidence = _get_routing_decision(llm, PROMPT_ROUTE, user_message, _sanitize_agent)
            target_agent = routed_agent if confidence >= CONFIDENCE_THRESHOLD else "general"
        
        if target_agent != "general":
            # From general to specialized: switch directly
            agent_session_state[session_id] = target_agent
            agent_changed = True

    def wrap_response(agent_name: str, result) -> Dict[str, Any]:
        if isinstance(result, dict):
            return {
                "response": result.get("response") or result.get("output"),
                "structured": result.get("structured") or {"intent": agent_name},
                "agent": agent_name,
                "agent_changed": agent_changed
            }
        return {"response": str(result), "agent": agent_name, "agent_changed": agent_changed}

    try:
        res = None
        if target_agent == "lawyer":
            user_context["session_id"] = session_id 
            res = handle_lawyer_request(user_message, user_context)
        
        elif target_agent == "insurance":
            # Wichtig: Hier rufen wir deinen Insurance Agent auf
            res = run_insurance_agent(user_message, session_id, user_context)
            
        elif target_agent == "repair":
            res = run_repair_agent_with_memory(user_message, session_id, user_context)

        else:
            return wrap_response("chatbot", handle_general_request(user_message, user_name))

        # --- HANDOVER LOGIK START ---
        if isinstance(res, dict) and res.get("handover"):
            next_agent = res.get("handover")
            
            if next_agent in HANDOVER_MAP:
                log.info(f"Handover bestätigt: {target_agent} -> {next_agent}")
                
                # 1. Session-Status aktualisieren
                agent_session_state[session_id] = next_agent
                
                # 2. Den neuen Agenten mit einem speziellen Start-Signal triggern
                # Wir geben ihm den Kontext mit, damit er weiß, dass ein Schaden vorliegt
                start_trigger = f"SYSTEM_HANDOVER_FROM_{target_agent.upper()}"
                new_res = HANDOVER_MAP[next_agent](start_trigger, session_id, user_context)
                
                old_text = res.get('response', '')
                new_text = new_res.get('response', '') if isinstance(new_res, dict) else new_res
                
                # Kombinierte Antwort: Bestätigung vom alten + Begrüßung vom neuen Agenten
                return {
                    "response": f"{old_text}\n\n{new_text}",
                    "structured": {"intent": next_agent, "handover_complete": True},
                    "agent": next_agent,
                    "agent_changed": True
                }
        # --- HANDOVER LOGIK ENDE ---

        return wrap_response(target_agent, res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Entschuldigung, ein interner Fehler ist aufgetreten.", "agent": target_agent}