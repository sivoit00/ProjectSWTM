from pydantic import BaseModel


class WorkshopBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str


class WorkshopCreate(WorkshopBase):
    pass


class Workshop(workshopBase):
    id: int

    class Config:
        from_attributes = True
