from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String, index=True, nullable=False)
    conversation_id = Column(String, index=True, nullable=False, unique=True)

    title = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (
            f"<ChatConversation(user_id={self.user_id}, conversation_id={self.conversation_id}, "
            f"title={self.title})>"
        )
