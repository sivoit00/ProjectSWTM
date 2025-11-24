import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agents.lawyerAgent import handle_lawyer_request

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini")

CURRENT_ACTIVE_AGENT = None 

PROMPT_ROUTE = """
Du bist ein KI-Orchestrator. Entscheide, welcher Agent zuständig ist.
Agenten:
- "lawyer": Anwälte, Rechtsfragen, Unfälle, Bußgelder.
- "general": Alles andere.
- "reset": Thema wechseln / Abbruch.

Format: JSON {{ "agent": "..." }}
Nutzertext: "{user_message}"
"""

AGENT_DISPATCHER = {
    "lawyer": handle_lawyer_request,
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
    global CURRENT_ACTIVE_AGENT
    
    if user_context is None:
        user_context = {}

    log.info(f"Orchestrator Routing: '{user_message}' | User: {user_context.get('name')}")

    target_agent = "general"

    if CURRENT_ACTIVE_AGENT:
        if user_message.lower() in ["stop", "abbruch", "ende"]:
            CURRENT_ACTIVE_AGENT = None
            return {"response": "Gespräch beendet.", "structured": {"intent": "reset"}}
        target_agent = CURRENT_ACTIVE_AGENT
    else:
        decision = _get_routing_decision(user_message)
        if decision == "reset":
            CURRENT_ACTIVE_AGENT = None
            return {"response": "Okay.", "structured": {"intent": "reset"}}
        target_agent = decision

    try:
        if target_agent == "lawyer":
            CURRENT_ACTIVE_AGENT = "lawyer"
            return handle_lawyer_request(user_message, user_context)
        
        else:
            CURRENT_ACTIVE_AGENT = None
            return handle_general_request(user_message)
            
    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {
            "response": "Entschuldigung, es gab einen internen Fehler bei der Verarbeitung.", 
            "structured": {"intent": target_agent, "error": str(e)}
        }