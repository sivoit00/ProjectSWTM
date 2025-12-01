import os
import logging
import smtplib
from typing import Any, Dict, List
from email.message import EmailMessage
import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import pathlib
from langchain.tools import tool
from langchain_core.runnables.history import RunnableWithMessageHistory
from agents.email_listener import check_inbox_for_replies
from agents.memory import get_session_history

load_dotenv()
log = logging.getLogger(__name__)


SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER") 
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_TO = os.environ.get("SMTP_TO") 

llm = ChatOpenAI(temperature=0.0, model="gpt-5-mini") 

def _extract_email_from_url(url: str) -> str:
    """Besucht eine URL und extrahiert die E-Mail via LLM."""
    if not url:
        return "Keine Website"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return "Seite nicht erreichbar"
    
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.extract()
            
        text_content = soup.get_text()[:4000]
        
        extraction_prompt = f"""
        Suche im folgenden Text nach einer Kontakt-Email-Adresse für den Anwalt oder die Kanzlei.
        Gib NUR die E-Mail zurück. Wenn keine gefunden wird, antworte mit 'N/A'.
        
        Text:
        {text_content}
        """
        
        result = llm.invoke(extraction_prompt)
        return result.content.strip()

    except Exception as e:
        log.warning(f"Email Scraping Fehler bei {url}: {e}")
        return "N/A"

@tool
def search_lawyers_online(city: str, topic: str = "Verkehrsrecht") -> List[Dict]:
    """Sucht online nach Anwälten. Gibt Name, Adresse, Email-Adresse, Telefon und BEWERTUNG zurück."""
    if not SERPAPI_KEY:
        return [{"error": "SERPAPI_KEY fehlt."}]
        
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps", "q": f"{topic} Anwalt {city}", "google_domain": "google.com",
        "hl": "de", "num": 3, "api_key": SERPAPI_KEY
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        results = []
        local_results = data.get("local_results", [])
        if not local_results and "organic_results" in data:
             local_results = data.get("organic_results", [])[:3]

        for item in local_results:
            website_url = item.get("website")

            found_email = "Nicht gefunden"
            if website_url:
                found_email = _extract_email_from_url(website_url)

            lawyer = {
                "name": item.get("title"),
                "email": found_email,
                "website": website_url,
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
        return f"E-Mail erfolgreich versendet an {SMTP_TO} (statt {lawyer_email} zu Testzwecken)."
    except Exception as e:
        return f"Fehler beim Versand: {str(e)}"

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
    """
    Nimmt user_message UND user_context entgegen.
    """
    log.info("Prüfe Posteingang auf Antworten...")
    check_inbox_for_replies()

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
            "response": "Entschuldigung, beim Verarbeiten Ihrer Anfrage ist ein interner Fehler aufgetreten.",
            "structured": {"error": str(e)}
        }