import json
import logging
from typing import Any, Dict
from langchain_openai import ChatOpenAI
from agents.lawyerAgent import handle_lawyer_request
from agents.insurance_agent import run_insurance_agent

log = logging.getLogger(__name__)

llm = ChatOpenAI(
    temperature=0.0,
    model="gpt-5-nano-2025-08-07"
)

PROMPT_ROUTE = """
Du bist ein KI-Orchestrator. Entscheide, welcher Agent zuständig ist.

Agenten:
- "lawyer": Anwälte, Rechtsfragen, Unfälle, Bußgelder, Verträge.
- "insurance": Versicherung, Police, Schaden, Prämie, Deckung, Versicherungsstatus.
- "general": Alles andere.

Format der Ausgabe: reines JSON, nur:
{{
  "agent": "<lawyer|insurance|general>"
}}

Analysen und Erklärungen sind verboten.

Nutzertext: "{user_message}"
JSON:
"""

AGENT_DISPATCHER = {
    "lawyer": handle_lawyer_request,
    "insurance": run_insurance_agent,
}


def _safe_json_loads(s: str) -> dict:
    """Sorgt dafür, dass das LLM-JSON zuverlässig geparst wird."""
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        log.warning("LLM lieferte kein valides JSON: %s", s)
        return {}


def _get_routing_agent(text: str) -> str:
    prompt = PROMPT_ROUTE.format(user_message=text)

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()

        data = _safe_json_loads(raw)
        agent = data.get("agent")

        if agent in AGENT_DISPATCHER or agent == "general":
            return agent

        return "general"

    except Exception as e:
        log.warning("Routing-Fehler: %s", e)
        return "general"


def handle_general_request(user_message: str) -> Dict[str, Any]:
    log.info("Handling general request.")
    try:
        prompt = f"Beantworte kurz und hilfreich: {user_message}"
        response = llm.invoke(prompt)
        return {
            "response": response.content.strip(),
            "structured": {"intent": "general"}
        }
    except Exception as e:
        log.exception("General agent failed.")
        return {
            "response": "Tut mir leid, es gab ein Problem.",
            "structured": {"intent": "general", "error": str(e)}
        }


def route_message(user_message: str) -> Dict[str, Any]:
    print("route_message called with:", user_message)
    log.info("kiClone routing: %s", user_message)

    agent_name = _get_routing_agent(user_message)
    log.info("Routing result: %s", agent_name)

    if agent_name == "general":
        return handle_general_request(user_message)

    try:
        handler = AGENT_DISPATCHER[agent_name]
        return handler(user_message)

    except Exception as e:
        log.exception("Agent '%s' failed.", agent_name)
        return {
            "response": "Der zuständige Fachbereich ist gerade nicht verfügbar.",
            "structured": {"intent": agent_name, "error": str(e)}
        }
