import os
import logging
import smtplib
from typing import Any, Dict, List
from email.message import EmailMessage

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.memory import ConversationBufferMemory
import requests
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-4o-mini") 

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER") 
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_TO = os.environ.get("SMTP_TO") 

@tool
def search_lawyers_online(city: str, topic: str = "Verkehrsrecht") -> List[Dict]:
    """Sucht online nach Anwälten. Gibt Name, Adresse, Email-Adresse, Telefon und BEWERTUNG zurück."""
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google", "q": f"{topic} Anwalt {city}", "google_domain": "google.com",
        "hl": "de", "num": 3, "api_key": SERPAPI_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        results = []
        for item in data.get("local_results", {}).get("places", [])[:3]:
            lawyer = {
                "name": item.get("title"),
                "email": SMTP_TO, 
                "telefon": item.get("phone") or "Keine Nummer",
                "anschrift": item.get("address") or "Keine Adresse",
                "bewertung": item.get("rating") or "Keine Bewertung",
                "reviews": item.get("reviews") or 0
            }
            results.append(lawyer)
        return results
    except Exception as e:
        log.error(f"SerpAPI Fehler: {e}")
        return []

@tool
def send_personal_email(lawyer_email: str, subject: str, email_body: str) -> str:
    """Versendet die E-Mail (Ghostwriting-Modus)."""
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER 
        msg["To"] = SMTP_TO 
        msg["Subject"] = subject
        msg.set_content(email_body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return f"E-Mail erfolgreich versendet."
    except Exception as e:
        return f"Fehler beim Versand: {str(e)}"

tools = [search_lawyers_online, send_personal_email]


SYSTEM_PROMPT = """
Du bist ein persönlicher Assistent (Ghostwriter) für den Nutzer.
Ziel: Anwalt finden und E-Mail schreiben.

**USER DATEN:**
Name: {user_name}
Email: {user_email}

**Regeln:**
1. **Interview:** Erst alle W-Fragen klären (Was, Wann, Wo, Versicherung).
   - FRAGE NICHT nach dem Namen, wenn er oben unter "USER DATEN" steht.
   
2. **Suche:** Nutze `search_lawyers_online`.
   - Nenne IMMER Name, Adresse UND Bewertung.

3. **Auswahl & Email:** - Nutze `send_personal_email`.
   - Schreibe aus der ICH-Perspektive.
   - Unterschreibe mit dem Namen des Nutzers.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_message}"),
    ("placeholder", "{agent_scratchpad}"),
])

memory = ConversationBufferMemory(
    memory_key="chat_history", 
    return_messages=True,
    input_key="user_message" 
)

agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)


def handle_lawyer_request(user_message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Nimmt user_message UND user_context entgegen.
    """
    if user_context is None:
        user_context = {}

    user_name = user_context.get("name", "Unbekannt")
    user_email = user_context.get("email", "Unbekannt")

    log.info(f"LawyerAgent gestartet für: {user_name}")

    try:
        result = agent_executor.invoke({
            "user_message": user_message,
            "user_name": user_name,
            "user_email": user_email
        })
        
        return {
            "response": result['output'], 
            "structured": {"intent": "lawyer"}
        }
    except Exception as e:
        log.exception("FEHLER IM LAWYER AGENT:")
        return {
            "response": "Entschuldigung, beim Verarbeiten Ihrer Anfrage ist ein interner Fehler aufgetreten.",
            "structured": {"error": str(e)}
        }