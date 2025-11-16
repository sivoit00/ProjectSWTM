import json
import logging
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI 
from .tools.searchTools import search_lawyers_by_city

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool

log = logging.getLogger(__name__)

llm = ChatOpenAI(temperature=0.0, model="gpt-5-nano-2025-08-07") 

@tool
def search_lawyers_by_city_tool(city: str, topic: str = "Verkehrsrecht") -> List[Dict]:
    """
    Sucht Anwälte in einer Stadt basierend auf einem Fachgebiet.
    Gibt eine Liste von Anwälten zurück.
    """
    return search_lawyers_by_city(city, topic)

tools = [search_lawyers_by_city_tool]

SYSTEM_PROMPT = """
Du bist ein spezialisierter Assistent des "systecs-Fahrzeugservice".
Deine Aufgabe ist es, Nutzern bei der Anwaltssuche zu helfen.

- Wenn der Nutzer einen Anwalt sucht, nutze dein 'search_lawyers_by_city_tool'.
- Du musst die Stadt (city) und das Thema (topic) aus der Anfrage ableiten.
- Wenn die Stadt fehlt, frage den Nutzer höflich danach.
- Wenn das Thema fehlt, verwende "Verkehrsrecht" als Standard.
- Präsentiere die Ergebnisse (maximal 3) direkt im Chat.
- Präsentiere Suchergebnisse **immer** als Markdown-Liste.
- Beginne **JEDES** Listenelement in einer **NEUEN ZEILE** mit einem Sternchen (`*`).
- **Beispiel für eine perfekte Antwort (exaktes Format):**
Hier sind die Empfehlungen, die ich gefunden habe:
* Kanzlei Müller — Verkehrsrecht, Schadensersatz — 089-1234
* Rechtsanwalt Schmid — Verkehrsrecht — 089-5678
- Wenn keine Ergebnisse gefunden werden, teile dies dem Nutzer mit.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{user_message}"),
    ("placeholder", "{agent_scratchpad}"), 
])

agent = create_openai_tools_agent(llm, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)

def handle_lawyer_request(user_message: str) -> Dict[str, Any]:
    log.info("LawyerAgent (Agent-Mode) processing: %s", user_message)
    
    try:
        result = agent_executor.invoke({
            "user_message": user_message
        })
        
        return {"response": result['output'], "structured": {"intent": "lawyer"}}

    except Exception as e:
        log.exception("lawYAgent (Agent-Mode) failed: %s", e)
        return {"response": "Entschuldigung, die Anwaltssuche ist gerade nicht verfügbar.", "structured": {"intent": "lawyer", "error": str(e)}}