from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Fahrzeug
from schemas import Fahrzeug as FahrzeugSchema, FahrzeugCreate
from auth.dependencies import get_current_user
from routes.kunden import get_or_create_kunde 

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[FahrzeugSchema])
def get_fahrzeuge(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)
    return db.query(Fahrzeug).filter(Fahrzeug.kunde_id == kunde.id).all()


@router.post("", response_model=FahrzeugSchema)
def create_fahrzeug(
    fahrzeug: FahrzeugCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    neues_fahrzeug = Fahrzeug(
        **fahrzeug.dict(),
        kunde_id=kunde.id,
    )
    db.add(neues_fahrzeug)
    db.commit()
    db.refresh(neues_fahrzeug)
    return neues_fahrzeug


@router.get("/{fahrzeug_id}", response_model=FahrzeugSchema)
def get_fahrzeug(
    fahrzeug_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    fahrzeug = (
        db.query(Fahrzeug)
        .filter(
            Fahrzeug.id == fahrzeug_id,
            Fahrzeug.kunde_id == kunde.id,
        )
        .first()
    )
    if not fahrzeug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )
    return fahrzeug


@router.put("/{fahrzeug_id}", response_model=FahrzeugSchema)
def update_fahrzeug(
    fahrzeug_id: int,
    fahrzeug_update: FahrzeugCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    fahrzeug = (
        db.query(Fahrzeug)
        .filter(
            Fahrzeug.id == fahrzeug_id,
            Fahrzeug.kunde_id == kunde.id, 
        )
        .first()
    )
    if not fahrzeug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    for key, value in fahrzeug_update.dict().items():
        setattr(fahrzeug, key, value)

    db.commit()
    db.refresh(fahrzeug)
    return fahrzeug


@router.delete("/{fahrzeug_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fahrzeug(
    fahrzeug_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    kunde = get_or_create_kunde(db, current_user)

    fahrzeug = (
        db.query(Fahrzeug)
        .filter(
            Fahrzeug.id == fahrzeug_id,
            Fahrzeug.kunde_id == kunde.id,
        )
        .first()
    )
    if not fahrzeug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    db.delete(fahrzeug)
    db.commit()