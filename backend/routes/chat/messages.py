from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from models.chat_message import ChatMessage
from models.chat_conversation import ChatConversation
from schemas.chat_message_schema import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse

from .deps import get_db

router = APIRouter()


@router.post("/save", response_model=ChatMessageResponse)
def save_chat_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    conv_id = (getattr(message, "conversation_id", None) or "default")

    existing_conv = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == message.user_id)
        .filter(ChatConversation.conversation_id == conv_id)
        .first()
    )
    if not existing_conv:
        db.add(ChatConversation(user_id=message.user_id, conversation_id=conv_id, title=None))
    else:
        existing_conv.updated_at = datetime.utcnow()

    db_message = ChatMessage(
        user_id=message.user_id,
        conversation_id=conv_id,
        sender=message.sender,
        message=message.message,
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


@router.get("/history/{user_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    user_id: str,
    conversation_id: Optional[str] = Query(default=None),
    limit: int = 100,
    db: Session = Depends(get_db),
):
    q = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if conversation_id:
        q = q.filter(ChatMessage.conversation_id == conversation_id)

    messages = q.order_by(ChatMessage.timestamp.asc()).limit(limit).all()

    return {"messages": messages, "total": len(messages)}


@router.delete("/history/{user_id}")
def clear_chat_history(
    user_id: str,
    conversation_id: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if conversation_id:
        q = q.filter(ChatMessage.conversation_id == conversation_id)

    deleted = q.delete()
    db.commit()
    return {"deleted": deleted, "message": "Chat history cleared"}
