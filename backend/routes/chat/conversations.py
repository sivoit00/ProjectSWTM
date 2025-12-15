from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models.chat_message import ChatMessage
from models.chat_conversation import ChatConversation
from schemas.chat_conversation_schema import ChatConversationResponse, ChatConversationRename

from .deps import get_db

router = APIRouter()


@router.get("/conversations/{user_id}", response_model=List[str])
def list_conversations(user_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(ChatMessage.conversation_id)
        .filter(ChatMessage.user_id == user_id)
        .distinct()
        .all()
    )
    return [r[0] for r in rows if r and r[0]]


@router.get("/conversations/{user_id}/details", response_model=List[ChatConversationResponse])
def list_conversation_details(user_id: str, db: Session = Depends(get_db)):
    
    rows = (
        db.query(ChatMessage.conversation_id)
        .filter(ChatMessage.user_id == user_id)
        .distinct()
        .all()
    )
    conv_ids = [r[0] for r in rows if r and r[0]]

    if conv_ids:
        existing = (
            db.query(ChatConversation.conversation_id)
            .filter(ChatConversation.user_id == user_id)
            .filter(ChatConversation.conversation_id.in_(conv_ids))
            .all()
        )
        existing_set = {r[0] for r in existing}
        missing = [cid for cid in conv_ids if cid not in existing_set]
        for cid in missing:
            db.add(ChatConversation(user_id=user_id, conversation_id=cid, title=None))
        if missing:
            db.commit()

    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )
    return conversations


@router.patch("/conversations/{user_id}/{conversation_id}", response_model=ChatConversationResponse)
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
        "ok": True,
        "deleted_messages": deleted_messages,
        "deleted_conversations": deleted_conversations,
    }
