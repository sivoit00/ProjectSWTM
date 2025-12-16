from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Insurance, Customer
from schemas import Insurance as InsuranceSchema, InsuranceCreate
from auth.dependencies import get_current_user
from routes.customers import get_or_create_customer

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("", response_model=list[InsuranceSchema])
def get_insurance(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)
    return (
        db.query(Insurance)
        .filter(Insurance.customer_id == customer.id)
        .all()
    )


@router.post("", response_model=InsuranceSchema)
def create_insurance(
    insurance: InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    new_insurance = Insurance(
        **insurance.dict(),
        customer_id=customer.id,
    )
    db.add(new_insurance)
    db.commit()
    db.refresh(new_insurance)
    return new_insurance


@router.get("/{insurance_id}", response_model=InsuranceSchema)
def get_insurance(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    insurance = (
        db.query(Insurance)
        .filter(
            Insurance.id == insurance_id,
            Insurance.customer_id == customer.id,
        )
        .first()
    )
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found",
        )
    return insurance


@router.put("/{insurance_id}", response_model=InsuranceSchema)
def update_insurance(
    insurance_id: int,
    insurance_update: InsuranceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    insurance = (
        db.query(Insurance)
        .filter(
            Insurance.id == insurance_id,
            Insurance.customer_id == customer.id,
        )
        .first()
    )
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found",
        )

    for key, value in insurance_update.dict().items():
        setattr(insurance, key, value)

    db.commit()
    db.refresh(insurance)
    return insurance


@router.delete("/{insurance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_insurance(
    insurance_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = get_or_create_customer(db, current_user)

    insurance = (
        db.query(Insurance)
        .filter(
            Insurance.id == insurance_id,
            Insurance.customer_id == customer.id,
        )
        .first()
    )
    if not insurance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insurance not found",
        )

    db.delete(insurance)
    db.commit()
