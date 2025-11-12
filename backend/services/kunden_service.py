from sqlalchemy.orm import Session
import models

class KundenService:
    @staticmethod
    def get_all_kunden(db: Session):
        return db.query(models.Kunde).all()

    @staticmethod
    def create_kunde(kunde_data: dict, db: Session):
        neuer_kunde = models.Kunde(**kunde_data)
        db.add(neuer_kunde)
        db.commit()
        db.refresh(neuer_kunde)
        return neuer_kunde

    @staticmethod
    def get_fahrzeuge_von_kunde(kunde_id: int, db: Session):
        return db.query(models.Fahrzeug).filter(models.Fahrzeug.kunde_id == kunde_id).all()
