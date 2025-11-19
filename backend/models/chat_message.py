from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)  # Keycloak user ID
    sender = Column(String, nullable=False)  # "User" or "Bot"
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<ChatMessage(user_id={self.user_id}, sender={self.sender})>"
