from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Kunde
from schemas import Kunde as KundeSchema, KundeCreate

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[KundeSchema])
def get_kunden(db: Session = Depends(get_db)):
    return db.query(Kunde).all()


@router.post("", response_model=KundeSchema)
def create_kunde(kunde: KundeCreate, db: Session = Depends(get_db)):
    neuer_kunde = Kunde(**kunde.dict())
    db.add(neuer_kunde)
    db.commit()
    db.refresh(neuer_kunde)
    return neuer_kunde


@router.get("/{kunde_id}", response_model=KundeSchema)
def get_kunde(kunde_id: int, db: Session = Depends(get_db)):
    kunde = db.query(Kunde).filter(Kunde.id == kunde_id).first()
    if not kunde:
        raise HTTPException(status_code=404, detail="Customer not found")
    return kunde
