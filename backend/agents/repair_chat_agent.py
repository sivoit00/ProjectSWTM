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
from agents.memory import get_session_history, clear_session_history
from agents.tools.google_search import search_google_maps
from agents.tools.email_sender import send_email_via_smtp
from agents.tools.rag import search_vector_db as rag_search_vector_db
from agents.tools.orchestrator_utils import process_handover_signal
from agents.tools.context_service import get_complete_user_context


load_dotenv()
log = logging.getLogger(__name__)


llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini") 

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
SYSTEM_PROMPT = _load_template("repair_general.md")

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

def run_repair_agent_with_memory(user_query: str, session_id: str = "REPAIR_DEFAULT", user_context: Dict[str, Any] = None) -> Dict[str, Any]:
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

    db_context = get_complete_user_context(str(identifier))

    final_context_data = user_context
    if db_context and "error" not in db_context:
        final_context_data = db_context

    context_json = json.dumps(final_context_data, indent=2, ensure_ascii=False)

    user_name = (
        final_context_data.get("customer", {}).get("full_name")
        or user_context.get("name")
        or "Unbekannt"
    )
    user_email = final_context_data.get("customer", {}).get("email") or user_context.get("email")
    user_id = str(final_context_data.get("customer", {}).get("id") or user_context.get("user_id", "anonymous"))

    sess_id = session_id or f"WORKSHOP_{user_id}"

    log.info(f"Repair Agent gestartet für: {user_name} (Session: {sess_id})")

    log.info(f"Repair Agent gestartet für: {user_name} (Session: {sess_id})")

    # WEICHE: Handover-Signal abfangen
    if user_query == "SYSTEM_HANDOVER_FROM_INSURANCE":
        # Wir bauen eine interne Nachricht, die dem LLM erklärt, was los ist
        actual_query = (
            f"Ein Schaden wurde gerade erfolgreich gemeldet. "
            f"Fahrzeug: {user_context.get('vehicle', 'Unbekannt')}. "
            f"Schaden: {user_context.get('damage_description', 'Nicht näher definiert')}. "
            f"Begrüße den Kunden {user_name} und biete ihm direkt an, einen Termin in seiner "
            f"bevorzugten Werkstatt {user_context.get('preferred_workshop', {}).get('name', 'einer Partnerwerkstatt')} zu vereinbaren."
        )
    else:
        actual_query = user_query

    try:
        result = agent_with_chat_history.invoke(
            {
                "user_message": actual_query, # Hier nutzen wir die übersetzte Nachricht
                "user_name": user_name,
                "user_email": user_email,
                # ... restliche Parameter wie bisher
            },
            config={"configurable": {"session_id": sess_id}}
        )   
        output_text = result['output']
        
        handover_target, clean_text = process_handover_signal(output_text)

        return {
            "response": clean_text, 
            "handover": handover_target,
            "structured": {"intent": "repair"}
        }

    except Exception as e:
        log.exception("FEHLER IM REPAIR AGENT:")
        return {
            "response": "Entschuldigung, es ist ein interner Fehler aufgetreten: " + str(e),
            "structured": {"error": str(e)}
        } 