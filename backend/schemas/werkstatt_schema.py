from pydantic import BaseModel


class WerkstattBase(BaseModel):
    name: str
    adresse: str
    plz: str
    ort: str


class WerkstattCreate(WerkstattBase):
    pass


class Werkstatt(WerkstattBase):
    id: int

    class Config:
        orm_mode = True
