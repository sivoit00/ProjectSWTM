import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agents.lawyerAgent import handle_lawyer_request 

log = logging.getLogger(__name__)
llm = ChatOpenAI(temperature=0.0, model="gpt-5-nano-2025-08-07") 

PROMPT_ROUTE = """
Du bist ein KI-Orchestrator. Deine Aufgabe ist es, die Nutzeranfrage an den richtigen Agenten zuzuweisen.

Verfügbare Agenten:
- "lawyer": Für Anwälte, Rechtsfragen, Unfälle, Bußgelder, Verträge.
- "general": Für alle anderen Anfragen (allgemeine Konversation, Hallo, etc.).

Gib als einzige Ausgabe reines JSON zurück mit dem Key "agent".

Beispiele:

Text: "Ich brauche einen Anwalt in München wegen einem Autounfall."
JSON: {{"agent":"lawyer"}}

Text: "Hallo, wie geht's dir?"
JSON: {{"agent":"general"}}

Text: "Was ist die Hauptstadt von Frankreich?"
JSON: {{"agent":"general"}}

Text: "Mein Bußgeldbescheid ist da."
JSON: {{"agent":"lawyer"}}

Text: "{user_message}"
JSON:
"""

AGENT_DISPATCHER = {
    "lawyer": handle_lawyer_request,
}

def _get_routing_agent(text: str) -> str:
    """Ermittelt den zuständigen Agenten ('lawyer' or 'general') via LLM."""
    prompt = PROMPT_ROUTE.format(user_message=text)
    
    try:
        response = llm.invoke(prompt)
        raw_content = response.content.strip() 
        data = json.loads(raw_content)
        agent = data.get("agent")
        if agent in AGENT_DISPATCHER:
            return agent
        return "general"
    except Exception as e:
        log.warning("Routing failed: %s. Defaulting to 'general'.", e)
        return "general"

def handle_general_request(user_message: str) -> Dict[str, Any]:
    """
    Standard-Chat-Funktion (wie ChatGPT).
    Wird aufgerufen, wenn agent_name == "general".
    """
    log.info("Handling general request: %s", user_message)
    try:
        prompt = f"Beantworte diese Nutzeranfrage: {user_message}"
        response = llm.invoke(prompt)
        chat_response = response.content
        
        return {"response": chat_response.strip(), "structured": {"intent": "general"}}
    
    except Exception as e:
        log.exception("General request failed: %s", e)
        return {"response": "Tut mir leid, ich habe gerade ein technisches Problem.", "structured": {"intent": "general", "error": str(e)}}

def route_message(user_message: str) -> Dict[str, Any]:
    """
    Die Hauptfunktion, die von FastAPI aufgerufen wird.
    Leitet die Anfrage an den richtigen Handler weiter.
    """
    log.info("kiClone routing message: %s", user_message)
    agent_name = _get_routing_agent(user_message)
    log.info("Routing decision: %s", agent_name)
    if agent_name == "general":
        response = handle_general_request(user_message)
    else:
        handler_func = AGENT_DISPATCHER[agent_name]
        try:
            response = handler_func(user_message)
        except Exception as e:
            log.exception("Agent '%s' failed to execute.", agent_name)
            response = {"response": "Entschuldigung, der zuständige Fachbereich ist gerade nicht verfügbar.", "structured": {"intent": agent_name, "error": str(e)}}
    
    return response