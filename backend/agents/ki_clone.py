import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
import os
from agents.lawyer_agent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent
from agents.repair_chat_agent import run_repair_agent_with_memory, is_session_active

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-5")

CURRENT_ACTIVE_AGENT = None 

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

def _load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPT_ROUTE = _load_template("orchestrator_route.md")

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
        log.debug(f"Raw routing LLM response: {response.content}")
        data = _safe_json_loads(response.content)
        return data.get("agent", "general")
    except Exception:
        return "general"

REPAIR_KEYWORDS = [
    "werkstatt", "termin", "service", "reparatur", "reifen", "inspektion", "ölwechsel", "wartung", "appointment", "repair", "workshop"
]

def _keyword_override(decision: str, text: str) -> str:
    if decision == "general":
        lowered = text.lower()
        for kw in REPAIR_KEYWORDS:
            if kw in lowered:
                log.debug(f"Keyword override triggered by '{kw}' -> 'repair'")
                return "repair"
    return decision

def handle_general_request(user_message: str) -> Dict[str, Any]:
    resp = llm.invoke(user_message)
    return {"response": resp.content, "structured": {"intent": "general"}}

def route_message(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    # Per-message routing (stateless) — avoids sticky behavior where the first matched
    # agent handles all following user messages. The orchestrator decides each call.
    if user_context is None:
        user_context = {}

    log.info(f"Orchestrator Routing: '{user_message}' | User: {user_context.get('name')}")

    # quick stop/reset handling
    if user_message.lower().strip() in ["stop", "abbruch", "ende"]:
        return {"response": "Gespräch beendet.", "structured": {"intent": "reset"}, "agent": "reset"}

    decision = _get_routing_decision(user_message)
    decision = _keyword_override(decision, user_message)

    # If we are in the middle of a repair workflow (session state not done), keep routing to repair
    session_id = user_context.get("session_id") or user_context.get("session") or "default"
    # Explicit switch to lawyer/insurance should override sticky repair
    lowered = user_message.lower()
    wants_lawyer = any(tok in lowered for tok in ["anwalt", "lawyer", "jurist", "rechtshilfe"]) 
    wants_insurance = any(tok in lowered for tok in ["versicherung", "insurance", "claim", "police"]) 

    if wants_lawyer:
        decision = "lawyer"
    elif wants_insurance:
        decision = "insurance"
    elif decision == "general" and is_session_active(session_id):
        log.debug(f"Sticky repair override: active session '{session_id}', forcing agent 'repair'.")
        decision = "repair"
    if decision == "reset":
        return {"response": "Okay.", "structured": {"intent": "reset"}, "agent": "reset"}

    target_agent = decision or "general"

    def wrap_response(agent_name: str, result) -> Dict[str, Any]:
        # Normalize different agent return types to a standard dict
        if isinstance(result, dict):
            structured = result.get("structured") or {"intent": agent_name}
            resp = result.get("response") or result.get("output") or result.get("data") or str(result)
            return {"response": resp, "structured": structured, "agent": agent_name}
        if isinstance(result, str):
            return {"response": result, "structured": {"intent": agent_name}, "agent": agent_name}
        return {"response": str(result), "structured": {"intent": agent_name}, "agent": agent_name}

    try:
        if target_agent == "lawyer":
            res = handle_lawyer_request(user_message, user_context)
            return wrap_response("lawyer", res)

        if target_agent == "insurance":
            user_id = None
            if user_context:
                user_id = user_context.get("user_id") or user_context.get("id")
            res = run_insurance_agent(user_message, user_id, user_context)
            return wrap_response("insurance", res)

        if target_agent == "repair":
            session_id = None
            if user_context:
                session_id = user_context.get("session_id") or user_context.get("session")
            res = run_repair_agent_with_memory(user_message, session_id or "default")
            return wrap_response("repair", res)

        # default: general
        res = handle_general_request(user_message)
        return wrap_response("general", res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Entschuldigung, es gab einen internen Fehler bei der Verarbeitung.", "structured": {"intent": target_agent, "error": str(e)}, "agent": target_agent}