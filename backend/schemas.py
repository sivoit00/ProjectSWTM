from pydantic import BaseModel
from typing import Optional, List
from datetime import date

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
