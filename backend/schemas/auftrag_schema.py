from pydantic import BaseModel
from typing import Optional
from datetime import date


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
