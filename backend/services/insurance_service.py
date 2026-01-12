import json
from typing import Any, Dict, Optional
from database import SessionLocal
from sqlalchemy.orm import joinedload
from models.damage_event import DamageEvent
from models.customer import Customer
from models.vehicle import Vehicle
from models.insurance import Insurance
import logging

log = logging.getLogger(__name__)

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
