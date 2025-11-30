"""
Session Management für persistentes Agent-Routing
Speichert den aktuellen Agent pro User-Session
"""
from typing import Dict, Optional
import logging

log = logging.getLogger(__name__)

# In-Memory Session Store (kann später durch Redis/DB ersetzt werden)
_session_store: Dict[str, Dict[str, any]] = {}

def get_session_state(session_id: str) -> Dict[str, any]:
    """
    Holt den Session-State für eine bestimmte Session.
    Erstellt automatisch einen neuen State wenn nicht vorhanden.
    """
    if session_id not in _session_store:
        _session_store[session_id] = {
            "active_agent": "chatbot",  # Tom ist Default
            "conversation_count": 0,
            "last_intent": None
        }
        log.info(f"Neue Session erstellt: {session_id} | active_agent=chatbot")
    
    return _session_store[session_id]


def set_active_agent(session_id: str, agent_name: str) -> None:
    """
    Setzt den aktiven Agent für eine Session.
    """
    state = get_session_state(session_id)
    old_agent = state["active_agent"]
    state["active_agent"] = agent_name
    
    if old_agent != agent_name:
        log.info(f"Session {session_id}: Agent-Wechsel {old_agent} → {agent_name}")


def get_active_agent(session_id: str) -> str:
    """
    Gibt den aktuellen aktiven Agent für eine Session zurück.
    """
    state = get_session_state(session_id)
    return state["active_agent"]


def increment_conversation(session_id: str) -> None:
    """
    Erhöht den Nachrichtenzähler für die Session.
    """
    state = get_session_state(session_id)
    state["conversation_count"] += 1


def reset_session(session_id: str) -> None:
    """
    Setzt die Session zurück (z.B. bei Themenwechsel zu Tom).
    """
    if session_id in _session_store:
        log.info(f"Session {session_id} wird zurückgesetzt")
        del _session_store[session_id]


def clear_all_sessions() -> None:
    """
    Löscht alle Sessions (für Tests/Debugging).
    """
    global _session_store
    _session_store = {}
    log.info("Alle Sessions wurden gelöscht")
