from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Customer
from schemas import Customer as CustomerSchema, CustomerCreate
from auth.dependencies import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_or_create_customer(db: Session, current_user: dict) -> Customer:
    user_id = current_user.get("user_id") or current_user.get("sub")
    if not user_id:
        raise HTTPException(status_code=400, detail="No user id in token")

    customer = db.query(Customer).filter(Customer.user_id == user_id).first()
    
    if customer:
        return customer

    email = current_user.get("email") or ""
    first_name = current_user.get("given_name") or current_user.get("firstName") or "Vorname"
    last_name = current_user.get("family_name") or current_user.get("lastName") or "Nachname"
    username = current_user.get("preferred_username") or email or "Unbekannt"

    new_customer = Customer(
        user_id=user_id,  
        email=email,      
        firstName=first_name,
        lastName=last_name,
        username=username
    )
    
    try:
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating customer: {str(e)}")


@router.get("/me", response_model=CustomerSchema)
def get_current_customer(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return get_or_create_customer(db, current_user)


@router.get("", response_model=list[CustomerSchema])
def get_customer(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    return db.query(Customer).filter(Customer.user_id == current_user["user_id"]).all()


@router.post("", response_model=CustomerSchema)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    existing = (
        db.query(Customer)
        .filter(Customer.user_id == current_user["user_id"])
        .first()
    )
    if existing:
        for key, value in customer.dict().items():
            setattr(existing, key, value)
        db.commit()
        db.refresh(existing)
        return existing

    new_customer = Customer(
        **customer.dict(),
        user_id=current_user["user_id"],
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@router.get("/{customer_id}", response_model=CustomerSchema)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.user_id == current_user["user_id"]
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerSchema)
def update_customer(
    customer_id: int,
    customer_update: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    customer = db.query(Customer).filter(
        Customer.id == customer_id,
        Customer.user_id == current_user["user_id"]
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for key, value in customer_update.dict().items():
        setattr(customer, key, value)

    db.commit()
    db.refresh(customer)
    return customer
