from sqlalchemy import Column, Integer, String, ForeignKey, Date, Numeric
from sqlalchemy.orm import relationship
from database import Base
import datetime


# --- Tabelle: Kunde ---
class Kunde(Base):
    __tablename__ = "kunde"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    telefon = Column(String(20))

    # Beziehung zu Fahrzeug (1 Kunde kann viele Fahrzeuge haben)
    fahrzeuge = relationship("Fahrzeug", back_populates="kunde")


# --- Tabelle: Fahrzeug ---
class Fahrzeug(Base):
    __tablename__ = "fahrzeug"

    id = Column(Integer, primary_key=True, index=True)
    marke = Column(String(50))
    modell = Column(String(50))
    baujahr = Column(Integer)
    kunde_id = Column(Integer, ForeignKey("kunde.id"))

    # Beziehungen
    kunde = relationship("Kunde", back_populates="fahrzeuge")
    auftraege = relationship("Auftrag", back_populates="fahrzeug")


# --- Tabelle: Werkstatt ---
class Werkstatt(Base):
    __tablename__ = "werkstatt"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    adresse = Column(String(200))
    plz = Column(String(10))
    ort = Column(String(100))

    # Beziehung zu Auftrag (eine Werkstatt kann viele Aufträge haben)
    auftraege = relationship("Auftrag", back_populates="werkstatt")


# --- Tabelle: Auftrag ---
class Auftrag(Base):
    __tablename__ = "auftrag"

    id = Column(Integer, primary_key=True, index=True)
    beschreibung = Column(String(255))
    status = Column(String(50))
    erstellt_am = Column(Date)
    fahrzeug_id = Column(Integer, ForeignKey("fahrzeug.id"))
    werkstatt_id = Column(Integer, ForeignKey("werkstatt.id"))
    kosten = Column(Numeric(10, 2))

    # Beziehungen
    fahrzeug = relationship("Fahrzeug", back_populates="auftraege")
    werkstatt = relationship("Werkstatt", back_populates="auftraege")


# --- Tabelle: KIAktion ---
class KIAktion(Base):
    __tablename__ = "ki_aktionen"

    id = Column(Integer, primary_key=True, index=True)
    nachricht = Column(String)  # was der Kunde geschrieben hat
    antwort = Column(String)    # was die KI geantwortet hat
    erstellt_am = Column(Date, default=datetime.date.today)
    auftrag_id = Column(Integer, ForeignKey("auftrag.id"), nullable=True)

    auftrag = relationship("Auftrag") #hallo
