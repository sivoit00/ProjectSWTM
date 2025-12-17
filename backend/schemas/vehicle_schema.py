from pydantic import BaseModel


class VehicleBase(BaseModel):
    brand: str
    model: str
    year: int
    numberplate: str


class VehicleCreate(VehicleBase):
    pass


class Vehicle(VehicleBase):
    id: int

    class Config:
        from_attributes = True
