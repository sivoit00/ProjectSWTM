import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agents.lawyer_agent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent
from agents.repair_chat_agent import run_repair_agent_with_memory, is_session_active

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini")

# Track active agent per session to enable fluid multi-turn conversations
ACTIVE_AGENT_BY_SESSION: dict[str, str] = {}

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

def _is_followup_answer(text: str) -> bool:
    """Detects short follow-up messages like 'ja', 'nein', '1', 'ok'."""
    t = (text or "").strip().lower()
    if not t:
        return False
    short_yes_no = {"ja", "nein", "j", "n", "yes", "no", "ok", "okay"}
    numerics = {"1", "2", "3"}
    return t in short_yes_no or t in numerics or len(t) <= 6

def _wants_switch(text: str) -> bool:
    """Detects intent to switch topic/agent, including English phrases."""
    t = (text or "").lower()
    switch_tokens = [
        # generic
        "wechsel", "wechseln", "anderes thema", "neues thema", "reset",
        "agent wechseln", "wechsel zum",
        # German agent intents
        "anwalt", "rechtsanwalt", "jurist", "juristische hilfe",
        "versicherung", "versicherungsagent", "versicherungsfall",
        "werkstatt", "reparaturagent",
        # English agent intents
        "lawyer", "attorney", "legal", "legal help",
        "insurance", "insurer",
        "repair", "workshop",
        # common command patterns
        "finde einen anwalt", "anwalt finden", "find a lawyer", "need a lawyer",
        "brauche versicherung", "insurance claim", "need insurance"
    ]
    return any(tok in t for tok in switch_tokens)

def handle_general_request(user_message: str) -> Dict[str, Any]:
    resp = llm.invoke(user_message)
    return {"response": resp.content, "structured": {"intent": "general"}}

def route_message(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    # Stateful routing — keeps active agent per session and supports follow-ups.
    if user_context is None:
        user_context = {}

    log.info(f"Orchestrator Routing: '{user_message}' | User: {user_context.get('name')}")

    # quick stop/reset handling
    if user_message.lower().strip() in ["stop", "abbruch", "ende"]:
        return {"response": "Gespräch beendet.", "structured": {"intent": "reset"}}

    # derive session_id for state
    session_id = (
        user_context.get("session_id")
        or user_context.get("email")
        or user_context.get("user_email")
        or user_context.get("user_id")
        or user_context.get("id")
        or "default"
    )

    # keep repair agent active when its appointment workflow is ongoing
    try:
        if is_session_active(session_id):
            ACTIVE_AGENT_BY_SESSION[session_id] = "repair"
    except Exception:
        pass

    active_agent = ACTIVE_AGENT_BY_SESSION.get(session_id)

    # Prefer staying with the active agent unless user explicitly wants to switch
    if active_agent and not _wants_switch(user_message):
        target_agent = active_agent
    else:
        decision = _get_routing_decision(user_message)
        if decision == "reset":
            ACTIVE_AGENT_BY_SESSION.pop(session_id, None)
            return {"response": "Okay.", "structured": {"intent": "reset"}}
        target_agent = decision or active_agent or "general"

    def wrap_response(agent_name: str, result) -> Dict[str, Any]:
        # Normalize different agent return types to a standard dict
        if isinstance(result, dict):
            structured = result.get("structured") or {"intent": agent_name}
            resp = result.get("response") or result.get("output") or result.get("data") or str(result)
            return {"response": resp, "structured": structured}
        if isinstance(result, str):
            return {"response": result, "structured": {"intent": agent_name}}
        return {"response": str(result), "structured": {"intent": agent_name}}

    try:
        if target_agent == "lawyer":
            res = handle_lawyer_request(user_message, user_context)
            ACTIVE_AGENT_BY_SESSION[session_id] = "lawyer"
            return wrap_response("lawyer", res)

        if target_agent == "insurance":
            user_id = None
            if user_context:
                user_id = user_context.get("user_id") or user_context.get("id")
            res = run_insurance_agent(user_message, user_id, user_context)
            ACTIVE_AGENT_BY_SESSION[session_id] = "insurance"
            return wrap_response("insurance", res)

        if target_agent == "repair":
            res = run_repair_agent_with_memory(user_message, session_id=session_id, user_context=user_context)
            ACTIVE_AGENT_BY_SESSION[session_id] = "repair"
            return wrap_response("repair", res)

        # default: general
        res = handle_general_request(user_message)
        ACTIVE_AGENT_BY_SESSION[session_id] = "general"
        return wrap_response("general", res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Entschuldigung, es gab einen internen Fehler bei der Verarbeitung.", "structured": {"intent": target_agent, "error": str(e)}}