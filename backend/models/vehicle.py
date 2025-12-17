from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Vehicle(Base):
    __tablename__ = "vehicle"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    numberplate = Column(String(50))
    customer_id = Column(Integer, ForeignKey("customer.id"))

    customer = relationship("Customer", back_populates="vehicles")