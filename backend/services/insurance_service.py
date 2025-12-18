import json
from typing import Any, Dict, Optional
from database import SessionLocal
from models.damage_event import DamageEvent
from models.customer import Customer
from models.vehicle import Vehicle
from models.insurance import Insurance

def get_policy_details(customer_id: str) -> Dict[str, Any]:
    """
    Placeholder: Gibt Fake-Daten zurück, bis ein Policy-Modell existiert.
    """
    return {
        "customer_id": customer_id,
        "policy_id": f"POL-{customer_id}",
        "coverage": {"liability": True, "collision": False, "theft": True},
        "status": "active"
    }


def calculate_premium(vehicle_data: Any) -> Dict[str, Any]:
    if isinstance(vehicle_data, str):
        try:
            vehicle = json.loads(vehicle_data)
        except Exception:
            vehicle = {}
    else:
        vehicle = vehicle_data or {}

    base = 200.0
    year = int(vehicle.get("year", 2020))
    age = 2025 - year
    premium = base + age * 10

    if vehicle.get("value"):
        premium += float(vehicle["value"]) * 0.01

    return {
        "estimated_premium": round(premium, 2),
        "currency": "EUR",
        "calculator_version": "v1.0"
    }


def submit_claim(claim_data: dict) -> dict:
    db = SessionLocal()
    try:
        event = DamageEvent(
            customer_id=claim_data.get("customer_id"),
            description=claim_data.get("description"),
            damage_type=claim_data.get("damage_type"),
            damage_date=claim_data.get("damage_date"),
            damage_location=claim_data.get("damage_location"),
            vehicle=json.dumps(claim_data.get("vehicle")) if claim_data.get("vehicle") else None,
            police_involved=claim_data.get("police_involved"),
            third_party_involved=claim_data.get("third_party_involved"),
            estimated_damage=claim_data.get("estimated_damage"),
            status="submitted"
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return {
            "completed": True,
            "claim_id": event.damage_event_id,
            "location": event.damage_location,
            "vehicle": claim_data.get("vehicle"),
            "description": claim_data.get("description")
        }

    except Exception as e:
        db.rollback()
        return {
            "error": str(e),
            "note": "Could not store DamageEvent in database"
        }

    finally:
        db.close()


def get_claim_status(claim_id: str) -> dict:
    db = SessionLocal()
    try:
        event = db.query(DamageEvent).filter_by(damage_event_id=claim_id).first()

        if not event:
            return {
                "claim_id": claim_id,
                "status": "unknown",
                "note": "DamageEvent not found"
            }

        return {
            "claim_id": event.damage_event_id,
            "status": event.status,
            "note": ""
        }

    finally:
        db.close()

def get_user_context(identifier: str) -> Dict[str, Any]:
    db = SessionLocal()
    context: Dict[str, Any] = {
        "customer_id": None,
        "customer_name": None,
        "customer_email": None,
        "customer_phone": None,
        "vehicle": None,
        "insurance": {
            "name": None, "email": None, "phone": None,
            "postcode": None, "city": None
        }
    }
    try:
        customer = None
        if "@" in identifier:
            customer = db.query(Customer).filter(Customer.email == identifier).first()
        elif len(identifier) > 10: 
            customer = db.query(Customer).filter(Customer.user_id == identifier).first()
        elif identifier.isdigit():
            customer = db.query(Customer).filter(Customer.id == int(identifier)).first()

        if customer:
            context["customer_id"] = customer.id
            context["customer_name"] = f"{customer.firstName} {customer.lastName}".strip()
            context["customer_email"] = customer.email
            context["customer_phone"] = customer.phone
            
            if customer.vehicles:
                f = customer.vehicles[0]
                context["vehicle"] = f"{f.brand} {f.model} ({f.year})"

            insurance = db.query(Insurance).filter_by(customer_id=customer.id).first()
            if insurance:
                context["insurance"] = {
                    "name": insurance.name,
                    "email": insurance.email,
                    "phone": insurance.phone,
                    "postcode": insurance.postcode,
                    "city": insurance.city
                }
    except Exception as e:
        context["error"] = f"Database error: {str(e)}"   
        return context
    finally:
        db.close()
