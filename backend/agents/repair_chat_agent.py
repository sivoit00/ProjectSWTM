import os
import logging
import smtplib
from typing import Any, Dict, List
from email.message import EmailMessage
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory

from agents.email_listener import check_inbox_for_replies
from agents.memory import get_session_history, global_store
from agents.tools.google_search import search_google_maps
from agents.tools.email_sender import send_email_via_smtp
from agents.tools.rag import search_vector_db as rag_search_vector_db
from fastapi import HTTPException

load_dotenv()
log = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER") 
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_TO = os.environ.get("SMTP_TO") 

llm = ChatOpenAI(temperature=0.0, model="gpt-5") 

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
# Strategy: escape ALL braces, then restore the two intended prompt variables
_ESCAPED = _RAW_PROMPT.replace("{", "{{").replace("}", "}}")
_ESCAPED = _ESCAPED.replace("{{user_input}}", "{user_message}")
_ESCAPED = _ESCAPED.replace("{{chat_history}}", "{chat_history}")
SYSTEM_PROMPT = _ESCAPED

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

def clear_session_memory(session_id: str) -> None:
    """Clears chat history for a given session id (orchestrator compatibility)."""
    try:
        if session_id in global_store:
            del global_store[session_id]
    except Exception:
        pass

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
                # Optional fields to satisfy escaped variables; they render as literals if empty
                "phone": user_context.get("phone", ""),
                "vehicle": user_context.get("vehicle", ""),
                "service": user_context.get("service", ""),
                "preferred_date": user_context.get("preferred_date", ""),
                "optional_damage_line": "",
                "damage_description": user_context.get("damage_description", ""),
            },
            config={"configurable": {"session_id": sess_id}}
        )
        return result['output'] if isinstance(result, dict) else str(result)
    except Exception as e:
        log.exception("FEHLER IM REPAIR AGENT:")
        return "Fehler: " + str(e)