from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Werkstatt, Kunde
from schemas import Werkstatt as WerkstattSchema, WerkstattCreate
from auth.dependencies import get_current_user
from routes.kunden import get_or_create_kunde

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[WerkstattSchema])
def get_werkstaetten(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)
    return (
        db.query(Werkstatt)
        .filter(Werkstatt.kunde_id == kunde.id)
        .all()
    )


@router.post("", response_model=WerkstattSchema)
def create_werkstatt(
    werkstatt: WerkstattCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    neue_werkstatt = Werkstatt(
        **werkstatt.dict(),
        kunde_id=kunde.id,
    )
    db.add(neue_werkstatt)
    db.commit()
    db.refresh(neue_werkstatt)
    return neue_werkstatt


@router.get("/{werkstatt_id}", response_model=WerkstattSchema)
def get_werkstatt(
    werkstatt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    werkstatt = (
        db.query(Werkstatt)
        .filter(
            Werkstatt.id == werkstatt_id,
            Werkstatt.kunde_id == kunde.id,
        )
        .first()
    )
    if not werkstatt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found",
        )
    return werkstatt


@router.put("/{werkstatt_id}", response_model=WerkstattSchema)
def update_werkstatt(
    werkstatt_id: int,
    werkstatt_update: WerkstattCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    werkstatt = (
        db.query(Werkstatt)
        .filter(
            Werkstatt.id == werkstatt_id,
            Werkstatt.kunde_id == kunde.id,
        )
        .first()
    )
    if not werkstatt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found",
        )

    for key, value in werkstatt_update.dict().items():
        setattr(werkstatt, key, value)

    db.commit()
    db.refresh(werkstatt)
    return werkstatt


@router.delete("/{werkstatt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_werkstatt(
    werkstatt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    werkstatt = (
        db.query(Werkstatt)
        .filter(
            Werkstatt.id == werkstatt_id,
            Werkstatt.kunde_id == kunde.id,
        )
        .first()
    )
    if not werkstatt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found",
        )

    db.delete(werkstatt)
    db.commit()
