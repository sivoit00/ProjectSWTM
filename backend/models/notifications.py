from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON
from datetime import datetime
from database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)               
    message = Column(String, nullable=False)             
    type = Column(String, nullable=False)                
    data = Column(JSON, nullable=True)                   
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, title={self.title})>"