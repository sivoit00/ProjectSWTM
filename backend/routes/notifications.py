from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.notifications import Notification 
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

router = APIRouter()

class NotificationOut(BaseModel):
    id: int
    title: str
    message: str
    type: str
    data: Optional[Any] = None
    created_at: datetime
    is_read: bool

    class Config:
        from_attributes = True

@router.get("/unread/{user_id}", response_model=list[NotificationOut])
def get_unread_notifications(user_id: str, db: Session = Depends(get_db)):
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False
    ).order_by(Notification.created_at.desc()).all()

@router.post("/mark-read/{notification_id}")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if notif:
        notif.is_read = True
        db.commit()
        return {"ok": True}
    raise HTTPException(status_code=404, detail="Notification not found")