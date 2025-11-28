from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import anyio
import logging
from typing import Optional, Dict, Any, List
from jose import jwt
from agents.kiClone import route_message 
from agents.repair_chat_agent import clear_session_memory
from services.guardrails_service import validate_request
import uuid
from datetime import datetime

router = APIRouter()
log = logging.getLogger(__name__)

class KIMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class AgentStep(BaseModel):
    agent: str
    timestamp: str
    status: str
    description: str

def extract_user_from_header(auth_header: Optional[str]) -> Dict[str, Any]:
    """
    Liest Name und Email aus dem Keycloak-Token, falls vorhanden.
    """
    default_context = {"name": None, "email": None, "user_id": None}
    
    if not auth_header:
        return default_context

    try:
        token = auth_header.split(" ")[1]
        payload = jwt.get_unverified_claims(token)
        
        return {
            "name": payload.get("name") or payload.get("preferred_username"),
            "email": payload.get("email"),
            "user_id": payload.get("sub")
        }
    except Exception as e:
        log.warning(f"Konnte User-Token nicht lesen: {e}")
        return default_context

@router.post("/message")
async def ki_message(
    req: KIMessage,
    authorization: Optional[str] = Header(None) 
):
    log.info("KI-Orchestrator received message: %s", req.message)
    user_context = extract_user_from_header(authorization)
    
    # Track agent steps for timeline visualization
    agent_steps: List[Dict[str, Any]] = []
    
    def add_step(agent: str, status: str, description: str):
        agent_steps.append({
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "description": description
        })
    
    if user_context['name']:
        log.info(f"User erkannt: {user_context['name']}")

    # === GUARDRAILS: Input-Validierung ===
    add_step("guardrails", "active", "Überprüfe Nachricht auf Sicherheit...")
    validation_result = validate_request(req.message, user_context)
    
    if not validation_result["valid"]:
        # Nachricht wurde blockiert - Support-Team wurde informiert (via DB-Log)
        severity = validation_result.get("severity", "MEDIUM")
        add_step("guardrails", "completed", "Nachricht wurde blockiert")
        
        # Antwort an Nutzer anpassen je nach Schweregrad
        if severity == "CRITICAL":
            user_message = "⚠️ Ihre Nachricht enthält unangemessene Inhalte und wurde an unser Support-Team weitergeleitet. Bitte formulieren Sie Ihre Anfrage respektvoll."
        elif severity == "HIGH":
            user_message = "⚠️ Ihre Anfrage konnte nicht verarbeitet werden. Bitte kontaktieren Sie unser Support-Team für weitere Hilfe."
        else:
            user_message = validation_result.get("blocked_reason", "Ihre Anfrage konnte nicht verarbeitet werden.")
        
        return {
            "ok": False,
            "response": user_message,
            "agent": "guardrails",
            "blocked": True,
            "agent_steps": agent_steps
        }
    
    add_step("guardrails", "completed", "Nachricht ist sicher")
    
    # Verwende gefilterten Input (z.B. sensible Daten wurden entfernt)
    filtered_message = validation_result["filtered_input"]
    
    # Wenn Warnungen existieren (z.B. sensible Daten wurden gefiltert), logge diese
    if validation_result.get("warnings"):
        log.info(f"Guardrails warnings for user {user_context.get('name', 'Unknown')}: {validation_result['warnings']}")

    # include session_id from body (if provided) into user_context so agents can use per-session memory
    if getattr(req, 'session_id', None):
        user_context['session_id'] = req.session_id

    try:
        add_step("chatbot", "active", "Tom's KI analysiert die Anfrage...")
        result = await anyio.to_thread.run_sync(
            route_message,
            filtered_message,  # Gefilterte Nachricht verwenden
            user_context,
        )

        if not isinstance(result, dict):
            raise ValueError("route_message returned invalid format")

        # Determine which agent was used based on result
        agent_type = result.get("agent", "general")
        
        # Spezifische Beschreibungen für verschiedene Agents
        if agent_type == "repair":
            add_step(agent_type, "active", "Werkstatt Agent sucht nach passenden Werkstätten...")
            add_step("chatbot", "completed", "Tom's KI bereitet die Antwort vor")
        elif agent_type == "lawyer":
            add_step(agent_type, "active", "Rechts Agent prüft rechtliche Aspekte...")
            add_step("chatbot", "completed", "Tom's KI bereitet die Antwort vor")
        elif agent_type == "insurance":
            add_step(agent_type, "active", "Versicherungs Agent prüft Ihre Police...")
            add_step("chatbot", "completed", "Tom's KI bereitet die Antwort vor")
        else:
            add_step("chatbot", "completed", "Tom's KI hat die Antwort erstellt")
        
        result["agent_steps"] = agent_steps
        return result

    except Exception as e:
        log.exception("KI Orchestrator failed.")
        add_step("chatbot", "completed", "Es ist ein Fehler aufgetreten")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clears agent memory for a given session id (useful to start a new chat)."""
    try:
        clear_session_memory(session_id)
        return {"ok": True, "message": f"Session {session_id} cleared."}
    except Exception as e:
        log.exception(f"Failed to clear session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/session/new")
async def create_session():
    """Create a new session id (UUID) to start a fresh chat on the frontend."""
    try:
        session_id = str(uuid.uuid4())
        return {"ok": True, "session_id": session_id, "message": "New session created."}
    except Exception as e:
        log.exception(f"Failed to create new session: {e}")
        raise HTTPException(status_code=500, detail=str(e))