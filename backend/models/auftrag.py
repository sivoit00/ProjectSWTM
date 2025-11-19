from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from database import Base


class Auftrag(Base):
    __tablename__ = "auftrag"

    id = Column(Integer, primary_key=True, index=True)
    beschreibung = Column(String(255))
    status = Column(String(50))
    erstellt_am = Column(Date)
    fahrzeug_id = Column(Integer, ForeignKey("fahrzeug.id"))
    werkstatt_id = Column(Integer, ForeignKey("werkstatt.id"))
    kosten = Column(Numeric(10, 2))

    fahrzeug = relationship("Fahrzeug", back_populates="auftraege")
    werkstatt = relationship("Werkstatt", back_populates="auftraege")
