import os
import logging
import json
import re
from typing import Dict, Any, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from services.insurance_utils import get_or_create_memory, save_state, load_state
from services.insurance_service import (
    get_user_context, 
    get_claim_status, 
    submit_claim, 
    calculate_premium, 
    get_policy_details
)

log = logging.getLogger(__name__)

@tool
def check_policy_details(customer_id: str) -> str:
    """
    Fragt die Versicherungsdetails, den Deckungsumfang und den Status der Police 
    für eine bestimmte Kundennummer (customer_id) ab.
    """
    if not customer_id:
        return "ERROR: Customer ID fehlt. Bitte fragen Sie den User danach."
    details = get_policy_details(str(customer_id))
    return json.dumps(details, indent=2, ensure_ascii=False)

@tool
def calculate_estimated_premium(vehicle_data: str) -> str:
    """
    Berechnet eine unverbindliche Schätzung der Versicherungsprämie basierend auf Fahrzeugdaten 
    (Modell, Baujahr, Wert).
    """
    result = calculate_premium(vehicle_data)
    return json.dumps(result, indent=2, ensure_ascii=False)

@tool
def get_claim_status_check(claim_id: str) -> str:
    """
    Fragt den Bearbeitungsstatus eines gemeldeten Schadensfalles (claim_id) ab.
    """
    status = get_claim_status(claim_id)
    return json.dumps(status, indent=2, ensure_ascii=False)

@tool
def submit_insurance_claim_tool(
    customer_id: str,
    damage_type: str,
    damage_date: str,
    damage_location: str,
    description: str,
    vehicle: str,
    estimated_damage: Optional[str] = None
) -> str:
    """
    REICHT DEN SCHADEN EIN. Dieses Tool MUSS aufgerufen werden, sobald 
    Typ, Datum, Ort, Beschreibung, Fahrzeug und Kunden-ID bekannt sind.
    """
    claim_dict = {
        "customer_id": customer_id,
        "damage_type": damage_type,
        "damage_date": damage_date,
        "damage_location": damage_location,
        "description": description,
        "vehicle": vehicle,
        "estimated_damage": estimated_damage,
        "police_involved": False, 
        "third_party_involved": False
    }

    result = submit_claim(claim_dict)
    return json.dumps(result, indent=2, ensure_ascii=False)


def _load_prompt() -> str:
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    path = os.path.join(templates_dir, "insurance_classifier.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _build_agent_step(response_text: str) -> Dict[str, Any]:
    return {
        "task": "insurance_processing",
        "timestamp": datetime.utcnow().isoformat(),
        "status": "completed",
        "agent": "insurance",
        "details": response_text
    }


def run_insurance_agent(
    user_input: str,
    session_id: str = "default",
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"response": "API Key fehlt.", "agent": "insurance"}

    llm = ChatOpenAI(
        api_key=api_key,
        model=os.getenv("OPENAI_MODEL", "gpt-5-mini"), 
        temperature=0
    )

    memory = get_or_create_memory(session_id)
    
    identifier = session_id
    if user_context:
        identifier = user_context.get("customer_id") or user_context.get("email") or session_id
    
    db_context = get_user_context(str(identifier))
    if db_context:
        if not user_context: user_context = {}
        user_context.update(db_context)

    state = load_state(session_id, user_context)
    chat_history_list = memory.load_memory_variables({}).get("chat_history", [])

    raw_template = _load_prompt()
    
    u_context_json = json.dumps(user_context, indent=2, ensure_ascii=False)
    u_context_escaped = u_context_json.replace("{", "{{").replace("}", "}}")
    
    context_prefix = f"## Aktueller Benutzerkontext (DB):\n{u_context_escaped}\n\n"
    system_content = context_prefix + raw_template

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_content),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    tools = [
        check_policy_details, 
        calculate_estimated_premium, 
        get_claim_status_check, 
        submit_insurance_claim_tool
    ]
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True
    )

    try:
        res_output = agent_executor.invoke({
            "input": user_input,
            "chat_history": chat_history_list
        })

        content = res_output.get("output", "").strip()
        intermediate_steps = res_output.get("intermediate_steps", [])

        handover = None
        claim_data = None

        for action, observation in intermediate_steps:
            if action.tool == "submit_insurance_claim_tool":
                handover = "repair"
                try:
                    obs_data = json.loads(observation)
                    if obs_data.get("completed"):
                        claim_data = obs_data
                except:
                    pass

        agent_step = _build_agent_step(content)
        memory.save_context({"user_input": user_input}, {"response": content})
        save_state(session_id, state)

        result = {
            "response": content,
            "agent": "insurance",
            "agent_steps": [agent_step],
            "handover": handover
        }
        if claim_data:
            result["claim_data"] = claim_data

        return result

    except Exception as e:
        log.exception(f"Error in insurance agent: {e}")
        return {
            "response": "Entschuldigung, ich habe gerade ein technisches Problem. Versuchen wir es gleich nochmal.",
            "agent": "insurance"
        }