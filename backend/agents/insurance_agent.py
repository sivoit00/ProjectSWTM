import os
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from services.insurance_utils import get_or_create_memory, save_state, load_state
from services.insurance_service import get_user_context, get_claim_status, submit_claim, calculate_premium, get_policy_details
from langchain_core.messages import AIMessage

log = logging.getLogger(__name__)

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
PROMPT_TEMPLATE_PATH = os.path.join(templates_dir, "insurance_classifier.md")

@tool
def check_policy_details(customer_id: str) -> str:
    """
    Retrieves the policy details (coverage, status) for a given customer ID from the database.
    Input MUST be a customer ID (string).
    """
    if not customer_id:
        return "ERROR: Customer ID is missing. Please ask the user for their customer ID first."

    details = get_policy_details(customer_id)
    return json.dumps(details, indent=2)


@tool
def calculate_estimated_premium(vehicle_data: str) -> str:
    """
    Calculates the estimated annual premium for a vehicle based on its data (make, model, year, value).
    Input MUST be a JSON string containing vehicle information (e.g., '{"year": 2022, "value": 30000}').
    """
    if not vehicle_data:
        return "ERROR: Vehicle data is missing. Please ask the user for details like vehicle year, value, or model."

    result = calculate_premium(vehicle_data)
    return json.dumps(result, indent=2)


@tool
def get_claim_status_check(claim_id: str) -> str:
    """
    Checks the current processing status of a claim using the claim ID.
    Input MUST be the specific claim ID (string).
    """
    if not claim_id:
        return "ERROR: Claim ID is missing. Please ask the user for the claim ID."

    status = get_claim_status(claim_id)
    return json.dumps(status, indent=2)


def _load_prompt() -> str:
    with open(PROMPT_TEMPLATE_PATH, "r", encoding="utf-8") as f:
        return f.read()

def _build_agent_step(response_text: str, agent_name: str = "insurance") -> Dict[str, Any]:
    now = datetime.utcnow().isoformat()
    return {
        "task": "agent_session",
        "timestamp": now,
        "status": "working",
        "description": f"{agent_name.capitalize()} Agent",
        "agent": agent_name,
        "event_type": "agent_session",
        "details": response_text,
        "messageId": None,
        "sessionId": f"sess-{int(datetime.utcnow().timestamp() * 1000)}"
    }

def run_insurance_agent(
    user_input: str,
    session_id: str = "default",
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"response": "API key missing", "structured": {}, "agent": "insurance", "agent_steps": []}

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

    prompt_template = _load_prompt()

    user_context_str = json.dumps(user_context, indent=2) if user_context else "Kein bekannter Benutzerkontext."
    context_prefix = f"## Aktueller Benutzerkontext\n{user_context_str}\n\n"

    system_content = context_prefix + prompt_template

    messages = [SystemMessage(content=system_content)] + chat_history_list + [HumanMessage(content=user_input)]

    tools = [check_policy_details, calculate_estimated_premium, get_claim_status_check]

    agent = create_openai_tools_agent(llm, tools, messages)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    try:
        res_output = agent_executor.invoke({
            "input": user_input,
        })

        content = res_output.get("output", "").strip()

        json_data = {}
        start = content.find("{")
        end = content.rfind("}") + 1

        if start != -1 and end != -1:
            try:
                potential_json = content[start:end]
                potential_json = potential_json.replace('Orchestrator-JSON mit den gesammelten Daten:\n', '').strip()
                json_data = json.loads(potential_json)
            except Exception as e:
                log.warning(f"JSON parsing failed: {e}")

        handover = None
        claim_data = None

        if isinstance(json_data, dict) and json_data.get("handover") == "repair":
            handover = "repair"
            claim_data_raw = {k: json_data.get(k) for k in ["customer_id", "vehicle", "license_plate", "description", "damage_type", "damage_date", "damage_location", "estimated_damage", "police_involved", "other_parties_involved"]}

            submit_result = submit_claim(claim_data_raw)

            if submit_result.get("completed"):
                claim_data = {
                    **claim_data_raw,
                    "claim_id": submit_result["claim_id"],
                }
                content = content.replace("CLM-20251215-0001", submit_result["claim_id"])
            else:
                 handover = None
                 content = f"Entschuldigung, der Schaden konnte nicht eingereicht werden: {submit_result.get('error', 'Unbekannter Fehler')}."

        agent_step = _build_agent_step(content)

        memory.save_context({"user_input": user_input}, {"response": content, "agent_steps": [agent_step]})
        save_state(session_id, state)

        return_data = {
            "response": content,
            "structured": json_data,
            "agent": "insurance",
            "agent_steps": [agent_step]
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
            "agent": "insurance",
            "agent_steps": []
        }