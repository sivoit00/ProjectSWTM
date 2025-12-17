from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Workshop, Customer
from schemas import Workshop as WorkshopSchema, WorkshopCreate
from auth.dependencies import get_current_user
from routes.customers import get_or_create_customer

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[WorkshopSchema])
def get_workshop(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)
    return (
        db.query(Workshop)
        .filter(Workshop.customer_id == customer.id)
        .all()
    )


@router.post("", response_model=WorkshopSchema)
def create_workshop(
    workshop: WorkshopCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    new_workshop = Workshop(
        **workshop.dict(),
        customer_id=customer.id,
    )
    db.add(new_workshop)
    db.commit()
    db.refresh(new_workshop)
    return new_workshop


@router.get("/{workshop_id}", response_model=WorkshopSchema)
def get_workshop(
    workshop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    workshop = (
        db.query(Worksop)
        .filter(
            Workshop.id == workshop_id,
            Workshop.customer_id == customer.id,
        )
        .first()
    )
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found",
        )
    return workshop


@router.put("/{workshop_id}", response_model=WorkshopSchema)
def update_workshop(
    workshop_id: int,
    workshop_update: WorkshopCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    workshop = (
        db.query(Workshop)
        .filter(
            Workshop.id == workshop_id,
            Workshop.customer_id == customer.id,
        )
        .first()
    )
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found",
        )

    for key, value in workshop_update.dict().items():
        setattr(workshop, key, value)

    db.commit()
    db.refresh(workshop)
    return workshop


@router.delete("/{workshop_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workshop(
    workshop_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    workshop = (
        db.query(Workshop)
        .filter(
            Workshop.id == workshop_id,
            Workshop.customer_id == customer.id,
        )
        .first()
    )
    if not workshop:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workshop not found",
        )

    db.delete(workshop)
    db.commit()
