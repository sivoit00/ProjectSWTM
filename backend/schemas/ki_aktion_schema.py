from pydantic import BaseModel
from typing import Optional
from datetime import date


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
