from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ChatConversationResponse(BaseModel):
    user_id: str
    conversation_id: str
    title: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatConversationRename(BaseModel):
    title: Optional[str] = None
