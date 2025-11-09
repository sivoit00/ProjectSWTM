# Sprint 1 - Abschlussdokumentation
**User Story US1.5:** Als Entwickler möchte ich API- und DB-Struktur einrichten, um spätere Integration vorzubereiten.

**Zeitraum:** 03.11 - 09.11.2025  
**Status:** ✅ **ABGESCHLOSSEN**  
**Verantwortlich:** Mohammed Al-Otaibi

---

## ✅ Akzeptanzkriterien (erfüllt)

1. ✅ **DB verbunden** - PostgreSQL läuft in Docker und ist erreichbar
2. ✅ **REST-API testbar** - Alle Endpoints funktionieren und sind dokumentiert

---

## 🎯 Implementierte Features

### 1. Datenbank-Setup ✅
- **PostgreSQL 13** läuft in Docker Container
- **Datenbank:** `fahrzeugservice`
- **5 Tabellen erstellt:**
  - `kunde` - Kundendaten (Name, Email, Telefon)
  - `fahrzeug` - Fahrzeuge (Marke, Modell, Baujahr, kunde_id)
  - `werkstatt` - Werkstätten (Name, Adresse, PLZ, Ort)
  - `auftrag` - Aufträge (Beschreibung, Status, Kosten, erstellt_am)
  - `ki_aktionen` - KI-Aktionen für spätere Chatbot-Integration

- **Testdaten eingefügt:**
  - 3 Kunden (Max Mustermann, Anna Schmidt, Peter Müller)
  - 4 Fahrzeuge (BMW, Mercedes, VW, Audi)
  - 3 Werkstätten (Berlin, München, Hamburg)
  - 4 Aufträge (verschiedene Status: offen, in_bearbeitung, abgeschlossen)

### 2. Backend-API (FastAPI) ✅

#### Implementierte Endpoints:

**Kunden:**
- `GET /kunden` - Alle Kunden abrufen
- `POST /kunden` - Neuen Kunden erstellen
- `PUT /kunden/{kunde_id}` - Kunde aktualisieren
- `DELETE /kunden/{kunde_id}` - Kunde löschen

**Fahrzeuge:**
- `GET /fahrzeuge` - Alle Fahrzeuge abrufen
- `POST /fahrzeuge` - Neues Fahrzeug erstellen
- `PUT /fahrzeuge/{fahrzeug_id}` - Fahrzeug aktualisieren
- `DELETE /fahrzeuge/{fahrzeug_id}` - Fahrzeug löschen
- `GET /fahrzeuge/{fahrzeug_id}/auftraege` - Alle Aufträge eines Fahrzeugs

**Werkstätten:**
- `GET /werkstatt` - Alle Werkstätten abrufen
- `POST /werkstatt` - Neue Werkstatt erstellen
- `PUT /werkstatt/{werkstatt_id}` - Werkstatt aktualisieren
- `DELETE /werkstatt/{werkstatt_id}` - Werkstatt löschen

**Aufträge:**
- `GET /auftraege` - Alle Aufträge abrufen
- `POST /auftraege` - Neuen Auftrag erstellen
- `PUT /auftraege/{auftrag_id}` - Auftrag aktualisieren
- `DELETE /auftraege/{auftrag_id}` - Auftrag löschen
- `GET /auftraege/status/{status}` - Aufträge nach Status filtern

**Zusatzfunktionen:**
- `GET /kunden/{kunde_id}/fahrzeuge` - Alle Fahrzeuge eines Kunden
- `POST /ki/auftrag` - KI-gestützte Auftragserstellung (vorbereitet)
- `POST /openai/chat` - OpenAI Chat-Integration (vorbereitet)

#### API-Dokumentation:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 3. Technische Details ✅

**Backend:**
- Framework: FastAPI
- ORM: SQLAlchemy
- Validierung: Pydantic v2
- Datenbank-Driver: psycopg2
- CORS aktiviert für Frontend (http://localhost:5173)

**Datenbank:**
- PostgreSQL 13
- Docker Volume für Datenpersistenz
- Automatische Tabellenerstellung via SQLAlchemy
- Foreign Keys & Relationships definiert

**Docker Setup:**
- 4 Services: db, backend, frontend, keycloak (vorbereitet)
- docker-compose.yml konfiguriert
- Umgebungsvariablen für DB-Connection

---

## 🧪 Tests durchgeführt

### 1. Datenbank-Verbindung ✅
```bash
docker compose exec db psql -U postgres -d fahrzeugservice -c "\dt"
```
**Ergebnis:** Alle 5 Tabellen vorhanden

### 2. API-Endpoints ✅
```bash
curl http://localhost:8000/kunden
curl http://localhost:8000/fahrzeuge
curl http://localhost:8000/auftraege
curl http://localhost:8000/werkstatt
```
**Ergebnis:** Alle Endpoints geben korrekte JSON-Daten zurück

### 3. CRUD-Operationen ✅
- ✅ CREATE: `POST /kunden` → Kunde erstellt
- ✅ READ: `GET /kunden` → Alle Kunden abgerufen
- ✅ UPDATE: `PUT /kunden/1` → Kunde aktualisiert
- ✅ DELETE: `DELETE /kunden/1` → Kunde gelöscht

### 4. Swagger UI ✅
- Alle Endpoints in Swagger UI sichtbar
- Alle Schemas korrekt definiert
- Try-it-out Funktion getestet

---

## 📊 Code-Änderungen

### Neue Dateien:
1. `backend/seed_data.py` - Script zum Einfügen von Testdaten
2. `SPRINT_1_DOKUMENTATION.md` - Diese Dokumentation

### Geänderte Dateien:
1. `backend/main.py` - **UPDATE & DELETE Endpoints hinzugefügt**
   ```python
   # ✅ NEU: 8 UPDATE Endpoints (PUT)
   # ✅ NEU: 4 DELETE Endpoints (DELETE)
   ```

**Code-Markierung:**
```python
# ---------------- UPDATE ENDPOINTS ----------------
# ✅ HINZUGEFÜGT für Sprint 1 (US1.5)
# PUT Endpoints für vollständige CRUD-Operationen

@app.put("/kunden/{kunde_id}", response_model=schemas.Kunde)
def update_kunde(kunde_id: int, kunde: schemas.KundeCreate, db: Session = Depends(get_db)):
    """
    ✅ Sprint 1: UPDATE-Endpoint für Kunden
    Aktualisiert einen bestehenden Kunden
    """
    db_kunde = db.query(models.Kunde).filter(models.Kunde.id == kunde_id).first()
    if not db_kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    for key, value in kunde.dict().items():
        setattr(db_kunde, key, value)
    db.commit()
    db.refresh(db_kunde)
    return db_kunde

# Analog für: /fahrzeuge, /werkstatt, /auftraege

# ---------------- DELETE ENDPOINTS ----------------
# ✅ HINZUGEFÜGT für Sprint 1 (US1.5)
# DELETE Endpoints für vollständige CRUD-Operationen

@app.delete("/kunden/{kunde_id}")
def delete_kunde(kunde_id: int, db: Session = Depends(get_db)):
    """
    ✅ Sprint 1: DELETE-Endpoint für Kunden
    Löscht einen Kunden aus der Datenbank
    """
    db_kunde = db.query(models.Kunde).filter(models.Kunde.id == kunde_id).first()
    if not db_kunde:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    db.delete(db_kunde)
    db.commit()
    return {"message": f"Kunde {kunde_id} gelöscht"}

# Analog für: /fahrzeuge, /werkstatt, /auftraege
```


## 🚀 Wie starte ich das Projekt?

### 1. Docker Services starten
```bash
cd ProjectSWTM-develop
docker compose up -d
```

### 2. Testdaten einfügen (optional)
```bash
docker compose exec backend python seed_data.py
```

### 3. API testen
- Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:5173

### 4. Datenbank prüfen
```bash
docker compose exec db psql -U postgres -d fahrzeugservice
\dt           # Tabellen anzeigen
SELECT * FROM kunde;
SELECT * FROM fahrzeug;
SELECT * FROM auftrag;
```

---


## 🎯 Sprint 1 Ergebnis

✅ **DoD** 

DB verbunden  ✅        `docker compose exec db psql` funktioniert |
REST-API testbar  ✅     Swagger UI zeigt alle Endpoints |
CRUD vollständig  ✅     CREATE, READ, UPDATE, DELETE für alle Ressourcen |
Testdaten vorhanden  ✅ `seed_data.py` hat Daten eingefügt |
Dokumentation  ✅        Diese Datei + Swagger UI |

---

**Abschluss:** Sprint 1 (US1.5) ist **vollständig implementiert** und **getestet**! 🎉
**Datum:** 09.11.2025
**Entwickler:** Mohammed Al-Otaibi
