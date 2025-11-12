from sqlalchemy.orm import Session
import models

class FahrzeugService:
    @staticmethod
    def get_all_fahrzeuge(db: Session):
        return db.query(models.Fahrzeug).all()

    @staticmethod
    def create_fahrzeug(fahrzeug_data: dict, db: Session):
        neues_fahrzeug = models.Fahrzeug(**fahrzeug_data)
        db.add(neues_fahrzeug)
        db.commit()
        db.refresh(neues_fahrzeug)
        return neues_fahrzeug

    @staticmethod
    def get_auftraege_von_fahrzeug(fahrzeug_id: int, db: Session):
        return db.query(models.Auftrag).filter(models.Auftrag.fahrzeug_id == fahrzeug_id).all()
