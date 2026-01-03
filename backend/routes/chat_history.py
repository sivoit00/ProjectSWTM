from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models.chat_message import ChatMessage
from models.chat_conversation import ChatConversation
from schemas.chat_message_schema import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse
from schemas.chat_conversation_schema import ChatConversationResponse, ChatConversationRename

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/chat", tags=["chat"])


def _get_or_create_conversation(db: Session, user_id: str, conversation_id: str) -> ChatConversation:
    conv = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .filter(ChatConversation.conversation_id == conversation_id)
        .first()
    )
    if conv:
        return conv

    conv = ChatConversation(
        user_id=user_id,
        conversation_id=conversation_id,
        title=None,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def _touch_conversation(db: Session, user_id: str, conversation_id: str) -> None:
    conv = _get_or_create_conversation(db, user_id, conversation_id)
    conv.updated_at = datetime.utcnow()
    db.commit()

@router.post("/save", response_model=ChatMessageResponse)
def save_chat_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    """Save a chat message to database"""
    conversation_id = message.conversation_id or "default"

    db_message = ChatMessage(
        user_id=message.user_id,
        conversation_id=conversation_id,
        sender=message.sender,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    _touch_conversation(db, message.user_id, conversation_id)
    return db_message

@router.get("/history/{user_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    user_id: str,
    limit: int = 100,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get chat history for a specific user"""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if conversation_id:
        query = query.filter(ChatMessage.conversation_id == conversation_id)

    messages = (
        query.order_by(ChatMessage.timestamp.asc())
        .limit(limit)
        .all()
    )
    
    return {
        "messages": messages,
        "total": len(messages)
    }

@router.delete("/history/{user_id}")
def clear_chat_history(
    user_id: str,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Clear chat history for a user (optionally scoped to one conversation)."""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if conversation_id:
        query = query.filter(ChatMessage.conversation_id == conversation_id)

    deleted = query.delete()
    db.commit()
    return {"deleted": deleted, "message": "Chat history cleared"}


@router.get(
    "/conversations/{user_id}/details",
    response_model=List[ChatConversationResponse],
)
def list_conversations(user_id: str, db: Session = Depends(get_db)):
    """Return known conversations for a user.

    Also backfills ChatConversation rows for any conversation_ids that exist in chat_messages.
    """
    conv_ids = [
        row[0]
        for row in (
            db.query(ChatMessage.conversation_id)
            .filter(ChatMessage.user_id == user_id)
            .distinct()
            .all()
        )
        if row[0]
    ]

    for cid in conv_ids:
        _get_or_create_conversation(db, user_id, cid)

    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )
    return conversations


@router.patch(
    "/conversations/{user_id}/{conversation_id}",
    response_model=ChatConversationResponse,
)
def rename_conversation(
    user_id: str,
    conversation_id: str,
    payload: ChatConversationRename,
    db: Session = Depends(get_db),
):
    conv = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .filter(ChatConversation.conversation_id == conversation_id)
        .first()
    )
    if not conv:
        conv = ChatConversation(user_id=user_id, conversation_id=conversation_id, title=None)
        db.add(conv)

    conv.title = payload.title
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conv)
    return conv


@router.delete("/conversations/{user_id}/{conversation_id}")
def delete_conversation(user_id: str, conversation_id: str, db: Session = Depends(get_db)):
    deleted_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .filter(ChatMessage.conversation_id == conversation_id)
        .delete()
    )

    deleted_conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .filter(ChatConversation.conversation_id == conversation_id)
        .delete()
    )

    db.commit()
    return {
        "deleted_messages": deleted_messages,
        "deleted_conversations": deleted_conversations,
    }
