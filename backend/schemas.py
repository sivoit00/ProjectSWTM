from pydantic import BaseModel
from typing import Optional, List
from datetime import date

# ------------------- KUNDE -------------------
class KundeBase(BaseModel):
    name: str
    email: str
    telefon: str


class KundeCreate(KundeBase):
    pass


class Kunde(KundeBase):
    id: int

    class Config:
        orm_mode = True


# ------------------- FAHRZEUG -------------------
class FahrzeugBase(BaseModel):
    marke: str
    modell: str
    baujahr: int
    kunde_id: int


class FahrzeugCreate(FahrzeugBase):
    pass


class Fahrzeug(FahrzeugBase):
    id: int

    class Config:
        orm_mode = True


# ------------------- WERKSTATT -------------------
class WerkstattBase(BaseModel):
    name: str
    adresse: str
    plz: str
    ort: str


class WerkstattCreate(WerkstattBase):
    pass


class Werkstatt(WerkstattBase):
    id: int

    class Config:
        orm_mode = True


# ------------------- AUFTRAG -------------------
class AuftragBase(BaseModel):
    beschreibung: str
    status: str
    fahrzeug_id: int
    werkstatt_id: int
    erstellt_am: Optional[date] = None


class AuftragCreate(AuftragBase):
    pass


class Auftrag(AuftragBase):
    id: int

    class Config:
        orm_mode = True


# ------------------- KI-AKTION -------------------
class KIAktionCreate(BaseModel):
    nachricht: str
    werkstatt_id: Optional[int] = None
    fahrzeug_id: Optional[int] = None
    kunde_id: Optional[int] = None


class KIAktionSchema(BaseModel):
    id: int
    nachricht: str
    antwort: str
    erstellt_am: Optional[date]
    auftrag_id: Optional[int]

    class Config:
        orm_mode = True


# ------------------- RECHTSANWALT -------------------
class RechtsanwaltBase(BaseModel):
    name: str
    kanzlei: str
    adresse: str
    plz: str
    ort: str
    telefon: str
    email: str


class RechtsanwaltCreate(RechtsanwaltBase):
    pass


class Rechtsanwalt(RechtsanwaltBase):
    id: int

    class Config:
        orm_mode = True


# ------------------- VERSICHERUNG -------------------
class VersicherungBase(BaseModel):
    versicherungsname: str
    versicherungsnummer: str
    art: str
    ansprechpartner: str
    telefon: str
    email: str


class VersicherungCreate(VersicherungBase):
    pass


class Versicherung(VersicherungBase):
    id: int

    class Config:
        orm_mode = True
