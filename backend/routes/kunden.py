from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
from database import SessionLocal
from services.kunden_service import KundenService

router = APIRouter(prefix="/kunden", tags=["Kunden"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[schemas.Kunde])
def get_kunden(db: Session = Depends(get_db)):
    return KundenService.get_all_kunden(db)

@router.post("", response_model=schemas.Kunde)
def create_kunde(kunde: schemas.KundeCreate, db: Session = Depends(get_db)):
    return KundenService.create_kunde(kunde.dict(), db)

@router.get("/{kunde_id}/fahrzeuge", response_model=list[schemas.Fahrzeug])
def get_fahrzeuge_von_kunde(kunde_id: int, db: Session = Depends(get_db)):
    return KundenService.get_fahrzeuge_von_kunde(kunde_id, db)
