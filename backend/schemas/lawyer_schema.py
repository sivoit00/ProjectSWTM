from pydantic import BaseModel

class LawyerBase(BaseModel):
    firstName: str
    lastName: str
    company: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str

class LawyerCreate(LawyerBase):
    pass

class Lawyer(LawyerBase):
    id: int

    class Config:
        orm_mode = True
