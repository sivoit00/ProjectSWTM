from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, Float
from sqlalchemy.sql import func
from database import Base
import uuid

def generate_claim_id():
    return f"CLM-{uuid.uuid4().hex[:10].upper()}"

class DamageEvent(Base):
    __tablename__ = "damage_event"

    id = Column(Integer, primary_key=True, index=True)

    
    damage_event_id = Column(String, unique=True, index=True, default=generate_claim_id)

    
    customer_id = Column(String, index=True)
    description = Column(Text)
    status = Column(String, default="submitted")

    
    damage_type = Column(String)
    damage_date = Column(String)
    damage_location = Column(String)

    vehicle = Column(Text)  

    police_involved = Column(Boolean)
    third_party_involved = Column(Boolean)
    estimated_damage = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
