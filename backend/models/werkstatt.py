from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Werkstatt(Base):
    __tablename__ = "werkstatt"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    adresse = Column(String(200))
    plz = Column(String(20))
    ort = Column(String(100))

    auftraege = relationship("Auftrag", back_populates="werkstatt")
