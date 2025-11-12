from sqlalchemy.orm import Session
import models
from datetime import date

class KIService:
    @staticmethod
    def ki_create_auftrag(action_data: dict, db: Session):
        werkstatt_id = action_data.get("werkstatt_id")
        if werkstatt_id is None:
            werk = db.query(models.Werkstatt).first()
            if werk:
                werkstatt_id = werk.id

        fahrzeug_id = action_data.get("fahrzeug_id")
        kunde_id = action_data.get("kunde_id")
        nachricht = action_data.get("nachricht", "")

        if fahrzeug_id is None and kunde_id is None:
            antwort = "Danke für Ihre Nachricht. Bitte geben Sie mindestens eine Fahrzeug- oder Kunden-ID an."
            ki = models.KIAktion(nachricht=nachricht, antwort=antwort, auftrag_id=None)
            db.add(ki)
            db.commit()
            db.refresh(ki)
            return ki

        auftrag = models.Auftrag(
            beschreibung=nachricht,
            status="offen",
            erstellt_am=date.today(),
            fahrzeug_id=fahrzeug_id,
            werkstatt_id=werkstatt_id,
            kosten=0,
        )
        db.add(auftrag)
        db.commit()
        db.refresh(auftrag)

        antwort = f"Ihr Auftrag wurde erstellt (ID {auftrag.id}). Wir haben Werkstatt-ID {werkstatt_id} zugewiesen."
        ki = models.KIAktion(nachricht=nachricht, antwort=antwort, auftrag_id=auftrag.id)
        db.add(ki)
        db.commit()
        db.refresh(ki)

        return ki
