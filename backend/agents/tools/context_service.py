from sqlalchemy.orm import Session
from database import SessionLocal
from sqlalchemy import or_
from models.customer import Customer
from models.vehicle import Vehicle
from models.insurance import Insurance
from models.workshop import Workshop
from models.lawyer import Lawyer

def get_complete_user_context(identifier: str) -> dict:
    db = SessionLocal()
    try:

        customer = db.query(Customer).filter(
            or_(
                Customer.id == (int(identifier) if identifier.isdigit() else -1),
                Customer.email.ilike(identifier),
                Customer.user_id == identifier
            )
        ).first()

        if not customer:
            return {"error": "User not found", "logged_in": False}


        vehicles = db.query(Vehicle).filter_by(customer_id=customer.id).all()
        insurance = db.query(Insurance).filter_by(customer_id=customer.id).first()
        workshop = db.query(Workshop).filter_by(customer_id=customer.id).first()
        lawyer = db.query(Lawyer).filter_by(customer_id=customer.id).first()

        context = {
            "logged_in": True,
            "customer": {
                "id": customer.id,
                "full_name": f"{customer.firstName} {customer.lastName}",
                "email": customer.email,
                "phone": customer.phone,
                "address": f"{customer.address}, {customer.postcode} {customer.city}"
            },
            "vehicles": [
                {"brand": v.brand, "model": v.model, "year": v.year, "plate": v.numberplate}
                for v in vehicles   
            ],
            "insurance": {
                "provider": insurance.name,
                "policy_number": insurance.number,
                "contact_person": insurance.contact,
                "phone": insurance.phone,
                "email": insurance.email,
                "address": f"{insurance.address}, {insurance.postcode} {insurance.city}"
            } if insurance else None,
            "preferred_workshop": {
                "name": workshop.name,
                "city": workshop.city,
                "phone": workshop.phone,
                "address": f"{workshop.address}, {workshop.postcode} {workshop.city}",
                "email": workshop.email
            } if workshop else None,
            "assigned_lawyer": {
                "name": f"{lawyer.firstName} {lawyer.lastName}",
                "company": lawyer.company,
                "phone": lawyer.phone,
                "adress": f"{lawyer.address}, {lawyer.postcode} {lawyer.city}",
                "email": lawyer.email
            } if lawyer else None
        }
        return context

    except Exception as e:
        return {"error": str(e), "logged_in": False}
    finally:
        db.close()