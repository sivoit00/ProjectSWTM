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

def _load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        return "{user_message}"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

try:
    PROMPT_ROUTE = _load_template("orchestrator_route.md")
except Exception:
    PROMPT_ROUTE = """
    Classify intent: lawyer, insurance, repair, general.
    JSON: {{"agent": "...", "confidence": 0.0 }}
    User: {user_message}
    """


def _switch_question(from_agent: str, to_agent: str) -> str:
    return (
        f"Ich kann dich zum Agent '{to_agent}' weiterleiten (aktuell: '{from_agent}'). "
        "Möchtest du wechseln?"
    )


def _llm_classify_switch_reply(user_reply: str) -> str:
    """Classify a reply to a switch-confirmation question.

    Returns: 'confirm' | 'decline' | 'unknown'
    """
    prompt = f"""
You are a strict classifier.
Decide whether the user's reply confirms switching agents, declines switching, or is unrelated/unclear.
Return ONLY JSON: {{"decision": "confirm"|"decline"|"unknown", "confidence": 0.0-1.0}}

User reply: {user_reply}
"""
    try:
        resp = llm.invoke(prompt)
        data = _safe_json_loads(getattr(resp, "content", str(resp)))
        decision = str(data.get("decision", "unknown")).strip().lower()
        confidence = float(data.get("confidence", 0.0) or 0.0)
        if confidence < 0.7:
            return "unknown"
        if decision in {"confirm", "decline"}:
            return decision
        return "unknown"
    except Exception:
        return "unknown"

state_storage = {}

def load_state(session_id: str) -> Dict[str, Any]:
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
        if session_id in pending_switch_state:
            del pending_switch_state[session_id]
        return {
            "response": "Gespräch zurückgesetzt. Ich bin wieder im allgemeinen Modus. Wie kann ich helfen?",
            "structured": {"intent": "reset"},
            "agent": "reset",
            "agent_changed": True
        }

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

    if active_agent:
        should_switch, new_agent, confidence = _should_switch_agent(
        llm, active_agent, user_message, _sanitize_agent
        )
        
        if should_switch and confidence >= CONFIDENCE_THRESHOLD:
            # Ask for confirmation instead of switching immediately
            pending_switch_state[session_id] = {
                "from_agent": active_agent,
                "to_agent": new_agent,
                "confidence": confidence,
                "original_message": user_message,
            }
            return {
                "response": _switch_question(active_agent, new_agent),
                "structured": {"intent": active_agent, "awaiting_switch_confirmation": True},
                "agent": active_agent,
                "agent_changed": False,
            }
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
            # From general to specialized: switch directly without confirmation
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
            # From general to specialized: switch directly
            agent_session_state[session_id] = target_agent
            agent_changed = True
            log.info(f"✅ New session started with agent: {target_agent}, agent_changed=True")
        else:
            log.info("Starting general chatbot, agent_changed=False")

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
            
            if isinstance(res, dict) and (res.get("handover") == "repair"):
                log.info("!!! Triggering Instant Handover to Repair !!!")
    
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
