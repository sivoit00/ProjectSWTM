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
    
    agent_steps: List[Dict[str, Any]] = []
    
    def add_task(task: str, status: str, description: str, agent: str = None, details: str = None, event_type: str = "task"):
        """Add a task event to timeline"""
        agent_steps.append({
            "task": task,  
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "description": description,  
            "details": details,  
            "agent": agent,  
            "event_type": event_type
        })
    
    def add_step(agent: str, status: str, description: str, event_type: str = "internal"):
        """Legacy function for backward compatibility"""
        agent_steps.append({
            "task": "internal",
            "agent": agent,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
            "description": description,
            "event_type": event_type
        })
    
    if user_context['name']:
        log.info(f"User erkannt: {user_context['name']}")

    add_step("guardrails", "active", "Überprüfe Nachricht auf Sicherheit...", "internal")
    validation_result = validate_request(req.message, user_context)
    
    if not validation_result["valid"]:
        severity = validation_result.get("severity", "MEDIUM")
        add_step("guardrails", "completed", "Nachricht wurde blockiert", "internal")
        
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
    
    add_step("guardrails", "completed", "Nachricht ist sicher", "internal")
    
    filtered_message = validation_result["filtered_input"]
    
    if validation_result.get("warnings"):
        log.info(f"Guardrails warnings for user {user_context.get('name', 'Unknown')}: {validation_result['warnings']}")

    if getattr(req, 'session_id', None):
        user_context['session_id'] = req.session_id

    try:
        result = await anyio.to_thread.run_sync(
            route_message,
            filtered_message, 
            user_context,
        )

        if not isinstance(result, dict):
            raise ValueError("route_message returned invalid format")

        agent_type = result.get("agent", "chatbot")
        agent_changed = result.get("agent_changed", False)
        bot_response = result.get("response", "").lower()
        
        completion_keywords = [
            "gern geschehen", "viel erfolg", "weitere fragen", 
            "weitere hilfe", "ich zu kontaktieren", "zögern sie nicht",
            "stehe ich ihnen", "jederzeit zur verfügung", "kann ich ihnen"
        ]
        task_completed = any(keyword in bot_response for keyword in completion_keywords)
        
       
        if agent_changed or (agent_type != "chatbot" and not task_completed):
           
            existing_tasks = [step.get("task") for step in agent_steps]
            
            if agent_type == "repair" and "werkstatt_suche" not in existing_tasks:
                add_task("werkstatt_suche", "working", 
                        "Werkstatt Agent übernimmt", 
                        agent_type,
                        "Suche nach passenden Werkstätten in Ihrer Nähe")
            elif agent_type == "lawyer" and "anwalt_suche" not in existing_tasks:
                add_task("anwalt_suche", "working", 
                        "Lawyer Agent übernimmt", 
                        agent_type,
                        "Suche nach qualifizierten Anwälten für rechtliche Beratung")
            elif agent_type == "insurance" and "versicherung_pruefung" not in existing_tasks:
                add_task("versicherung_pruefung", "working", 
                        "Insurance Agent übernimmt", 
                        agent_type,
                        "Prüfung Ihrer Versicherungsangelegenheit")
        if task_completed and agent_type != "chatbot":
            if agent_type == "repair":
                add_task("werkstatt_suche", "completed", 
                        "Werkstatt-Suche abgeschlossen", 
                        agent_type,
                        "Alle Informationen bereitgestellt")
            elif agent_type == "lawyer":
                add_task("anwalt_suche", "completed", 
                        "Rechtsberatung abgeschlossen", 
                        agent_type,
                        "Anwaltsinformationen bereitgestellt")
            elif agent_type == "insurance":
                add_task("versicherung_pruefung", "completed", 
                        "Versicherungsprüfung abgeschlossen", 
                        agent_type,
                        "Prüfung erfolgreich durchgeführt")
            
            add_task("return_to_tom", "completed", 
                    "Tom übernimmt wieder", 
                    "chatbot",
                    "Bereit für neue Anfragen")
        
        result["agent_steps"] = agent_steps
        return result

    except Exception as e:
        log.exception("KI Orchestrator failed.")
        add_step("chatbot", "completed", "Es ist ein Fehler aufgetreten", "agent_message")
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