from pydantic import BaseModel


class FahrzeugBase(BaseModel):
    brand: str
    model: str
    year: int
    numberplate: str


class FahrzeugCreate(FahrzeugBase):
    pass


class Fahrzeug(FahrzeugBase):
    id: int

    class Config:
        from_attributes = True
