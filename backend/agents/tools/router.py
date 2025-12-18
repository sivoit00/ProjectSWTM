import logging
from typing import Any
from agents.tools.orchestrator_utils import _safe_json_loads, _check_explicit_triggers

log = logging.getLogger(__name__)

def _get_routing_decision(llm, prompt_template, text, sanitize_func) -> tuple[str, float]:
    """Fragt das LLM, welcher Agent zuständig sein könnte."""
    try:
        response = llm.invoke(prompt_template.format(user_message=text))
        data = _safe_json_loads(response.content)
        agent = sanitize_func(data.get("agent", "general"))
        confidence = _clamp_confidence(data.get("confidence", 0.5))
        return (agent, confidence)
    except Exception:
        return ("general", 0.0)

def _should_switch_agent(llm, current_agent, user_message, sanitize_func) -> tuple[bool, str, float]:
    """Entscheidet kontext-bewusst ob Agent gewechselt werden soll."""
    current_agent = sanitize_func(current_agent)

    has_trigger, trigger_agent = _check_explicit_triggers(user_message)
    if has_trigger and trigger_agent != current_agent:
        return (True, trigger_agent, 0.95)
    
    context_prompt = f"""
You are an intelligent agent router. Analyze if the user wants to switch to a different agent.
Current Active Agent: {current_agent}
User Message: {user_message}
Available Agents: lawyer, repair, insurance, general
Return ONLY JSON: {{"should_switch": boolean, "target_agent": "...", "confidence": 0.0-1.0, "reason": "..."}}
"""
    try:
        response = llm.invoke(context_prompt)
        result = _safe_json_loads(response.content)
        
        should_switch = bool(result.get("should_switch", False))
        target_agent = sanitize_func(result.get("target_agent", "general"))
        confidence = _clamp_confidence(result.get("confidence", 0.5))
        
        log.info(f"Agent Switch: {should_switch}, Target: {target_agent}")
        return (should_switch, target_agent, confidence)
    except Exception as e:
        log.error(f"Error in agent switch decision: {e}")
        return (False, current_agent, 0.0)
    
def _clamp_confidence(value: Any, default: float = 0.0) -> float:
    try:
        c = float(value)
    except (TypeError, ValueError):
        return default
    if c < 0.0:
        return 0.0
    if c > 1.0:
        return 1.0
    return c