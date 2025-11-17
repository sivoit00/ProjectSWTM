from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import KIAktion, Auftrag, Werkstatt
from schemas import KIAktionCreate, KIAktionSchema
from datetime import date

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/auftrag", response_model=KIAktionSchema)
def ki_create_auftrag(action: KIAktionCreate, db: Session = Depends(get_db)):
    werkstatt_id = action.werkstatt_id
    if werkstatt_id is None:
        werk = db.query(Werkstatt).first()
        if werk:
            werkstatt_id = werk.id

    if action.fahrzeug_id is None and action.kunde_id is None:
        antwort = "Thank you for your message. Please provide at least a vehicle or customer ID."
        ki = KIAktion(nachricht=action.nachricht, antwort=antwort, auftrag_id=None)
        db.add(ki)
        db.commit()
        db.refresh(ki)
        return ki

    auftrag = Auftrag(
        beschreibung=action.nachricht,
        status="offen",
        erstellt_am=date.today(),
        fahrzeug_id=action.fahrzeug_id,
        werkstatt_id=werkstatt_id,
        kosten=0,
    )
    db.add(auftrag)
    db.commit()
    db.refresh(auftrag)

    antwort = f"Your order has been created (ID {auftrag.id}). We assigned workshop ID {werkstatt_id}."
    ki = KIAktion(nachricht=action.nachricht, antwort=antwort, auftrag_id=auftrag.id)
    db.add(ki)
    db.commit()
    db.refresh(ki)

    return ki
