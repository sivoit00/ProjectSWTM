from sqlalchemy import Column, Integer, String
from database import Base
from sqlalchemy.orm import relationship



class Kunde(Base):
    __tablename__ = "kunde"

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

    fahrzeuge = relationship("Fahrzeug", back_populates="kunde")