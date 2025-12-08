from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Auftrag, Kunde
from schemas import Auftrag as AuftragSchema, AuftragCreate
from datetime import date
from auth.dependencies import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[AuftragSchema])
def get_auftraege(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if "admin" in current_user.get("roles", []):
        return db.query(Auftrag).all()
    
    user_email = current_user.get("email")
    if user_email:
        kunde = db.query(Kunde).filter(Kunde.email == user_email).first()
        if kunde:
            return db.query(Auftrag).filter(Auftrag.kunde_id == kunde.id).all()
    return []


@router.post("", response_model=AuftragSchema)
def create_auftrag(
    auftrag: AuftragCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    neuer_auftrag = Auftrag(**auftrag.dict())
    if not neuer_auftrag.erstellt_am:
        neuer_auftrag.erstellt_am = date.today()
    db.add(neuer_auftrag)
    db.commit()
    db.refresh(neuer_auftrag)
    return neuer_auftrag


@router.get("/{auftrag_id}", response_model=AuftragSchema)
def get_auftrag(
    auftrag_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    auftrag = db.query(Auftrag).filter(Auftrag.id == auftrag_id).first()
    if not auftrag:
        raise HTTPException(status_code=404, detail="Order not found")
    return auftrag


@router.get("/status/{status}", response_model=list[AuftragSchema])
def get_auftraege_nach_status(
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Auftrag).filter(Auftrag.status.ilike(status)).all()
