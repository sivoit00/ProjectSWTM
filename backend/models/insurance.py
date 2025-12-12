from sqlalchemy import Column, Integer, String
from database import Base

class Insurance(Base):
    __tablename__ = "insurance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)

    name = Column(String(200))
    email = Column(String(200))
    phone = Column(String(50))
    postcode = Column(String(20))
    city = Column(String(100))
