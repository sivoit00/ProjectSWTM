from pydantic import BaseModel


class VersicherungBase(BaseModel):
    name: str
    number: str
    contact: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str


class VersicherungCreate(VersicherungBase):
    pass


class Versicherung(VersicherungBase):
    id: int

    class Config:
        orm_mode = True
