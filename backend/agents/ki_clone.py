import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
import os
import re
from agents.lawyer_agent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent
from agents.repair_chat_agent import run_repair_agent_with_memory 

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini") 

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

agent_session_state = {}

def _load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        return "{user_message}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

try:
    PROMPT_ROUTE = _load_template("orchestrator_route.md")
except:
    PROMPT_ROUTE = """
    Classify intent: lawyer, insurance, repair, general.
    JSON: {"agent": "..."}
    User: {user_message}
    """

def _safe_json_loads(s: str) -> dict:
    try:
        s = s.replace("```json", "").replace("```", "").strip()
        start = s.find("{")
        end = s.rfind("}") + 1
        if start != -1 and end != -1:
            s = s[start:end]
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

def _keyword_override(decision: str, text: str) -> str:
    """Zwingt Entscheidung bei sehr eindeutigen Keywords"""
    text = text.lower()
    
    if any(x in text for x in ["anwalt", "lawyer", "rechtsbeistand", "verklagen"]):
        return "lawyer"
        
    if decision == "general":
        repair_keywords = ["werkstatt", "termin", "reparatur", "reifen", "ölwechsel", "inspektion"]
        if any(k in text for k in repair_keywords):
            return "repair"
            
    return decision

def handle_general_request(user_message: str) -> Dict[str, Any]:
    sys_msg = "Du bist ein hilfreicher Assistent. Antworte kurz und prägnant."
    messages = [("system", sys_msg), ("human", user_message)]
    resp = llm.invoke(messages)
    return {"response": resp.content, "structured": {"intent": "general"}}

def route_message(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    if user_context is None:
        user_context = {}

    user_email = user_context.get("email")
    session_id = user_context.get("session_id") or user_email or "default_session"
    
    user_name = user_context.get("name", "User")
    log.info(f"Orchestrator Routing: '{user_message}' | User: {user_name} | Session: {session_id}")

    if user_message.lower().strip() in ["stop", "abbruch", "ende", "reset", "neues thema"]:
        if session_id in agent_session_state:
            del agent_session_state[session_id]
        return {"response": "Gespräch zurückgesetzt. Wie kann ich helfen?", "structured": {"intent": "reset"}, "agent": "reset"}

    decision = _get_routing_decision(user_message)
    decision = _keyword_override(decision, user_message)

    active_agent = agent_session_state.get(session_id)

    if active_agent and decision == "general":
        log.info(f"Sticky Session: Bleibe bei Agent '{active_agent}'")
        target_agent = active_agent
    else:
        if decision != "general":
            log.info(f"Agent Wechsel/Start: {active_agent} -> {decision}")
            agent_session_state[session_id] = decision
            target_agent = decision
        else:
            target_agent = "general"

    
    def wrap_response(agent_name: str, result) -> Dict[str, Any]:
        if isinstance(result, dict):
            structured = result.get("structured") or {"intent": agent_name}
            resp = result.get("response") or result.get("output") or str(result)
            return {"response": resp, "structured": structured, "agent": agent_name}
        return {"response": str(result), "structured": {"intent": agent_name}, "agent": agent_name}

    try:
        if target_agent == "lawyer":
            user_context["session_id"] = session_id 
            
            res = handle_lawyer_request(user_message, user_context)
            return wrap_response("lawyer", res)

        elif target_agent == "insurance":
            user_id = user_context.get("user_id") or "default_id"
            res = run_insurance_agent(user_message, user_id, user_context)
            return wrap_response("insurance", res)

        elif target_agent == "repair":
            res = run_repair_agent_with_memory(user_message, session_id)
            return wrap_response("repair", res)

        else: # General
            res = handle_general_request(user_message)
            return wrap_response("general", res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Sorry, interner Fehler.", "structured": {"error": str(e)}, "agent": target_agent}