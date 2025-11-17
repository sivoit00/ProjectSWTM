from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Werkstatt
from schemas import Werkstatt as WerkstattSchema, WerkstattCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[WerkstattSchema])
def get_werkstaetten(db: Session = Depends(get_db)):
    return db.query(Werkstatt).all()


@router.post("", response_model=WerkstattSchema)
def create_werkstatt(werkstatt: WerkstattCreate, db: Session = Depends(get_db)):
    neue_werkstatt = Werkstatt(**werkstatt.dict())
    db.add(neue_werkstatt)
    db.commit()
    db.refresh(neue_werkstatt)
    return neue_werkstatt


@router.get("/{werkstatt_id}", response_model=WerkstattSchema)
def get_werkstatt(werkstatt_id: int, db: Session = Depends(get_db)):
    werkstatt = db.query(Werkstatt).filter(Werkstatt.id == werkstatt_id).first()
    if not werkstatt:
        raise HTTPException(status_code=404, detail="Workshop not found")
    return werkstatt
