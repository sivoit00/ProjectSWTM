"""
services/insurance_service.py
Sauberer Insurance-Service, der direkt mit der Datenbank arbeitet.
"""

import os
import json
from typing import Any, Dict
from database import SessionLocal
from models.DamageEvent import DamageEvent


def get_policy_details(customer_id: str) -> Dict[str, Any]:
    """
    Placeholder: Gibt Fake-Daten zurück, bis du ein Policy-Modell hast.
    """
    return {
        "customer_id": customer_id,
        "policy_id": f"POL-{customer_id}",
        "coverage": {"liability": True, "collision": False, "theft": True},
        "status": "active"
    }

def calculate_premium(vehicle_data: Any) -> Dict[str, Any]:
    """
    Einfacher Prämienrechner (Mock).
    """
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
            damage_event_id=claim_data["claim_id"],
            customer_id=claim_data.get("customer_id"),
            description=claim_data.get("description", ""),
            status="submitted"
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return {
            "claim_id": event.damage_event_id,
            "status": event.status,
            "note": "DamageEvent stored in database"
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
