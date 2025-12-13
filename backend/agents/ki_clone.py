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

def _check_explicit_triggers(text: str) -> tuple[bool, str]:
    """Prüft ob User explizit einen Agenten-Wechsel wünscht."""
    text_lower = text.lower()
    
    # Explizite Wechsel-Trigger (hohe Priorität)
    lawyer_triggers = [
        "ich brauche einen anwalt",
        "ich möchte rechtliche",
        "hilf mir rechtlich",
        "ich brauche rechtsberatung",
        "rechtshilfe",
        "ich möchte einen anwalt"
    ]
    
    repair_triggers = [
        "ich brauche einen werkstatttermin",
        "ich möchte einen termin",
        "termin bei einer werkstatt",
        "werkstatt buchen",
        "ich brauche eine werkstatt",
        "hilf mir mit werkstatt"
    ]
    
    insurance_triggers = [
        "ich möchte einen schaden melden",
        "schadensmeldung machen",
        "hilf mir mit versicherung",
        "ich brauche versicherungshilfe"
    ]
    
    for trigger in lawyer_triggers:
        if trigger in text_lower:
            return (True, "lawyer")
    
    for trigger in repair_triggers:
        if trigger in text_lower:
            return (True, "repair")
    
    for trigger in insurance_triggers:
        if trigger in text_lower:
            return (True, "insurance")
    
    return (False, "general")

def _should_switch_agent(current_agent: str, user_message: str) -> tuple[bool, str, float]:
    """
    Entscheidet kontext-bewusst ob Agent gewechselt werden soll.
    
    Returns: (should_switch, target_agent, confidence)
    """
    # 1. Explizite Trigger haben höchste Priorität
    has_trigger, trigger_agent = _check_explicit_triggers(user_message)
    if has_trigger and trigger_agent != current_agent:
        return (True, trigger_agent, 0.95)
    
    # 2. LLM mit Kontext-Awareness
    context_prompt = f"""
You are an intelligent agent router. Analyze if the user wants to switch to a different agent.

Current Active Agent: {current_agent}
User Message: {user_message}

Available Agents:
- lawyer: Legal advice, accident support, legal questions
- repair: Workshop appointments, car repairs, maintenance
- insurance: Insurance claims, damage reports, insurance questions
- general: General conversation, greetings, other topics

Rules:
1. STAY with current agent if user is just MENTIONING another topic in context
2. SWITCH only if user EXPLICITLY wants help with a NEW topic
3. Examples:
   - "Ich muss noch mit Versicherung sprechen" (Lawyer context) → STAY (just mentioning)
   - "Hilf mir mit meiner Versicherung" → SWITCH to insurance (explicit request)
   - "Die Werkstatt hat gesagt..." (Insurance context) → STAY (just reporting)
   - "Ich brauche einen Werkstatttermin" → SWITCH to repair (explicit request)

Return ONLY valid JSON:
{{"should_switch": boolean, "target_agent": "lawyer|repair|insurance|general", "confidence": 0.0-1.0, "reason": "short explanation"}}
"""
    
    try:
        response = llm.invoke(context_prompt)
        result = _safe_json_loads(response.content)
        
        should_switch = result.get("should_switch", False)
        target_agent = result.get("target_agent", "general")
        confidence = result.get("confidence", 0.5)
        
        log.info(f"Agent Switch Decision: switch={should_switch}, target={target_agent}, confidence={confidence}, reason={result.get('reason', 'N/A')}")
        
        return (should_switch, target_agent, confidence)
    except Exception as e:
        log.error(f"Error in agent switch decision: {e}")
        return (False, current_agent, 0.0)

def _get_routing_decision(text: str) -> str:
    """Fragt das LLM, welcher Agent zuständig sein könnte (für neue Sessions)."""
    try:
        response = llm.invoke(PROMPT_ROUTE.format(user_message=text))
        data = _safe_json_loads(response.content)
        return data.get("agent", "general")
    except Exception:
        return "general"

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
        # Es gibt bereits einen aktiven Agenten
        # Prüfe kontext-bewusst ob gewechselt werden soll
        should_switch, new_agent, confidence = _should_switch_agent(active_agent, user_message)
        
        if should_switch and confidence > 0.7:
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
            target_agent = _get_routing_decision(user_message)
            log.info(f"LLM routing decision: {target_agent}")
        
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

            # Prüfen, ob Insurance-Agent Handover möchte
            if isinstance(res, dict) and res.get("handover") == "repair":
                # Daten speichern für den Repair-Agenten
                agent_session_state[session_id] = "repair"
        
                # claim_data in user_context speichern
                if "claim_data" in res:
                    user_context["claim_data"] = res["claim_data"]

                return {
                    "response": res.get("response", ""),
                    "structured": {"intent": "insurance"},
                    "agent": "insurance",
                    "agent_changed": True  # sehr wichtig!
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
