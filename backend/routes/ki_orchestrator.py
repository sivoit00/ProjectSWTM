from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import anyio
import logging
from agents.kiClone import route_message

router = APIRouter()
log = logging.getLogger(__name__)


class KIMessage(BaseModel):
    message: str


@router.post("/message")
async def ki_message(req: KIMessage):
    log.info("KI-Orchestrator received message: %s", req.message)

    try:
        # route_message ist synchron → Threadpool
        result = await anyio.to_thread.run_sync(route_message, req.message)

        if not isinstance(result, dict):
            raise ValueError("route_message returned invalid format")

        return result

    except Exception as e:
        log.exception("KI Orchestrator failed.")
        raise HTTPException(status_code=500, detail=str(e))
