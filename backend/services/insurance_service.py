import json
from typing import Any, Dict, Optional
from database import SessionLocal
from models.DamageEvent import DamageEvent
from models.kunde import Kunde
from models.fahrzeug import Fahrzeug
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



def get_user_context(customer_id: Optional[str]) -> Dict[str, Any]:

    db = SessionLocal()
    context: Dict[str, Any] = {}

    try:

        if not customer_id:
            return context

        kunde: Optional[Kunde] = None

        # customer_id can be either the numeric DB id (as string) or an email address.
        # Avoid querying an Integer column with a non-numeric value (psycopg2 DataError).
        customer_id_str = str(customer_id).strip()
        if customer_id_str.isdigit():
            kunde = db.query(Kunde).filter_by(id=int(customer_id_str)).first()
        else:
            kunde = db.query(Kunde).filter_by(email=customer_id_str).first()

        if not kunde:
            return context

        context["customer_id"] = str(kunde.id)
        context["customer_name"] = kunde.name
        context["customer_email"] = kunde.email
        context["customer_phone"] = kunde.telefon

        
        fahrzeuge: list = []
        for f in kunde.fahrzeuge:
            fahrzeuge.append({
                "id": f.id,
                "marke": f.marke,
                "modell": f.modell,
                "baujahr": f.baujahr
            })
        context["vehicles"] = fahrzeuge

        
        insurance: Optional[Insurance] = db.query(Insurance).filter_by(user_id=str(kunde.id)).first()
        if insurance:
            context["insurance"] = {
                "name": insurance.name,
                "email": insurance.email,
                "phone": insurance.phone,
                "postcode": insurance.postcode,
                "city": insurance.city
            }

        return context

    finally:
        db.close()
