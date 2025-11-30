from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.sql import func
from database import Base


class DamageEvent(Base):
    __tablename__ = "DamageEvents"

    id = Column(Integer, primary_key=True, index=True)
    damage_event_id = Column(String, unique=True, index=True)  
    customer_id = Column(Integer, index=True)
    description = Column(Text)
    status = Column(String, default="submitted")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
