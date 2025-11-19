from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from database import Base
import datetime


class KIAktion(Base):
    __tablename__ = "ki_aktionen"

    id = Column(Integer, primary_key=True, index=True)
    nachricht = Column(String)
    antwort = Column(String)
    erstellt_am = Column(Date, default=datetime.date.today)
    auftrag_id = Column(Integer, ForeignKey("auftrag.id"), nullable=True)

    auftrag = relationship("Auftrag")
