from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Versicherung, Kunde
from schemas import Versicherung as VersicherungSchema, VersicherungCreate
from auth.dependencies import get_current_user
from routes.kunden import get_or_create_kunde

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("", response_model=list[VersicherungSchema])
def get_versicherungen(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)
    return (
        db.query(Versicherung)
        .filter(Versicherung.kunde_id == kunde.id)
        .all()
    )


@router.post("", response_model=VersicherungSchema)
def create_versicherung(
    versicherung: VersicherungCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    neue_versicherung = Versicherung(
        **versicherung.dict(),
        kunde_id=kunde.id,
    )
    db.add(neue_versicherung)
    db.commit()
    db.refresh(neue_versicherung)
    return neue_versicherung


@router.get("/{versicherung_id}", response_model=VersicherungSchema)
def get_versicherung(
    versicherung_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    versicherung = (
        db.query(Versicherung)
        .filter(
            Versicherung.id == versicherung_id,
            Versicherung.kunde_id == kunde.id,
        )
        .first()
    )
    if not versicherung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found",
        )
    return versicherung


@router.put("/{versicherung_id}", response_model=VersicherungSchema)
def update_versicherung(
    versicherung_id: int,
    versicherung_update: VersicherungCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    versicherung = (
        db.query(Versicherung)
        .filter(
            Versicherung.id == versicherung_id,
            Versicherung.kunde_id == kunde.id,
        )
        .first()
    )
    if not versicherung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found",
        )

    for key, value in versicherung_update.dict().items():
        setattr(versicherung, key, value)

    db.commit()
    db.refresh(versicherung)
    return versicherung


@router.delete("/{versicherung_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_versicherung(
    versicherung_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    versicherung = (
        db.query(Versicherung)
        .filter(
            Versicherung.id == versicherung_id,
            Versicherung.kunde_id == kunde.id,
        )
        .first()
    )
    if not versicherung:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found",
        )

    db.delete(versicherung)
    db.commit()
