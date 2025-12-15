from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChatMessageBase(BaseModel):
    sender: str  # "User" or "Bot"
    message: str
    conversation_id: Optional[str] = "default"

class ChatMessageCreate(ChatMessageBase):
    user_id: str

class ChatMessageResponse(ChatMessageBase):
    id: int
    user_id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total: int
