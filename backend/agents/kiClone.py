import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agents.lawyerAgent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent

from agents.repair_chat_agent import run_repair_agent_with_memory

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini")

CURRENT_ACTIVE_AGENT = None 

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
    # Per-message routing (stateless) — avoids sticky behavior where the first matched
    # agent handles all following user messages. The orchestrator decides each call.
    if user_context is None:
        user_context = {}

    log.info(f"Orchestrator Routing: '{user_message}' | User: {user_context.get('name')}")

    # quick stop/reset handling
    if user_message.lower().strip() in ["stop", "abbruch", "ende"]:
        return {"response": "Gespräch beendet.", "structured": {"intent": "reset"}}

    decision = _get_routing_decision(user_message)
    if decision == "reset":
        return {"response": "Okay.", "structured": {"intent": "reset"}}

    target_agent = decision or "general"

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
            # pass full user_context so agents can access token-extracted info (e.g. email)
            res = run_repair_agent_with_memory(user_message, session_id or "default", user_context)
            return wrap_response("repair", res)

        # default: general
        res = handle_general_request(user_message)
        return wrap_response("general", res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Entschuldigung, es gab einen internen Fehler bei der Verarbeitung.", "structured": {"intent": target_agent, "error": str(e)}}