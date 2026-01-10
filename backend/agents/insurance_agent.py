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
from langchain_core.messages import SystemMessage

from agents.memory import get_session_history
from agents.tools.orchestrator_utils import process_handover_signal
from services.insurance_service import (
    get_claim_status, 
    submit_claim, 
    calculate_premium, 
)

from agents.tools.context_service import get_complete_user_context

load_dotenv()
log = logging.getLogger(__name__)


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

tools = [calculate_estimated_premium, get_claim_status_check, submit_insurance_claim_tool]


llm = ChatOpenAI(temperature=0.0, model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))

def _load_system_prompt():
    path = os.path.join(os.path.dirname(__file__), "templates", "insurance_classifier.md")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content=_load_system_prompt()), # <--- Statisch laden!
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

    identifier = (
        user_context.get("user_id") or 
        user_context.get("customer_id") or 
        user_context.get("email") or 
        session_id
    )
 
    db_context = get_complete_user_context(str(identifier))
    
    if db_context and "error" not in db_context:
        user_context = db_context
    
    context_json = json.dumps(user_context, ensure_ascii=False, indent=2)
    log.info(f"DEBUG: Übergabe an Agent - Kontext: {context_json}")

    try:
        result = insurance_agent_with_history.invoke(
            {
                "input": user_message,
                "user_message": user_message,
                "user_context": context_json 
            },
            config={"configurable": {"session_id": session_id}}
        )

        output_text = result['output']
        
        handover_target, clean_text = process_handover_signal(output_text)

        return {
            "response": clean_text,
            "agent": "insurance",
            "handover": handover_target, 
            "structured": {
                "intent": "insurance_claim",
                "customer_id": user_context.get("customer", {}).get("id")
            }
        }
    except Exception as e:
        log.exception("FEHLER IM INSURANCE AGENT:")
        return {"response": f"Fehler: {str(e)}", "agent": "insurance"}