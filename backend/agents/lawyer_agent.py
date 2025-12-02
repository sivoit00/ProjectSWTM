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
from agents.memory import get_session_history
from agents.tools.google_search import search_google_maps
from agents.tools.email_sender import send_email_via_smtp

load_dotenv()
log = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER") 
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_TO = os.environ.get("SMTP_TO") 

llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini") 

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
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

SYSTEM_PROMPT = _load_template("lawyer_system.md")

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

def handle_lawyer_request(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    log.info("Prüfe Posteingang auf Antworten...")
    try:
        check_inbox_for_replies()
    except Exception:
        pass

    if user_context is None:
        user_context = {}

    user_name = user_context.get("name", "Unbekannt")
    user_email = user_context.get("email")
    session_id = f"LAWYER_{user_email}"

    log.info(f"LawyerAgent gestartet für: {user_name} (Session: {session_id})")

    try:
        result = agent_with_chat_history.invoke(
            {
                "user_message": user_message,
                "user_name": user_name,
                "user_email": user_email,
                "session_id": session_id
            },
            config={"configurable": {"session_id": session_id}}
        )
        
        return {
            "response": result['output'], 
            "structured": {"intent": "lawyer"}
        }
    except Exception as e:
        log.exception("FEHLER IM LAWYER AGENT:")
        return {
            "response": "Fehler: " + str(e),
            "structured": {"error": str(e)}
        }