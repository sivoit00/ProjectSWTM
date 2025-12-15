from pydantic import BaseModel

class RechtsanwaltBase(BaseModel):
    firstName: str
    lastName: str
    company: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str

class RechtsanwaltCreate(RechtsanwaltBase):
    pass

class Rechtsanwalt(RechtsanwaltBase):
    id: int

    class Config:
        orm_mode = True
