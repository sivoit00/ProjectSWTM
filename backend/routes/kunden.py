from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Kunde
from schemas import Kunde as KundeSchema, KundeCreate
from auth.dependencies import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_kunde(db: Session, current_user: dict) -> Kunde:
    user_id = current_user.get("user_id") or current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="No user id in token")

    kunde = db.query(Kunde).filter(Kunde.user_id == user_id).first()
    if kunde:
        return kunde

    username = (
        current_user.get("preferred_username")
        or current_user.get("username")
        or "Unbekannt"
    )
    email = current_user.get("email") or ""

    kunde = Kunde(
        user_id=user_id,
        email=email,
        name=username,
    )
    db.add(kunde)
    db.commit()
    db.refresh(kunde)
    return kunde



@router.get("", response_model=list[KundeSchema])
def get_kunden(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Kunde).filter(Kunde.user_id == current_user["user_id"]).all()


@router.post("", response_model=KundeSchema)
def create_kunde(
    kunde: KundeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Wird vom Onboarding/Profile verwendet:
    - existiert schon ein Kunde -> Felder aktualisieren (zusätzliche Daten)
    - sonst neuen Kunden mit diesen Feldern + user_id anlegen
    """
    existing = (
        db.query(Kunde)
        .filter(Kunde.user_id == current_user["user_id"])
        .first()
    )
    if existing:
        for key, value in kunde.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    neuer_kunde = Kunde(
        **kunde.dict(),
        user_id=current_user["user_id"],
    )
    db.add(neuer_kunde)
    db.commit()
    db.refresh(neuer_kunde)
    return neuer_kunde


@router.get("/{kunde_id}", response_model=KundeSchema)
def get_kunde(
    kunde_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    kunde = db.query(Kunde).filter(
        Kunde.id == kunde_id,
        Kunde.user_id == current_user["user_id"]
    ).first()
    if not kunde:
        raise HTTPException(status_code=404, detail="Customer not found")
    return kunde


@router.put("/{kunde_id}", response_model=KundeSchema)
def update_kunde(
    kunde_id: int,
    kunde_update: KundeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = db.query(Kunde).filter(
        Kunde.id == kunde_id,
        Kunde.user_id == current_user["user_id"]
    ).first()
    if not kunde:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in kunde_update.dict().items():
        setattr(kunde, key, value)

    db.commit()
    db.refresh(kunde)
    return kunde
