from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Fahrzeug(Base):
    __tablename__ = "fahrzeug"

    id = Column(String(200), primary_key=True, index=True)
    marke = Column(String(50))
    modell = Column(String(50))
    baujahr = Column(Integer)
    kunde_id = Column(String(200), ForeignKey("kunde.id"))

    kunde = relationship("Kunde", back_populates="fahrzeuge")
    auftraege = relationship("Auftrag", back_populates="fahrzeug")
