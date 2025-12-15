from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Fahrzeug(Base):
    __tablename__ = "fahrzeug"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(50))
    model = Column(String(50))
    year = Column(Integer)
    numberplate = Column(String(50))
    kunde_id = Column(Integer, ForeignKey("kunde.id"))

    kunde = relationship("Kunde", back_populates="fahrzeuge")
    auftraege = relationship("Auftrag", back_populates="fahrzeug")
