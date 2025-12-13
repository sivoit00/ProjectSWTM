import os
import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from services.insurance_utils import get_or_create_memory, save_state, load_state
from services.insurance_service import get_user_context

log = logging.getLogger(__name__)

PROMPT_TEMPLATE_PATH = "templates/insurance_agent.md"

def _load_prompt() -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def run_insurance_agent(
    user_input: str,
    session_id: str = "default",
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"response": "API key missing", "structured": {}, "agent": "insurance"}

    llm = ChatOpenAI(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"),
        temperature=0
    )

    memory = get_or_create_memory(session_id)

    if not user_context or not user_context.get("customer_id"):
        identifier = None
        if user_context:
            identifier = (
                user_context.get("customer_id")
                or user_context.get("email")
                or user_context.get("user_id")
            )
        db_context = get_user_context(identifier or session_id)
        if db_context:
            if user_context:
                user_context.update(db_context)
            else:
                user_context = db_context

    state = load_state(session_id, user_context)

    chat_history_list = memory.load_memory_variables({}).get("chat_history", [])
    chat_history_text = "\n".join([f"{m.type}: {m.content}" for m in chat_history_list])

    prompt_template = _load_prompt()
    prompt_text = (
        prompt_template
        .replace("{chat_history}", chat_history_text)
        .replace("{user_input}", user_input)
    )

    try:
        res = llm.invoke([
            SystemMessage(content=prompt_text),
            HumanMessage(content=user_input)
        ])

        import json
        content = res.content.strip()

        start = content.find("{")
        end = content.rfind("}") + 1
        json_data = {}

        if start != -1 and end != -1:
            try:
                json_data = json.loads(content[start:end])
            except Exception as e:
                log.warning(f"JSON parsing failed: {e}")

        handover = None
        claim_data = None

        if isinstance(json_data, dict) and json_data.get("handover") == "repair":
            handover = "repair"
            claim_data = {
                "customer_id": json_data.get("customer_id"),
                "vehicle": json_data.get("vehicle"),
                "description": json_data.get("description"),
                "damage_date": json_data.get("damage_date"),
                "damage_location": json_data.get("damage_location"),
                "estimated_damage": json_data.get("estimated_damage"),
            }

        memory.save_context({"user_input": user_input}, {"response": content})
        save_state(session_id, state)

        return_data = {
            "response": content,
            "structured": json_data,
            "agent": "insurance"
        }

        if handover == "repair":
            return_data["handover"] = "repair"
            return_data["claim_data"] = claim_data

        return return_data

    except Exception as e:
        log.exception(f"Error in insurance agent: {e}")
        return {
            "response": "Sorry, es gab einen internen Fehler.",
            "structured": {},
            "agent": "insurance"
        }
