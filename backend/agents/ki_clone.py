import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agents.lawyer_agent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent
from agents.repair_chat_agent import run_repair_agent_with_memory
from agents.session_manager import get_active_agent, set_active_agent, get_session_state, reset_session
from agents.intent_detector import detect_intent_from_message, should_switch_agent

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini") 

PROMPT_ROUTE = """
Du bist ein KI-Orchestrator. Entscheide, welcher Agent zuständig ist.
Agenten:
- "lawyer": Anwälte, Rechtsfragen, Unfälle, Bußgelder, Verträge.
- "insurance": Versicherung, Police, Schaden, Prämie, Deckung, Versicherungsstatus.
- "repair": Werkstatt-/Reparatur- und Serviceanfragen, Werkstattsuche, Termine, Empfehlungen.
- "general": Alles andere.
- "reset": Thema wechseln / Abbruch.

Format der Ausgabe: reines JSON, nur:
{{
    "agent": "<lawyer|insurance|repair|general|reset>"
}}

Analysen und Erklärungen sind verboten.

Nutzertext: "{user_message}"
"""

AGENT_DISPATCHER = {
    "lawyer": handle_lawyer_request,
    "insurance": run_insurance_agent,
    "repair": run_repair_agent_with_memory,
}

def _safe_json_loads(s: str) -> dict:
    try:
        s = s.replace("```json", "").replace("```", "").strip()
        return json.loads(s)
    except json.JSONDecodeError:
        return {}

def _get_routing_decision(text: str) -> str:
    try:
        response = llm.invoke(PROMPT_ROUTE.format(user_message=text))
        data = _safe_json_loads(response.content)
        return data.get("agent", "general")
    except Exception:
        return "general"

def handle_general_request(user_message: str) -> Dict[str, Any]:
    resp = llm.invoke(user_message)
    return {"response": resp.content, "structured": {"intent": "general"}}

def route_message(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Session-basiertes persistentes Routing.
    Der active_agent bleibt aktiv, bis ein Themenwechsel erkannt wird.
    """
    if user_context is None:
        user_context = {}

    # Session-ID aus Context holen (oder Default verwenden)
    session_id = user_context.get("session_id") or user_context.get("user_id") or "default"
    
    log.info(f"Orchestrator Routing: '{user_message}' | Session: {session_id} | User: {user_context.get('name')}")

    # Intent-Detection: Prüfe ob User ein neues Thema startet
    detected_intent = detect_intent_from_message(user_message)
    
    # Hole aktuellen aktiven Agent aus Session
    current_agent = get_active_agent(session_id)
    
    # Reset-Handling
    if detected_intent == "reset":
        reset_session(session_id)
        return {
            "response": "Okay, ich starte von vorne. Wie kann ich Ihnen helfen?",
            "structured": {"intent": "reset"},
            "agent": "chatbot",
            "agent_changed": True
        }
    
    # Prüfe ob Agent-Wechsel nötig ist
    if should_switch_agent(current_agent, detected_intent):
        if detected_intent:
            # Wechsel zu spezialisiertem Agent
            set_active_agent(session_id, detected_intent)
            target_agent = detected_intent
            agent_changed = True
            log.info(f"Session {session_id}: Themenwechsel erkannt → {target_agent}")
        else:
            # Kein Intent erkannt, bleibe bei current_agent
            target_agent = current_agent
            agent_changed = False
    else:
        # Kein Wechsel nötig
        # ABER: Wenn spezialisierter Agent aktiv ist und KEIN Intent mehr erkannt wird,
        # kehre zu Tom zurück (normale Konversation)
        if current_agent not in ["chatbot", "general"] and detected_intent is None:
            log.info(f"Session {session_id}: Kein spezieller Intent mehr → zurück zu Tom")
            set_active_agent(session_id, "chatbot")
            target_agent = "chatbot"
            agent_changed = True
        else:
            # Bleibe beim aktiven Agent
            target_agent = current_agent
            agent_changed = False
    
    log.info(f"Session {session_id}: Aktiver Agent = {target_agent} (Changed: {agent_changed})")

    def wrap_response(agent_name: str, result, changed: bool = False) -> Dict[str, Any]:
        # Normalize different agent return types to a standard dict
        if isinstance(result, dict):
            structured = result.get("structured") or {"intent": agent_name}
            resp = result.get("response") or result.get("output") or result.get("data") or str(result)
            return {
                "response": resp, 
                "structured": structured, 
                "agent": agent_name,
                "agent_changed": changed  # Für Timeline-Events
            }
        if isinstance(result, str):
            return {
                "response": result, 
                "structured": {"intent": agent_name}, 
                "agent": agent_name,
                "agent_changed": changed
            }
        return {
            "response": str(result), 
            "structured": {"intent": agent_name}, 
            "agent": agent_name,
            "agent_changed": changed
        }

    try:
        if target_agent == "lawyer":
            res = handle_lawyer_request(user_message, user_context)
            return wrap_response("lawyer", res, agent_changed)

        if target_agent == "insurance":
            user_id = user_context.get("user_id") or user_context.get("id")
            res = run_insurance_agent(user_message, user_id, user_context)
            return wrap_response("insurance", res, agent_changed)

        if target_agent == "repair":
            res = run_repair_agent_with_memory(user_message, session_id)
            return wrap_response("repair", res, agent_changed)

        # default: chatbot (Tom)
        if target_agent == "chatbot" or target_agent == "general":
            res = handle_general_request(user_message)
            return wrap_response("chatbot", res, agent_changed)
        
        # Fallback
        res = handle_general_request(user_message)
        return wrap_response("chatbot", res, agent_changed)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {
            "response": "Entschuldigung, es gab einen internen Fehler bei der Verarbeitung.",
            "structured": {"intent": target_agent, "error": str(e)},
            "agent": target_agent,
            "agent_changed": False
        }