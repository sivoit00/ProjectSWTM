from sqlalchemy.orm import Session
import models

class WerkstattService:
    @staticmethod
    def get_all_werkstaetten(db: Session):
        return db.query(models.Werkstatt).all()

    @staticmethod
    def create_werkstatt(werkstatt_data: dict, db: Session):
        neue_werkstatt = models.Werkstatt(**werkstatt_data)
        db.add(neue_werkstatt)
        db.commit()
        db.refresh(neue_werkstatt)
        return neue_werkstatt
