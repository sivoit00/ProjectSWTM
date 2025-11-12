from sqlalchemy.orm import Session
import models
from datetime import date

class AuftragService:
    @staticmethod
    def get_all_auftraege(db: Session):
        return db.query(models.Auftrag).all()

    @staticmethod
    def create_auftrag(auftrag_data: dict, db: Session):
        neuer_auftrag = models.Auftrag(**auftrag_data)
        if not neuer_auftrag.erstellt_am:
            neuer_auftrag.erstellt_am = date.today()
        db.add(neuer_auftrag)
        db.commit()
        db.refresh(neuer_auftrag)
        return neuer_auftrag

    @staticmethod
    def get_auftraege_nach_status(status: str, db: Session):
        return db.query(models.Auftrag).filter(models.Auftrag.status.ilike(status)).all()
