from pydantic import BaseModel


class CustomerBase(BaseModel):
    firstName: str
    lastName: str
    username: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str


class CustomerCreate(CustomerBase):
    pass


class Customer(CustomerBase):
    id: int
    user_id: str

    class Config:
        orm_mode = True
