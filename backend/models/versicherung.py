from sqlalchemy import Column, Integer, String, ForeignKey
from database import Base


class Versicherung(Base):
    __tablename__ = "versicherung"

    id = Column(Integer, primary_key=True, index=True)
    kunde_id = Column(Integer, ForeignKey("kunde.id"))

    name = Column(String(150))
    number = Column(String(100))
    contact = Column(String(150))
    email = Column(String(150))
    phone = Column(String(50))
    address = Column(String(150))
    postcode = Column(String(20))
    city = Column(String(100))
