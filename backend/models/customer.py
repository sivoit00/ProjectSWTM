from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship
import uuid

#def generate_customer_id():
#    return f"CUST-{uuid.uuid4().hex[:5].upper()}"

class Customer(Base):
    __tablename__ = "customer"

    #id = Column(String, unique=True, index=True, default=generate_customer_id)
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(String, index=True)
    firstName = Column(String(100))
    lastName = Column(String(100))
    username = Column(String(100))
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(200))
    postcode = Column(String(20))
    city = Column(String(100))

    vehicles = relationship("Vehicle", back_populates="customer")