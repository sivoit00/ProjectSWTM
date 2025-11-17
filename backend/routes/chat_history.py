from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from models.chat_message import ChatMessage
from schemas.chat_message_schema import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/save", response_model=ChatMessageResponse)
def save_chat_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    """Save a chat message to database"""
    db_message = ChatMessage(
        user_id=message.user_id,
        sender=message.sender,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

@router.get("/history/{user_id}", response_model=ChatHistoryResponse)
def get_chat_history(user_id: str, limit: int = 100, db: Session = Depends(get_db)):
    """Get chat history for a specific user"""
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.user_id == user_id)\
        .order_by(ChatMessage.timestamp.asc())\
        .limit(limit)\
        .all()
    
    return {
        "messages": messages,
        "total": len(messages)
    }

@router.delete("/history/{user_id}")
def clear_chat_history(user_id: str, db: Session = Depends(get_db)):
    """Clear all chat history for a user"""
    deleted = db.query(ChatMessage)\
        .filter(ChatMessage.user_id == user_id)\
        .delete()
    db.commit()
    return {"deleted": deleted, "message": "Chat history cleared"}
