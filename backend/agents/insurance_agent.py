import os
import logging
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory

from agents.memory import get_session_history 
from services.insurance_service import (
    get_user_context, 
    get_claim_status, 
    submit_claim, 
    calculate_premium, 
    get_policy_details
)

load_dotenv()
log = logging.getLogger(__name__)


@tool
def check_policy_details(customer_id: str) -> str:
    """Fragt Versicherungsdetails und Status für eine customer_id ab."""
    details = get_policy_details(str(customer_id))
    return json.dumps(details, indent=2, ensure_ascii=False)

@tool
def calculate_estimated_premium(vehicle_data: str) -> str:
    """Berechnet eine unverbindliche Prämie basierend auf Fahrzeugdaten."""
    result = calculate_premium(vehicle_data)
    return json.dumps(result, indent=2, ensure_ascii=False)

@tool
def get_claim_status_check(claim_id: str) -> str:
    """Fragt den Status eines Schadensfalles (claim_id) ab."""
    status = get_claim_status(claim_id)
    return json.dumps(status, indent=2, ensure_ascii=False)

@tool
def submit_insurance_claim_tool(
    customer_id: str, damage_type: str, damage_date: str, 
    damage_location: str, description: str, vehicle: str, 
    estimated_damage: Optional[str] = None
) -> str:
    """REICHT DEN SCHADEN EIN. Tool aufrufen, wenn alle Daten vorliegen."""
    claim_dict = {
        "customer_id": customer_id, "damage_type": damage_type,
        "damage_date": damage_date, "damage_location": damage_location,
        "description": description, "vehicle": vehicle,
        "estimated_damage": estimated_damage,
        "police_involved": False, "third_party_involved": False
    }
    result = submit_claim(claim_dict)
    return json.dumps(result, indent=2, ensure_ascii=False)

tools = [check_policy_details, calculate_estimated_premium, get_claim_status_check, submit_insurance_claim_tool]


llm = ChatOpenAI(temperature=0.0, model=os.getenv("OPENAI_MODEL", "gpt-5-mini"))

def _load_system_prompt():
    path = os.path.join(os.path.dirname(__file__), "templates", "insurance_classifier.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

prompt = ChatPromptTemplate.from_messages([
    ("system", _load_system_prompt()),
    ("system", "Nutzer-Kontext aus DB: {user_context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_message}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

insurance_agent_with_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="user_message",
    history_messages_key="chat_history",
)


def run_insurance_agent(user_message: str, session_id: str = "INS_DEFAULT", user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    if user_context is None:
        user_context = {}

    identifier = user_context.get("customer_id") or session_id
    db_context = get_user_context(str(identifier))
    if db_context:
        user_context.update(db_context)
    
    context_json = json.dumps(user_context, ensure_ascii=False)
    log.info(f"DEBUG: Übergabe an Agent - Kontext: {context_json}")

    try:
        result = insurance_agent_with_history.invoke(
            {
                "input": user_message,
                "user_message": user_message,
                "user_context": json.dumps(user_context, ensure_ascii=False) 
            },
            config={"configurable": {"session_id": session_id}}
        )

        output_text = result['output']
        
        handover = None
        if "submit_insurance_claim_tool" in str(result.get("intermediate_steps", "")):
            handover = "repair"

        return {
            "response": output_text,
            "agent": "insurance",
            "handover": handover,
            "structured": {"intent": "insurance_claim"}
        }

    except Exception as e:
        log.exception("FEHLER IM INSURANCE AGENT:")
        return {"response": f"Fehler: {str(e)}", "agent": "insurance"}