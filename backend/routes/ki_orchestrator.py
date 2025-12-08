from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
import anyio
import logging
from typing import Optional, Dict, Any, List
from agents.ki_clone import route_message 
from agents.repair_chat_agent import clear_session_memory
from services.guardrails_service import validate_request
import uuid
from datetime import datetime, timezone
from auth.dependencies import get_optional_user

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

@router.post("/message")
async def ki_message(
    req: KIMessage,
    user_context: Optional[dict] = Depends(get_optional_user)
):
    log.info("KI-Orchestrator received message: %s", req.message)
    if not user_context:
        user_context = {"name": None, "email": None, "user_id": None}
    
    user_name = user_context.get("name") or "Your"
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
        
        if agent_changed:
            add_task("message_processing", "completed", 
                    "Agent handover completed", 
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
        
        for step in agent_steps:
            if step.get("status") == "working" and step.get("agent") != agent_type:
                step["status"] = "standby"
                agent_name = step.get("agent", "").lower()
                if "repair" in agent_name:
                    step["description"] = "Workshop agent on standby"
                elif "lawyer" in agent_name:
                    step["description"] = "Lawyer agent on standby"
                elif "insurance" in agent_name:
                    step["description"] = "Insurance agent on standby"
                elif "tom" in agent_name or "chatbot" in agent_name:
                    step["description"] = "Tom on standby"
        
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
                        f"{user_name}'s Agent taking over again", 
                        "chatbot",
                        "Ready for new requests")
                        
        if task_completed and agent_type != "chatbot":
            for step in agent_steps:
                if step.get("agent") == agent_type and step.get("status") == "working":
                    step["status"] = "standby"
                    if agent_type == "repair":
                        step["description"] = "Workshop search completed"
                        step["details"] = "All information provided"
                    elif agent_type == "lawyer":
                        step["description"] = "Legal consultation completed"
                        step["details"] = "Lawyer information provided"
                    elif agent_type == "insurance":
                        step["description"] = "Insurance review completed"
                        step["details"] = "Review successfully completed"
            
            tom_active = False
            for step in agent_steps:
                if step.get("agent") in ["chatbot", "Tom"] and step.get("status") == "working":
                    tom_active = True
                    break
            
            if not tom_active:
                add_task("tom_active", "working", 
                        f"{user_name}'s Agent taking over", 
                        "chatbot",
                        "Ready for your next request",
                        "task")
        
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