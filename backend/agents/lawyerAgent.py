import os
import json
import logging
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
import requests
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

# LLM
llm = ChatOpenAI(temperature=0.0, model="gpt-5-nano-2025-08-07")

# SerpAPI Key aus .env
SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
if not SERPAPI_KEY:
    raise ValueError("SERPAPI_KEY nicht gesetzt. Bitte in .env eintragen.")

@tool
def search_lawyers_online(city: str, topic: str = "Verkehrsrecht") -> List[Dict]:
    """
    Sucht online nach Anwälten via SerpAPI Google Search API.
    Liefert Name, Email, Telefon, Anschrift, Bewertung zurück.
    Maximal 3 Ergebnisse.
    """
    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google",
        "q": f"{topic} Anwalt {city}",
        "google_domain": "google.com",
        "hl": "de",
        "num": 3,
        "api_key": SERPAPI_KEY,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []

        for item in data.get("local_results", {}).get("places", [])[:3]:
            lawyer = {
                "name": item.get("title"),
                "email": item.get("email") or "Keine Info",
                "telefon": item.get("phone") or "Keine Info",
                "anschrift": item.get("address") or "Keine Info",
                "bewertung": item.get("rating") or "Keine Info"
            }
            results.append(lawyer)
        return results

    except Exception as e:
        log.exception("Fehler bei der SerpAPI-Anfrage: %s", e)
        return []

# Tools
tools = [search_lawyers_online]

# System-Prompt für saubere Ausgabe
SYSTEM_PROMPT = """
Du bist ein spezialisierter Assistent des "systecs-Fahrzeugservice".
Deine Aufgabe ist es, Nutzern bei der Anwaltssuche zu helfen.

- Nutze die Funktion 'search_lawyers_online(city, topic)'.
- Zeige maximal 3 Ergebnisse mit Name, Email, Telefon, Anschrift, Bewertung.
- Formatiere die Antwort **immer** als Markdown-Liste:
* Name — Email — Telefon — Anschrift — Bewertung
- Wenn keine Ergebnisse gefunden werden, informiere den Nutzer höflich.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{user_message}"),
    ("placeholder", "{agent_scratchpad}"),
])

# Agent erstellen
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

def handle_lawyer_request(user_message: str) -> Dict[str, Any]:
    log.info("LawyerAgent (online) processing: %s", user_message)
    try:
        result = agent_executor.invoke({"user_message": user_message})
        return {"response": result['output'], "structured": {"intent": "lawyer"}}
    except Exception as e:
        log.exception("LawyerAgent (online) failed: %s", e)
        return {"response": "Entschuldigung, die Anwaltssuche ist gerade nicht verfügbar.",
                "structured": {"intent": "lawyer", "error": str(e)}}
