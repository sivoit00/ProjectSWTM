from .customer_schema import CustomerBase, CustomerCreate, Customer
from .vehicle_schema import VehicleBase, VehicleCreate, Vehicle
from .workshop_schema import WorkshopBase, WorkshopCreate, Workshop
from .lawyer_schema import Lawyer, LawyerCreate, LawyerBase
from .insurance_schema import Insurance, InsuranceCreate, InsuranceBase

__all__ = [
    "CustomerBase", "CustomerCreate", "Customer",
    "VehicleBase", "VehicleCreate", "Vehicle",
    "WorkshopBase", "WorkshopCreate", "Workshop",
    "Lawyer", "LawyerCreate", "LawyerBase",
    "Insurance", "InsuranceCreate", "InsuranceBase"
]
