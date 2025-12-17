from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Workshop(Base):
    __tablename__ = "workshop"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"))

    name = Column(String(100))
    email = Column(String(100))
    phone = Column(String(50))
    address = Column(String(200))
    postcode = Column(String(20))
    city = Column(String(100))
