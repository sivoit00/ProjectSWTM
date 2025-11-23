"""
services/insurance_service.py

Helper functions that represent the actual Insurance Agent tools.
Implemented with defensive fallback: DB access -> REST -> Mock.
"""

import os
import json
from typing import Any, Dict

# try: import db session (if available)
try:
    from database import SessionLocal
    from models import Customer, Policy, Claim  
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

import requests

BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")  
TIMEOUT = 6

def _call_rest(path: str, method: str = "get", json_body: dict = None):
    url = f"{BASE_URL.rstrip('/')}/{path.lstrip('/')}"
    try:
        if method.lower() == "get":
            r = requests.get(url, timeout=TIMEOUT)
        else:
            r = requests.post(url, json=json_body, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ---- service-implementations ----

def get_policy_details(customer_id: str) -> Dict[str, Any]:
    """
    Liefert die Policy-Details zu einem Kunden.
    Versucht DB, sonst REST-Fallback, sonst Mock-Antwort.
    """
    # DB path
    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            policy = db.query(Policy).filter(Policy.customer_id == customer_id).first()
            if policy:
                return {"policy_id": policy.id, "coverage": policy.coverage, "status": policy.status}
        except Exception:
            pass

    # REST fallback
    resp = _call_rest(f"kunden/{customer_id}")
    if resp and not resp.get("error"):
        # Assumption: /customers/{id} returns customers + possibly policy; adjust if necessary
        # Simple fallback: return whole customer object
        return {"customer": resp}
    # last fallback (Mock)
    return {
        "policy_id": f"POL-{customer_id}",
        "coverage": {"liability": True, "collision": False, "theft": True},
        "status": "active"
    }

def calculate_premium(vehicle_data: Any) -> Dict[str, Any]:
    """
    Einfacher Prämien-Rechner (Mock): nimmt vehicle_data dict oder json-string
    In Produktion: hier Business-Logik einbauen oder externen Pricing-Service anfragen.
    """
    if isinstance(vehicle_data, str):
        try:
            vehicle = json.loads(vehicle_data)
        except Exception:
            vehicle = {"make": "unknown", "year": 2020}
    elif isinstance(vehicle_data, dict):
        vehicle = vehicle_data
    else:
        vehicle = {"make": "unknown", "year": 2020}

    base = 200.0
    # simple heuristic example
    age = 2025 - int(vehicle.get("year", 2020))
    premium = base + max(0, age) * 10
    if vehicle.get("value"):
        premium += float(vehicle["value"]) * 0.01

    return {"estimated_premium": round(premium, 2), "currency": "EUR", "calculator_version": "v1.0"}

def submit_claim(claim_data: Any) -> Dict[str, Any]:
    """
    Legt einen Schaden an. Falls DB vorhanden -> create Claim, ansonsten REST oder Mock.
    claim_data: dict oder json-string mit keys: customer_id, vehicle_id, description, amount_estimate
    """
    if isinstance(claim_data, str):
        try:
            claim = json.loads(claim_data)
        except Exception:
            claim = {"description": claim_data}
    else:
        claim = claim_data or {}

    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            new_claim = Claim(
                customer_id=claim.get("customer_id"),
                vehicle_id=claim.get("vehicle_id"),
                description=claim.get("description"),
                status="submitted",
                amount_estimate=claim.get("amount_estimate")
            )
            db.add(new_claim)
            db.commit()
            db.refresh(new_claim)
            return {"claim_id": new_claim.id, "status": new_claim.status}
        except Exception:
            pass

    # REST fallback
    resp = _call_rest("claims", method="post", json_body=claim)
    if resp and not resp.get("error"):
        return resp

    # Mock response
    import time
    fake_id = f"CLM-{int(time.time())}"
    return {"claim_id": fake_id, "status": "submitted", "note": "mock claim created"}

def get_claim_status(claim_id: str) -> Dict[str, Any]:
    """
    Liefert Status eines Schadenfalls
    """
    if DB_AVAILABLE:
        try:
            db = SessionLocal()
            claim = db.query(Claim).filter(Claim.id == claim_id).first()
            if claim:
                return {"claim_id": claim.id, "status": claim.status}
        except Exception:
            pass

    resp = _call_rest(f"claims/{claim_id}")
    if resp and not resp.get("error"):
        return resp

    return {"claim_id": claim_id, "status": "unknown", "note": "no record in DB/REST; returned mock status"}
