from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas
from database import SessionLocal
from services.auftrag_service import AuftragService

router = APIRouter(prefix="/auftraege", tags=["Aufträge"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=list[schemas.Auftrag])
def get_auftraege(db: Session = Depends(get_db)):
    return AuftragService.get_all_auftraege(db)

@router.post("", response_model=schemas.Auftrag)
def create_auftrag(auftrag: schemas.AuftragCreate, db: Session = Depends(get_db)):
    return AuftragService.create_auftrag(auftrag.dict(), db)

@router.get("/status/{status}", response_model=list[schemas.Auftrag])
def get_auftraege_nach_status(status: str, db: Session = Depends(get_db)):
    return AuftragService.get_auftraege_nach_status(status, db)
