from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
from database import SessionLocal
from services.fahrzeug_service import FahrzeugService

router = APIRouter(prefix="/fahrzeuge", tags=["Fahrzeuge"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[schemas.Fahrzeug])
def get_fahrzeuge(db: Session = Depends(get_db)):
    return FahrzeugService.get_all_fahrzeuge(db)

@router.post("", response_model=schemas.Fahrzeug)
def create_fahrzeug(fahrzeug: schemas.FahrzeugCreate, db: Session = Depends(get_db)):
    return FahrzeugService.create_fahrzeug(fahrzeug.dict(), db)

@router.get("/{fahrzeug_id}/auftraege", response_model=list[schemas.Auftrag])
def get_auftraege_von_fahrzeug(fahrzeug_id: int, db: Session = Depends(get_db)):
    return FahrzeugService.get_auftraege_von_fahrzeug(fahrzeug_id, db)
