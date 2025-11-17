from pydantic import BaseModel


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
