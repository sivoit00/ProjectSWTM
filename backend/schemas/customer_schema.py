from pydantic import BaseModel
from typing import Optional

class CustomerBase(BaseModel):
    email: str
    username: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    city: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    user_id: str

class Config:
    from_attributes = True