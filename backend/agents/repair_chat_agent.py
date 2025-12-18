import os
import logging
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory

from agents.email_listener import check_inbox_for_replies
from agents.memory import get_session_history, clear_session_history
from agents.tools.google_search import search_google_maps
from agents.tools.email_sender import send_email_via_smtp
from agents.tools.rag import search_vector_db as rag_search_vector_db


load_dotenv()
log = logging.getLogger(__name__)


llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini") 

@tool
def search_workshops_online(city: str, topic: str = "Verkehrsrecht") -> List[Dict]:
    """Sucht online nach Werkstätten Gibt Name, Adresse, Email-Adresse (gescraped), Telefon und Bewertung zurück."""
    query = f"{topic} Werkstatt {city}"
    return search_google_maps(query=query, num_results=3)

@tool
def send_personal_email(lawyer_email: str, subject: str, email_body: str) -> str:
    """Versendet die E-Mail (Ghostwriting-Modus)."""
    return send_email_via_smtp(to_email=lawyer_email, subject=subject, body=email_body)

@tool
def search_vector_db(query: str, top_k: int = 3) -> List[Dict]:
    """Durchsucht die Vektordatenbank nach relevanten Dokumenten."""
    return rag_search_vector_db(query=query, top_k=top_k)

tools = [search_workshops_online, send_personal_email, search_vector_db]


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")

def _load_template(name: str) -> str:
    path = os.path.join(TEMPLATES_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# Load and adapt template placeholders for ChatPromptTemplate
_RAW_PROMPT = _load_template("repair_general.md")

SYSTEM_PROMPT = _RAW_PROMPT.replace("{user_input}", "{user_message}")

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
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

def run_repair_agent_with_memory(user_query: str, session_id: str = "REPAIR_DEFAULT", user_context: Dict[str, Any] = None) -> str:
    log.info("Prüfe Posteingang auf Antworten...")
    try:
        check_inbox_for_replies()
    except Exception:
        pass

    if user_context is None:
        user_context = {}

    user_name = user_context.get("name", "Unbekannt")
    user_email = user_context.get("email")
    sess_id = session_id or f"WORKSHOP_{user_email}"

    log.info(f"Repair Agent gestartet für: {user_name} (Session: {sess_id})")

    try:
        result = agent_with_chat_history.invoke(
            {
                "user_message": user_query,
                "user_name": user_name,
                "user_email": user_email,
                "session_id": sess_id,
                "phone": user_context.get("phone", ""),
                "vehicle": user_context.get("vehicle", ""),
                "service": user_context.get("service", ""),
                "preferred_date": user_context.get("preferred_date", ""),
                "optional_damage_line": "",
                "damage_description": user_context.get("damage_description", ""),
            },
            config={"configurable": {"session_id": sess_id}}
        )
        return {
            "response": result['output'], 
            "structured": {"intent": "repair"}
        }

    except Exception as e:
        log.exception("FEHLER IM REPAIR AGENT:")
        return {
            "response": "Entschuldigung, es ist ein interner Fehler aufgetreten: " + str(e),
            "structured": {"error": str(e)}
        } 