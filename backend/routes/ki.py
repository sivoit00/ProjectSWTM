from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
from database import SessionLocal
from services.ki_service import KIService

router = APIRouter(prefix="/ki", tags=["KI-Auftragserstellung"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auftrag", response_model=schemas.KIAktionSchema)
def ki_create_auftrag(action: schemas.KIAktionCreate, db: Session = Depends(get_db)):
    action_dict = {
        "nachricht": action.nachricht,
        "fahrzeug_id": action.fahrzeug_id,
        "kunde_id": action.kunde_id,
        "werkstatt_id": action.werkstatt_id,
    }
    return KIService.ki_create_auftrag(action_dict, db)
