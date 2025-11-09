"""
Testdaten für die Fahrzeugservice-Datenbank
Führe dieses Script aus, um die DB mit Beispieldaten zu füllen.
"""
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from datetime import date

def seed_database():
    # Session erstellen
    db = SessionLocal()
    
    try:
        # 1. Kunden erstellen
        print("📝 Erstelle Kunden...")
        kunden_data = [
            {"name": "Max Mustermann", "email": "max@example.com", "telefon": "+49 123 456789"},
            {"name": "Anna Schmidt", "email": "anna@example.com", "telefon": "+49 987 654321"},
            {"name": "Peter Müller", "email": "peter@example.com", "telefon": "+49 555 123456"},
        ]
        
        kunden = []
        for k in kunden_data:
            kunde = models.Kunde(**k)
            db.add(kunde)
            kunden.append(kunde)
        db.commit()
        print(f"✅ {len(kunden)} Kunden erstellt")
        
        # Kunden neu laden um IDs zu bekommen
        for kunde in kunden:
            db.refresh(kunde)
        
        # 2. Fahrzeuge erstellen
        print("\n🚗 Erstelle Fahrzeuge...")
        fahrzeuge_data = [
            {"marke": "BMW", "modell": "3er", "baujahr": 2020, "kunde_id": kunden[0].id},
            {"marke": "Mercedes", "modell": "C-Klasse", "baujahr": 2019, "kunde_id": kunden[0].id},
            {"marke": "VW", "modell": "Golf", "baujahr": 2021, "kunde_id": kunden[1].id},
            {"marke": "Audi", "modell": "A4", "baujahr": 2022, "kunde_id": kunden[2].id},
        ]
        
        fahrzeuge = []
        for f in fahrzeuge_data:
            fahrzeug = models.Fahrzeug(**f)
            db.add(fahrzeug)
            fahrzeuge.append(fahrzeug)
        db.commit()
        print(f"✅ {len(fahrzeuge)} Fahrzeuge erstellt")
        
        # Fahrzeuge neu laden
        for fahrzeug in fahrzeuge:
            db.refresh(fahrzeug)
        
        # 3. Werkstätten erstellen
        print("\n🔧 Erstelle Werkstätten...")
        werkstaetten_data = [
            {"name": "Meister Auto", "adresse": "Hauptstraße 123", "plz": "10115", "ort": "Berlin"},
            {"name": "KFZ Profis", "adresse": "Musterweg 45", "plz": "80331", "ort": "München"},
            {"name": "Auto Service Plus", "adresse": "Parkstraße 78", "plz": "20095", "ort": "Hamburg"},
        ]
        
        werkstaetten = []
        for w in werkstaetten_data:
            werkstatt = models.Werkstatt(**w)
            db.add(werkstatt)
            werkstaetten.append(werkstatt)
        db.commit()
        print(f"✅ {len(werkstaetten)} Werkstätten erstellt")
        
        # Werkstätten neu laden
        for werkstatt in werkstaetten:
            db.refresh(werkstatt)
        
        # 4. Aufträge erstellen
        print("\n📋 Erstelle Aufträge...")
        auftraege_data = [
            {
                "beschreibung": "Ölwechsel und Inspektion",
                "status": "offen",
                "erstellt_am": date(2024, 11, 1),
                "fahrzeug_id": fahrzeuge[0].id,
                "werkstatt_id": werkstaetten[0].id,
                "kosten": 150.00
            },
            {
                "beschreibung": "Bremsen wechseln",
                "status": "in_bearbeitung",
                "erstellt_am": date(2024, 11, 5),
                "fahrzeug_id": fahrzeuge[1].id,
                "werkstatt_id": werkstaetten[0].id,
                "kosten": 320.50
            },
            {
                "beschreibung": "TÜV-Vorbereitung",
                "status": "abgeschlossen",
                "erstellt_am": date(2024, 10, 20),
                "fahrzeug_id": fahrzeuge[2].id,
                "werkstatt_id": werkstaetten[1].id,
                "kosten": 89.90
            },
            {
                "beschreibung": "Reifen wechseln",
                "status": "offen",
                "erstellt_am": date(2024, 11, 8),
                "fahrzeug_id": fahrzeuge[3].id,
                "werkstatt_id": werkstaetten[2].id,
                "kosten": 200.00
            },
        ]
        
        auftraege = []
        for a in auftraege_data:
            auftrag = models.Auftrag(**a)
            db.add(auftrag)
            auftraege.append(auftrag)
        db.commit()
        print(f"✅ {len(auftraege)} Aufträge erstellt")
        
        print("\n✨ Datenbank erfolgreich mit Testdaten gefüllt! ✨")
        print("\n📊 Übersicht:")
        print(f"  - {len(kunden)} Kunden")
        print(f"  - {len(fahrzeuge)} Fahrzeuge")
        print(f"  - {len(werkstaetten)} Werkstätten")
        print(f"  - {len(auftraege)} Aufträge")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Starte Datenbank-Seeding...\n")
    seed_database()
