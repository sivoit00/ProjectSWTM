import os
import logging
import json
from typing import Any, Dict, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory

from agents.email_listener import check_inbox_for_replies
from agents.memory import get_session_history
from agents.tools.google_search import search_google_maps
from agents.tools.email_sender import send_email_via_smtp
from agents.tools.orchestrator_utils import process_handover_signal
from agents.tools.context_service import get_complete_user_context

load_dotenv()
log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini") 

@tool
def search_lawyers_online(city: str, topic: str = "Verkehrsrecht") -> List[Dict]:
    """Sucht online nach Anwälten. Gibt Name, Adresse, Email-Adresse (gescraped), Telefon und Bewertung zurück."""
    query = f"{topic} Anwalt {city}"
    return search_google_maps(query=query, num_results=3)

@tool
def send_personal_email(lawyer_email: str, subject: str, email_body: str) -> str:
    """Versendet die E-Mail (Ghostwriting-Modus)."""
    return send_email_via_smtp(to_email=lawyer_email, subject=subject, body=email_body)

tools = [search_lawyers_online, send_personal_email]

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

def _load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    if not os.path.exists(path):
        return "You are a lawyer agent. User ID: {user_id}. Always include [Ref: {user_id}] in email subjects."
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = _load_template("lawyer_system.md")

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("system", "Nutzer-Kontext aus DB: {user_context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_message}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

agent_with_chat_history = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="user_message",
    history_messages_key="chat_history",
)

def handle_lawyer_request(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    log.info("Prüfe Posteingang auf Antworten...")
    try:
        check_inbox_for_replies()
    except Exception:
        pass

    if user_context is None:
        user_context = {}

    identifier = (
        user_context.get("user_id") or 
        user_context.get("customer_id") or 
        user_context.get("email") or 
        "anonymous"
    )

    log.info(f"LawyerAgent gestartet für: {user_id}")

    # WEICHE: Handover-Signal abfangen
    if user_message == "SYSTEM_HANDOVER_FROM_INSURANCE":
        actual_message = (
            f"Ich habe gerade einen Versicherungsschaden für {user_name} aufgenommen. "
            f"Es geht um einen Vorfall mit dem Fahrzeug {user_context.get('vehicle', 'Unbekannt')}. "
            f"Biete dem Kunden eine rechtliche Erstberatung an und frage nur noch nach fehlenden "
            f"rechtlichen Details wie z.B. Personenschaden oder Polizeibericht."
        )
    else:
        actual_message = user_message
    db_context = get_complete_user_context(str(identifier))
    
    final_context_data = user_context
    if db_context and "error" not in db_context:
        final_context_data = db_context
    
    context_json = json.dumps(final_context_data, indent=2, ensure_ascii=False)

    user_name = final_context_data.get("customer", {}).get("full_name") or user_context.get("name", "Unbekannt")
    user_email = final_context_data.get("customer", {}).get("email") or user_context.get("email")
    user_id = str(final_context_data.get("customer", {}).get("id") or user_context.get("user_id", "anonymous"))
    
    session_id = user_context.get("session_id")
    if not session_id:
         session_id = f"LAWYER_{user_id}"
         
    log.info(f"LawyerAgent gestartet für: {user_name} (Session: {session_id})")

    try:
        result = agent_with_chat_history.invoke(
            {
                "user_message": actual_message,
                "user_context": context_json,
                "user_name": user_name,
                "user_id": user_id,
                # ...
            },
            config={"configurable": {"session_id": session_id}}
        )
        output_text = result['output']
        
        handover_target, clean_text = process_handover_signal(output_text)

        return {
            "response": clean_text, 
            "handover": handover_target,
            "structured": {"intent": "lawyer"}
        }

    except Exception as e:
        log.exception("FEHLER IM LAWYER AGENT:")
        return {
            "response": "Entschuldigung, es ist ein interner Fehler aufgetreten: " + str(e),
            "structured": {"error": str(e)}
        }