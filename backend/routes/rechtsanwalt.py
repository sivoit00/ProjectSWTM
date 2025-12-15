from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Rechtsanwalt, Kunde
from schemas import Rechtsanwalt as RechtsanwaltSchema, RechtsanwaltCreate
from auth.dependencies import get_current_user
from routes.kunden import get_or_create_kunde

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[RechtsanwaltSchema])
def get_rechtsanwaelte(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)
    return (
        db.query(Rechtsanwalt)
        .filter(Rechtsanwalt.kunde_id == kunde.id)
        .all()
    )


@router.post("", response_model=RechtsanwaltSchema)
def create_rechtsanwalt(
    rechtsanwalt: RechtsanwaltCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    neuer_rechtsanwalt = Rechtsanwalt(
        **rechtsanwalt.dict(),
        kunde_id=kunde.id,
    )
    db.add(neuer_rechtsanwalt)
    db.commit()
    db.refresh(neuer_rechtsanwalt)
    return neuer_rechtsanwalt


@router.get("/{rechtsanwalt_id}", response_model=RechtsanwaltSchema)
def get_rechtsanwalt(
    rechtsanwalt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    rechtsanwalt = (
        db.query(Rechtsanwalt)
        .filter(
            Rechtsanwalt.id == rechtsanwalt_id,
            Rechtsanwalt.kunde_id == kunde.id,
        )
        .first()
    )
    if not rechtsanwalt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found",
        )
    return rechtsanwalt


@router.put("/{rechtsanwalt_id}", response_model=RechtsanwaltSchema)
def update_rechtsanwalt(
    rechtsanwalt_id: int,
    rechtsanwalt_update: RechtsanwaltCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    rechtsanwalt = (
        db.query(Rechtsanwalt)
        .filter(
            Rechtsanwalt.id == rechtsanwalt_id,
            Rechtsanwalt.kunde_id == kunde.id,
        )
        .first()
    )
    if not rechtsanwalt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found",
        )

    for key, value in rechtsanwalt_update.dict().items():
        setattr(rechtsanwalt, key, value)

    db.commit()
    db.refresh(rechtsanwalt)
    return rechtsanwalt


@router.delete("/{rechtsanwalt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_rechtsanwalt(
    rechtsanwalt_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    rechtsanwalt = (
        db.query(Rechtsanwalt)
        .filter(
            Rechtsanwalt.id == rechtsanwalt_id,
            Rechtsanwalt.kunde_id == kunde.id,
        )
        .first()
    )
    if not rechtsanwalt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found",
        )

    db.delete(rechtsanwalt)
    db.commit()
