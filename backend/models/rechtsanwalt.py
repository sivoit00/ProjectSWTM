from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Rechtsanwalt(Base):
    __tablename__ = "rechtsanwalt"

    id = Column(Integer, primary_key=True, index=True)
    kunde_id = Column(Integer, ForeignKey("kunde.id"))

    firstName = Column(String(100))
    lastName = Column(String(100))
    company = Column(String(150))
    email = Column(String(150))
    phone = Column(String(50))
    address = Column(String(150))
    postcode = Column(String(20))
    city = Column(String(100))
