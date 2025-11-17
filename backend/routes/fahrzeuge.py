from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Fahrzeug
from schemas import Fahrzeug as FahrzeugSchema, FahrzeugCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[FahrzeugSchema])
def get_fahrzeuge(db: Session = Depends(get_db)):
    return db.query(Fahrzeug).all()


@router.post("", response_model=FahrzeugSchema)
def create_fahrzeug(fahrzeug: FahrzeugCreate, db: Session = Depends(get_db)):
    neues_fahrzeug = Fahrzeug(**fahrzeug.dict())
    db.add(neues_fahrzeug)
    db.commit()
    db.refresh(neues_fahrzeug)
    return neues_fahrzeug


@router.get("/{fahrzeug_id}", response_model=FahrzeugSchema)
def get_fahrzeug(fahrzeug_id: int, db: Session = Depends(get_db)):
    fahrzeug = db.query(Fahrzeug).filter(Fahrzeug.id == fahrzeug_id).first()
    if not fahrzeug:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return fahrzeug
