from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatConversationBase(BaseModel):
    conversation_id: str
    title: Optional[str] = None


class ChatConversationUpsert(ChatConversationBase):
    user_id: str


class ChatConversationRename(BaseModel):
    title: Optional[str] = None


class ChatConversationResponse(ChatConversationBase):
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
