from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
from database import SessionLocal
from services.werkstatt_service import WerkstattService

router = APIRouter(prefix="/werkstatt", tags=["Werkstätten"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[schemas.Werkstatt])
def get_werkstatt(db: Session = Depends(get_db)):
    return WerkstattService.get_all_werkstaetten(db)

@router.post("", response_model=schemas.Werkstatt)
def create_werkstatt(werkstatt: schemas.WerkstattCreate, db: Session = Depends(get_db)):
    return WerkstattService.create_werkstatt(werkstatt.dict(), db)
