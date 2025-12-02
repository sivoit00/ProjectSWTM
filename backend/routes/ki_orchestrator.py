from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import anyio
import logging
from typing import Optional, Dict, Any, List
from jose import jwt
from agents.ki_clone import route_message 
from agents.repair_chat_agent import clear_session_memory
from services.guardrails_service import validate_request
import uuid
from datetime import datetime, timezone

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
            "timestamp": datetime.now(timezone.utc).isoformat(),
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
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "description": description,
            "event_type": event_type
        })
    
    if user_context['name']:
        log.info(f"User erkannt: {user_context['name']}")

    add_step("guardrails", "active", "Überprüfe Nachricht auf Sicherheit...", "internal")
    validation_result = validate_request(req.message, user_context)
    
    if not validation_result["valid"]:
        add_step("guardrails", "completed", "Nachricht wurde blockiert", "internal")
        
        user_message = "⚠️ Diese Anfrage kann nicht weitergeführt werden. Bitte senden Sie eine neue Nachricht."
        
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

    # include session_id from body (if provided) into user_context so agents can use per-session memory
    if getattr(req, 'session_id', None):
        user_context['session_id'] = req.session_id

    try:
        add_task("message_processing", "working", 
                "Processing your request...", 
                "Tom",
                filtered_message[:50] + "..." if len(filtered_message) > 50 else filtered_message,
                "task")
        
        result = await anyio.to_thread.run_sync(
            route_message,
            filtered_message,
            user_context,
        )

        if not isinstance(result, dict):
            raise ValueError("route_message returned invalid format")

        agent_type = result.get("agent", "chatbot")
        agent_changed = result.get("agent_changed", False)
        
        # Handle response - kann string oder dict sein
        response_raw = result.get("response", "")
        if isinstance(response_raw, dict):
            bot_response = str(response_raw.get("response", response_raw.get("output", ""))).lower()
        else:
            bot_response = str(response_raw).lower()
        
        add_task("message_processing", "completed", 
                "Response ready", 
                agent_type,
                "Processing completed",
                "task")
        
        completion_keywords = [
            "gern geschehen", "viel erfolg", "weitere fragen", 
            "weitere hilfe", "ich zu kontaktieren", "zögern sie nicht",
            "stehe ich ihnen", "jederzeit zur verfügung", "kann ich ihnen",
            "alles klar", "kein problem", "hoffe", "helfen",
            "noch etwas", "sonst noch", "für dich tun", "unterstützen"
        ]
        task_completed = any(keyword in bot_response for keyword in completion_keywords)
        
       
        # Setze ALLE vorherigen working Tasks auf completed, außer vom aktuellen Agent
        for step in agent_steps:
            if step.get("status") == "working" and step.get("agent") != agent_type:
                step["status"] = "completed"
                # Update description
                agent_name = step.get("agent", "").lower()
                if "repair" in agent_name:
                    step["description"] = "Workshop search completed"
                elif "lawyer" in agent_name:
                    step["description"] = "Legal consultation completed"
                elif "insurance" in agent_name:
                    step["description"] = "Insurance review completed"
        
        if agent_changed:
            existing_tasks = [step.get("task") for step in agent_steps]
            
            if agent_type == "repair" and "werkstatt_suche" not in existing_tasks:
                add_task("werkstatt_suche", "working", 
                        "Repair Agent taking over", 
                        "repair",
                        "Searching for suitable workshops near you")
            elif agent_type == "lawyer" and "anwalt_suche" not in existing_tasks:
                add_task("anwalt_suche", "working", 
                        "Lawyer Agent taking over", 
                        "lawyer",
                        "Searching for qualified lawyers for legal advice")
            elif agent_type == "insurance" and "versicherung_pruefung" not in existing_tasks:
                add_task("versicherung_pruefung", "working", 
                        "Insurance Agent taking over", 
                        "insurance",
                        "Reviewing your insurance matter")
            elif agent_type == "chatbot" and "tom_uebernimmt" not in existing_tasks:
                add_task("tom_uebernimmt", "completed", 
                        "Tom taking over again", 
                        "Tom",
                        "Ready for new requests")
                        
        # Wenn Task abgeschlossen ist, setze working Tasks auf completed
        if task_completed and agent_type != "chatbot":
            # Finde den working Task des aktuellen Agenten und setze auf completed
            for step in agent_steps:
                if step.get("agent") == agent_type and step.get("status") == "working":
                    step["status"] = "completed"
                    # Update description für abgeschlossene Tasks
                    if agent_type == "repair":
                        step["description"] = "Werkstatt-Suche abgeschlossen"
                        step["details"] = "Alle Informationen bereitgestellt"
                    elif agent_type == "lawyer":
                        step["description"] = "Rechtsberatung abgeschlossen"
                        step["details"] = "Anwaltsinformationen bereitgestellt"
                    elif agent_type == "insurance":
                        step["description"] = "Versicherungsprüfung abgeschlossen"
                        step["details"] = "Prüfung erfolgreich durchgeführt"
        
        # Stelle sicher, dass response ein String ist
        if isinstance(result.get("response"), dict):
            result["response"] = result["response"].get("response", result["response"].get("output", str(result["response"])))
        
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