from pydantic import BaseModel


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
