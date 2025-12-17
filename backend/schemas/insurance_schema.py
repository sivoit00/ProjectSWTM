from pydantic import BaseModel


class InsuranceBase(BaseModel):
    name: str
    number: str
    contact: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str


class InsuranceCreate(InsuranceBase):
    pass


class Insurance(InsuranceBase):
    id: int

    class Config:
        orm_mode = True
