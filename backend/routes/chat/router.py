from fastapi import APIRouter

from . import messages, conversations

router = APIRouter(prefix="/chat", tags=["chat"])
router.include_router(messages.router)
router.include_router(conversations.router)
