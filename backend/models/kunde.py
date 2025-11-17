from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Kunde(Base):
    __tablename__ = "kunde"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    telefon = Column(String(20))

    fahrzeuge = relationship("Fahrzeug", back_populates="kunde")
