import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
import os
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
    JSON: {"agent": "..." }
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

state_storage = {}

def load_state(session_id: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    return state_storage.get(session_id, {
        "fields": {},
        "asked": {},
        "awaiting_submission": False,
        "awaiting_workshop_decision": False
    })

def save_state(session_id: str, state: Dict[str, Any]):
    state_storage[session_id] = state

def _get_routing_decision(text: str) -> str:
    """Fragt das LLM, welcher Agent zuständig sein könnte."""
    try:
        response = llm.invoke(PROMPT_ROUTE.format(user_message=text))
        data = _safe_json_loads(response.content)
        return data.get("agent", "general")
    except Exception:
        return "general"

def _keyword_override(decision: str, text: str) -> str:
    text = text.lower()
    if any(x in text for x in ["anwalt", "lawyer", "rechtsbeistand", "verklagen"]):
        return "lawyer"

    insurance_keywords = [
        "schaden", "schadensmeldung", "claim", "damage",
        "insurance", "versicher", "accident", "crash", "bump"
    ]
    if any(k in text for k in insurance_keywords):
        return "insurance"

    if decision == "general":
        repair_keywords = ["werkstatt", "termin", "reparatur", "reifen", "ölwechsel", "inspektion"]
        if any(k in text for k in repair_keywords):
            return "repair"
    return decision

def handle_general_request(user_message: str, user_name: str = None) -> Dict[str, Any]:
    if user_name:
        sys_msg = f"Du bist der persönliche Assistent von {user_name}. Antworte kurz und prägnant."
    else:
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
    
    log.info(f"Orchestrator: '{user_message}' | User: {user_name} | Session: {session_id}")

    if user_message.lower().strip() in ["stop", "abbruch", "ende", "reset", "neues thema", "exit"]:
        if session_id in agent_session_state:
            del agent_session_state[session_id]
        return {
            "response": "Gespräch zurückgesetzt. Ich bin wieder im allgemeinen Modus. Wie kann ich helfen?",
            "structured": {"intent": "reset"},
            "agent": "reset",
            "agent_changed": True
        }

    active_agent = agent_session_state.get(session_id)
    target_agent = "general"
    agent_changed = False
    decision = _get_routing_decision(user_message)
    decision_with_keywords = _keyword_override(decision, user_message)

    if active_agent:
        if decision == "general":
            target_agent = active_agent
        elif decision != active_agent:
            if decision_with_keywords != decision and decision_with_keywords != "general":
                 target_agent = decision_with_keywords
                 agent_session_state[session_id] = target_agent
                 agent_changed = True
            elif decision != "general":
                target_agent = decision
                agent_session_state[session_id] = target_agent
                agent_changed = True
            else:
                target_agent = active_agent
        else:
            target_agent = active_agent

    else:
        target_agent = decision_with_keywords
        if target_agent != "general":
            agent_session_state[session_id] = target_agent
            agent_changed = True

    def wrap_response(agent_name: str, result) -> Dict[str, Any]:
        if isinstance(result, dict):
            structured = result.get("structured") or {"intent": agent_name}
            resp = result.get("response") or result.get("output") or str(result)
            return {"response": resp, "structured": structured, "agent": agent_name, "agent_changed": agent_changed}
        return {"response": str(result), "structured": {"intent": agent_name}, "agent": agent_name, "agent_changed": agent_changed}

    try:
        state = load_state(session_id, user_context)
        if state.get("awaiting_workshop_decision") and target_agent == "insurance":
            if user_message.strip().lower() in ["ja", "yes", "jo", "okay", "ok"]:
                state["awaiting_workshop_decision"] = False
                save_state(session_id, state)

                agent_session_state[session_id] = "repair"

                claim_data = state.get("fields", {})
                res = run_repair_agent_with_memory(
                    f"Bitte starte einen Werkstattprozess für diesen Schadensfall:\n{json.dumps(claim_data)}",
                    session_id
                )
                return wrap_response("repair", res)

            elif user_message.strip().lower() in ["nein", "no"]:
                state["awaiting_workshop_decision"] = False
                save_state(session_id, state)
                reply = "Alles klar. Wenn du später einen Termin brauchst, sag einfach Bescheid."
                return wrap_response("insurance", reply)

        if target_agent == "lawyer":
            user_context["session_id"] = session_id 
            res = handle_lawyer_request(user_message, user_context)
            return wrap_response("lawyer", res)
        elif target_agent == "insurance":
            res = run_insurance_agent(user_message, session_id, user_context)
            return wrap_response("insurance", res)
        elif target_agent == "repair":
            res = run_repair_agent_with_memory(user_message, session_id)
            return wrap_response("repair", res)

        else:
            if session_id in agent_session_state:
                del agent_session_state[session_id]
            res = handle_general_request(user_message)
            return wrap_response("chatbot", res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Sorry, es gab einen internen Fehler.", "structured": {"error": str(e)}, "agent": target_agent}
