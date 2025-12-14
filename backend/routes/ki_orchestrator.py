from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import anyio
import logging
import asyncio
from typing import Optional, Dict, Any, List
import uuid
from datetime import datetime, timezone
from agents.ki_clone import route_message
from agents.repair_chat_agent import clear_session_memory
from services.guardrails_service import validate_request
from services.sse_emitter import SSEEmitter
from auth.dependencies import get_optional_user

router = APIRouter()
log = logging.getLogger(__name__)

class KIMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

def get_utc_now():
    return datetime.now(timezone.utc).isoformat()

@router.post("/stream")
async def stream_ki(
    req: KIMessage,
    user_context: Optional[dict] = Depends(get_optional_user)
):
    """
    Zentraler KI-Endpunkt mit Streaming-Response.
    Verarbeitet Guardrails, KI-Routing und sendet Antwort stückweise zurück.
    """
    if not user_context:
        user_context = {"name": None, "email": None, "user_id": None}

    emitter = SSEEmitter()
    agent_steps: List[Dict[str, Any]] = []

    async def add_step(
        *,
        agent: str,
        status: str,
        description: str,
        task: str = "internal",
        details: Optional[str] = None,
        event_type: str = "agent_step",
    ):
        step = {
            "task": task,
            "agent": agent,
            "timestamp": get_utc_now(),
            "status": status,
            "description": description,
            "details": details,
            "event_type": event_type,
        }
        agent_steps.append(step)

    async def producer():
        try:
            log.info(f"KI Stream Anfrage: {req.message[:50]}...")

            await add_step(agent="guardrails", status="active", description="Prüfe Sicherheit...")
            
            validation_result = validate_request(req.message, user_context)

            if not validation_result["valid"]:
                await add_step(agent="guardrails", status="completed", description="Blockiert")
                await emitter.send("final", {
                    "ok": False,
                    "blocked": True,
                    "response": "⚠️ Diese Anfrage wurde von den Sicherheitsrichtlinien blockiert.",
                    "agent": "guardrails",
                    "agent_steps": agent_steps
                })
                return

            await add_step(agent="guardrails", status="completed", description="Sicher")
            filtered_message = validation_result["filtered_input"]

            if req.session_id:
                user_context["session_id"] = req.session_id

            await add_step(
                task="processing",
                agent="Orchestrator",
                status="working",
                description="Verarbeite Anfrage...",
                details=filtered_message
            )

            result = await anyio.to_thread.run_sync(
                route_message,
                filtered_message,
                user_context
            )

            if not isinstance(result, dict):
                raise ValueError("Ungültiges Ergebnis von route_message")

            agent_type = result.get("agent", "chatbot")
            agent_changed = result.get("agent_changed", False)
            
            response_raw = result.get("response", result.get("output", ""))
            response_text = str(response_raw)

            if agent_changed:
                await add_step(agent=agent_type, status="completed", description="Agent gewechselt")
            
            words = response_text.split(" ")
            for i, word in enumerate(words):
                delta = word + (" " if i < len(words) - 1 else "")
                
                payload = {
                    "delta": delta,
                    "agent": agent_type,
                    "agent_changed": agent_changed if i == 0 else False
                }
                
                await emitter.send("message", payload)
                await asyncio.sleep(0.02) 

            await emitter.send("final", {
                "ok": True,
                "response": response_text,
                "agent": agent_type,
                "agent_steps": agent_steps
            })

        except Exception as e:
            log.exception("KI Stream Fehler")
            await emitter.send("error", {"message": str(e)})
        finally:
            await emitter.close()

    asyncio.create_task(producer())

    return StreamingResponse(
        emitter.stream(),
        media_type="text/event-stream"
    )

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    try:
        clear_session_memory(session_id)
        return {"ok": True, "message": f"Session {session_id} gelöscht."}
    except Exception as e:
        log.exception(f"Fehler beim Löschen von Session {session_id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/new")
async def create_session():
    try:
        session_id = str(uuid.uuid4())
        return {
            "ok": True,
            "session_id": session_id,
            "message": "Neue Session erstellt."
        }
    except Exception as e:
        log.exception("Fehler beim Erstellen einer neuen Session")
        raise HTTPException(status_code=500, detail=str(e))