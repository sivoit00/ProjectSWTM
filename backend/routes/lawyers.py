from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Lawyer, Customer
from schemas import Lawyer as LawyerSchema, LawyerCreate
from auth.dependencies import get_current_user
from routes.customers import get_or_create_customer

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[LawyerSchema])
def get_lawyer(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)
    return (
        db.query(Lawyer)
        .filter(Lawyer.customer_id == customer.id)
        .all()
    )


@router.post("", response_model=LawyerSchema)
def create_lawyer(
    lawyer: LawyerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    new_lawyer = Lawyer(
        **lawyer.dict(),
        customer_id=customer.id,
    )
    db.add(new_lawyer)
    db.commit()
    db.refresh(new_lawyer)
    return new_lawyer


@router.get("/{lawyer_id}", response_model=LawyerSchema)
def get_lawyer(
    lawyer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    lawyer = (
        db.query(Lawyer)
        .filter(
            Lawyer.id == lawyer_id,
            Lawyer.customer_id == customer.id,
        )
        .first()
    )
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found",
        )
    return lawyer


@router.put("/{lawyer_id}", response_model=LawyerSchema)
def update_lawyer(
    lawyer_id: int,
    lawyer_update: LawyerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    lawyer = (
        db.query(Lawyer)
        .filter(
            Lawyer.id == lawyer_id,
            Lawyer.customer_id == customer.id,
        )
        .first()
    )
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found",
        )

    for key, value in lawyer_update.dict().items():
        setattr(lawyer, key, value)

    db.commit()
    db.refresh(lawyer)
    return lawyer


@router.delete("/{lawyer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lawyer(
    lawyer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    lawyer = (
        db.query(Lawyer)
        .filter(
            Lawyer.id == lawyer_id,
            Lawyer.customer_id == customer.id,
        )
        .first()
    )
    if not lawyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lawyer not found",
        )

    db.delete(lawyer)
    db.commit()
