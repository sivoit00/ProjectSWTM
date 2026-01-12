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
from agents.tools.orchestrator_utils import _check_explicit_triggers, _safe_json_loads, _normalize_text, _get_full_routing_info, process_handover_signal

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini") 

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
agent_session_state = {}
pending_switch_state: Dict[str, Dict[str, Any]] = {}

ALLOWED_AGENTS = {"lawyer", "insurance", "repair", "general", "reset"}
CONFIDENCE_THRESHOLD = 0.7

HANDOVER_MAP = {
    "repair": lambda msg, sid, ctx: run_repair_agent_with_memory(msg, sid, ctx),
    "lawyer": lambda msg, sid, ctx: handle_lawyer_request(msg, sid, ctx),
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
        resp = llm.invoke([("system", "Du bist ein präziser Klassifizierer."), ("human", prompt)])
        decision = resp.content.strip().lower()

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
        pending_switch_state.pop(session_id, None)
        return {"response": "Gespräch zurückgesetzt. Wie kann ich helfen?", "agent": "reset", "agent_changed": True}

    # 2. Bestehende Switch-Bestätigung (Pending State)
    pending = pending_switch_state.get(session_id)
    if pending:
        decision = _llm_classify_switch_reply(user_message)
        if decision == "confirm":
            target_agent = pending.get("to_agent", "general")
            original_msg = pending.get("original_message") or user_message
            pending_switch_state.pop(session_id, None)

            if target_agent != "general":
                agent_session_state[session_id] = target_agent
            else:
                agent_session_state.pop(session_id, None)

            user_message = original_msg 
        elif decision == "decline":
            pending_switch_state.pop(session_id, None)
            active = agent_session_state.get(session_id) or "chatbot"
            return {"response": "Alles klar – ich bleibe im aktuellen Modus.", "agent": active, "agent_changed": False}
        else:
            return {"response": "Bitte bestätige kurz: Soll ich den Experten wechseln?", "agent": "orchestrator"}

    # 3. ROUTER FRAGEN (Template nutzen)
    routing_data = _get_full_routing_info(llm, PROMPT_ROUTE, user_message)
    target_agent = _sanitize_agent(routing_data.get("agent"))
    confidence = routing_data.get("confidence", 0.0)
    concierge_intro = routing_data.get("concierge_message", "")
    
    active_agent = agent_session_state.get(session_id)
    agent_changed = False

    # 4. Kurze Bestätigungen abfangen (Deine Logik)
    confirmations = {"ja", "gerne", "einverstanden", "nein", "ok", "okay", "machen wir", "top", "gut"}
    is_short_confirm = user_message.lower().strip().rstrip(".!?") in confirmations and len(user_message.split()) <= 2

    # 5. ENTSCHEIDUNG: Welcher Agent führt aus?
    if active_agent and is_short_confirm:
        target_agent = active_agent
    elif target_agent != "general" and target_agent != active_agent:
  
        if confidence >= CONFIDENCE_THRESHOLD:
            agent_session_state[session_id] = target_agent
            agent_changed = True
        else:
            target_agent = active_agent or "general"
    elif not active_agent:

        if confidence >= CONFIDENCE_THRESHOLD:
            agent_session_state[session_id] = target_agent
            agent_changed = True
        else:
            target_agent = "general"

    # 6. AGENTEN-AUFRUF
    try:
        if agent_changed:
            current_msg = (
                f"(Anweisung: Der Concierge hat bereits begrüßt. Überspringe deine "
                f"Einleitung/Empathie und starte direkt mit den Daten/Fragen.) "
                f"{user_message}"
            )
        else:
            current_msg = user_message

        if target_agent == "lawyer":
            user_context["session_id"] = session_id
            res = handle_lawyer_request(current_msg, user_context)
        elif target_agent == "insurance":
            res = run_insurance_agent(current_msg, session_id, user_context)
        elif target_agent == "repair":
            res = run_repair_agent_with_memory(current_msg, session_id, user_context)

        # 7. HANDOVER LOGIK (Deine Spezial-Logik für Reparatur -> Versicherung etc.)
        if isinstance(res, dict) and res.get("handover"):
            next_agent = res.get("handover")
            if next_agent in HANDOVER_MAP:
                agent_session_state[session_id] = next_agent
        
                start_trigger = f"SYSTEM_HANDOVER_FROM_{target_agent.upper()}"
                new_res = HANDOVER_MAP[next_agent](start_trigger, session_id, user_context)
        
                old_text = res.get('response', '')
                new_text = new_res.get('response', '') if isinstance(new_res, dict) else new_res
        
                return {
                    "response": f"{old_text}\n\n{new_text}",
                    "agent": next_agent,
                    "agent_changed": False  
                }

        # 8. ANTWORT WRAPPEN & CONCIERGE TEXT HINZUFÜGEN
        agent_text = res.get("response") if isinstance(res, dict) else str(res)

        welcome_key = f"{session_id}_welcomed"
        has_been_welcomed = agent_session_state.get(welcome_key, False)

        if agent_changed and concierge_intro and not has_been_welcomed:
            final_text = f"{concierge_intro}\n\n{agent_text}"
            agent_session_state[welcome_key] = True
        else:
            final_text = agent_text

        return {
            "response": final_text,
            "agent": target_agent,
            "agent_changed": agent_changed,
            "structured": res.get("structured") if isinstance(res, dict) else {}
        }

    except Exception as e:
        log.exception(f"Fehler im Agenten: {e}")
        return {"response": "Entschuldigung, ein Fehler ist aufgetreten.", "agent": "error"}