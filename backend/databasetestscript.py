# databasetest_aws.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.DamageEvent import DamageEvent
from datetime import datetime

# ---------------------------------------------------
# 1. Datenbank-URL einstellen (AWS-RDS)
# ---------------------------------------------------
DATABASE_URL = "postgresql://postgres:Aasal22!!@projectswtm.c9gqueuwynyt.eu-north-1.rds.amazonaws.com:5432/fahrzeugservice"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ---------------------------------------------------
# 2. Testdaten für ein Schadensereignis
# ---------------------------------------------------
test_claim = {
    "claim_id": f"CLM-{int(datetime.utcnow().timestamp())}",  # eindeutige ID
    "customer_id": 123,
    "description": "Testschaden: Kratzer an der Stoßstange"
}

# ---------------------------------------------------
# 3. Eintrag in die Datenbank
# ---------------------------------------------------
db = SessionLocal()

try:
    event = DamageEvent(
        damage_event_id=test_claim["claim_id"],
        customer_id=test_claim["customer_id"],
        description=test_claim["description"],
        status="submitted"
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    print(f"✅ DamageEvent gespeichert: {event.damage_event_id}, Status: {event.status}")

    # Direkt wieder abfragen
    queried_event = db.query(DamageEvent).filter_by(damage_event_id=event.damage_event_id).first()
    print(f"🔍 Abgefragt: {queried_event.damage_event_id}, Status: {queried_event.status}, Beschreibung: {queried_event.description}")

except Exception as e:
    db.rollback()
    print("❌ Fehler beim Speichern:", str(e))

finally:
    db.close()
