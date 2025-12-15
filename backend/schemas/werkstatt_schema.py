from pydantic import BaseModel


class WerkstattBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    postcode: str
    city: str


class WerkstattCreate(WerkstattBase):
    pass


class Werkstatt(WerkstattBase):
    id: int

    class Config:
        from_attributes = True
