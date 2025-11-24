from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
import anyio
import logging
from typing import Optional, Dict, Any
from jose import jwt
from agents.kiClone import route_message 

router = APIRouter()
log = logging.getLogger(__name__)

class KIMessage(BaseModel):
    message: str

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
    
    if user_context['name']:
        log.info(f"User erkannt: {user_context['name']}")

    try:
        result = await anyio.to_thread.run_sync(
            route_message, 
            req.message, 
            user_context
        )

        if not isinstance(result, dict):
            raise ValueError("route_message returned invalid format")

        return result

    except Exception as e:
        log.exception("KI Orchestrator failed.")
        raise HTTPException(status_code=500, detail=str(e))