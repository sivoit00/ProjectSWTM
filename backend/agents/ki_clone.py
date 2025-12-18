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

ALLOWED_AGENTS = {"lawyer", "insurance", "repair", "general", "reset"}
CONFIDENCE_THRESHOLD = 0.7

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
    JSON: {{"agent": "...", "confidence": 0.0 }}
    User: {user_message}
    """

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

def _sanitize_agent(agent: Any, default: str = "general") -> str:
    if not isinstance(agent, str):
        return default
    agent = agent.strip().lower()
    return agent if agent in ALLOWED_AGENTS else default

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

    if active_agent:
        should_switch, new_agent, confidence = _should_switch_agent(
        llm, active_agent, user_message, _sanitize_agent
        )
        
        if should_switch and confidence >= CONFIDENCE_THRESHOLD:
            # Hohe Confidence → Wechsel durchführen
            target_agent = new_agent
            if target_agent != "general":
                agent_session_state[session_id] = target_agent
            else:
                # Wechsel zu general = Session beenden
                if session_id in agent_session_state:
                    del agent_session_state[session_id]
            agent_changed = True
            log.info(f"Agent switch: {active_agent} → {target_agent} (confidence: {confidence})")
        else:
            # Kein Wechsel, bleibe beim aktuellen Agenten
            target_agent = active_agent
            log.info(f"Staying with current agent: {active_agent} (confidence: {confidence})")
    else:
        # Keine aktive Session → Neue Intent-Erkennung
        log.info(f"No active session for {session_id}, detecting intent...")
        
        # Prüfe zuerst explizite Trigger
        has_trigger, trigger_agent = _check_explicit_triggers(user_message)
        
        if has_trigger:
            target_agent = trigger_agent
            log.info(f"Explicit trigger detected: {target_agent}")
        else:
            # Fallback auf LLM-basierte Entscheidung
            routed_agent, confidence = _get_routing_decision(
                llm, PROMPT_ROUTE, user_message, _sanitize_agent
            )
            log.info(f"LLM routing decision: {routed_agent} (confidence: {confidence})")
            if routed_agent != "general" and confidence >= CONFIDENCE_THRESHOLD:
                target_agent = routed_agent
            else:
                target_agent = "general"
                log.info("LLM confidence too low -> staying in general")
        
        if target_agent != "general":
            agent_session_state[session_id] = target_agent
            agent_changed = True
            log.info(f"✅ New session started with agent: {target_agent}, agent_changed=True")
        else:
            log.info(f"Starting general chatbot, agent_changed=False")

    def wrap_response(agent_name: str, result) -> Dict[str, Any]:
        if isinstance(result, dict):
            structured = result.get("structured") or {"intent": agent_name}
            resp = result.get("response") or result.get("output") or str(result)
            return {"response": resp, "structured": structured, "agent": agent_name, "agent_changed": agent_changed}
        return {"response": str(result), "structured": {"intent": agent_name}, "agent": agent_name, "agent_changed": agent_changed}

    try:

        if target_agent == "lawyer":
            user_context["session_id"] = session_id 
            res = handle_lawyer_request(user_message, user_context)
            return wrap_response("lawyer", res)
        elif target_agent == "insurance":
            res = run_insurance_agent(user_message, session_id, user_context)
            
            user_said_yes = re.search(r"\b(ja|gerne|einverstanden|mach das)\b", user_message.lower())
            
            if isinstance(res, dict) and (res.get("handover") == "repair" or (user_said_yes and active_agent == "insurance")):
                log.info(f"!!! Triggering Instant Handover to Repair !!!")
    
                agent_session_state[session_id] = "repair"
                repair_res = run_repair_agent_with_memory("START_REPAIR_FLOW", session_id, user_context)
    
                insurance_text = res.get('response', res) if isinstance(res, dict) else res
                repair_text = repair_res.get('response', repair_res) if isinstance(repair_res, dict) else repair_res
    
                combined_response = f"{insurance_text}\n\n{repair_text}"
    
                return {
                    "response": combined_response,
                    "structured": {"intent": "repair", "handover_complete": True},
                    "agent": "repair",
                    "agent_changed": True
                }

            return wrap_response("insurance", res)
        
        elif target_agent == "repair":
            res = run_repair_agent_with_memory(user_message, session_id, user_context)
            return wrap_response("repair", res)

        else:
            if session_id in agent_session_state:
                del agent_session_state[session_id]
            res = handle_general_request(user_message)
            return wrap_response("chatbot", res)

    except Exception as e:
        log.exception(f"Fehler im Agenten '{target_agent}': {e}")
        return {"response": "Sorry, es gab einen internen Fehler.", "structured": {"error": str(e)}, "agent": target_agent}
