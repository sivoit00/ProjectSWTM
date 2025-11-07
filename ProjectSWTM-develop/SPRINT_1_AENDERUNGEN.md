# Sprint 1 - Änderungen und Implementierung

**Status:** ✅ Abgeschlossen  
**Datum:** 6. November 2025  
**Ziel:** API- und DB-Struktur einrichten, um spätere Integration vorzubereiten

---

## 📋 Übersicht

Sprint 1 fokussiert sich auf die Einrichtung einer vollständigen REST-API mit CRUD-Operationen für alle Hauptentitäten des Fahrzeugservice-Systems.

---

## 🔧 Implementierte Features

### 1. **Backend API-Struktur (FastAPI)**

#### **Kunden-Endpoints** (`/kunden`)
- `GET /kunden` - Alle Kunden abrufen
- `GET /kunden/{kunde_id}` - Einzelnen Kunden abrufen
- `POST /kunden` - Neuen Kunden anlegen
- `PUT /kunden/{kunde_id}` - Kundendaten aktualisieren
- `DELETE /kunden/{kunde_id}` - Kunden löschen

#### **Fahrzeug-Endpoints** (`/fahrzeuge`)
- `GET /fahrzeuge` - Alle Fahrzeuge abrufen
- `GET /fahrzeuge/{fahrzeug_id}` - Einzelnes Fahrzeug abrufen
- `POST /fahrzeuge` - Neues Fahrzeug anlegen
- `PUT /fahrzeuge/{fahrzeug_id}` - Fahrzeugdaten aktualisieren
- `DELETE /fahrzeuge/{fahrzeug_id}` - Fahrzeug löschen

#### **Werkstatt-Endpoints** (`/werkstatt`)
- `GET /werkstatt` - Alle Werkstätten abrufen
- `GET /werkstatt/{werkstatt_id}` - Einzelne Werkstatt abrufen
- `POST /werkstatt` - Neue Werkstatt anlegen
- `PUT /werkstatt/{werkstatt_id}` - Werkstattdaten aktualisieren
- `DELETE /werkstatt/{werkstatt_id}` - Werkstatt löschen

#### **Auftrags-Endpoints** (`/auftraege`)
- `GET /auftraege` - Alle Aufträge abrufen
- `GET /auftraege/{auftrag_id}` - Einzelnen Auftrag abrufen
- `POST /auftraege` - Neuen Auftrag anlegen
- `PUT /auftraege/{auftrag_id}` - Auftragsdaten aktualisieren
- `DELETE /auftraege/{auftrag_id}` - Auftrag löschen

---

## 🛠️ Technische Verbesserungen

### **Error-Handling**
- ✅ HTTP 404-Fehler für nicht existierende Ressourcen
- ✅ Deutsche Fehlermeldungen für bessere UX
- ✅ Beispiel: `"Kunde mit ID 123 nicht gefunden"`

### **Pydantic V2 Migration**
```python
# Vorher (Pydantic V1)
class Config:
    orm_mode = True

# Nachher (Pydantic V2)
class Config:
    from_attributes = True
```

### **Code-Dokumentation**
- ✅ Docstrings für alle API-Endpoints
- ✅ Swagger UI Auto-Dokumentation unter http://localhost:8000/docs

---

## 📁 Geänderte Dateien

### **main.py**
- Erweitert um vollständige CRUD-Operationen
- Hinzugefügt: GET-Endpoints mit ID-Parameter
- Hinzugefügt: PUT-Endpoints für Updates
- Hinzugefügt: DELETE-Endpoints
- Hinzugefügt: Error-Handling mit HTTPException

### **schemas.py**
- Migriert: `orm_mode = True` → `from_attributes = True`
- Betroffen: Kunde, Fahrzeug, Werkstatt, Auftrag, KIAktionSchema

---

## 🗄️ Datenbankstruktur

### **Beziehungen (Relationships)**
```
Kunde (1) ──→ (N) Fahrzeug
Fahrzeug (1) ──→ (N) Auftrag
Werkstatt (1) ──→ (N) Auftrag
```

### **Tabellen**
- `kunde` - Kundenstammdaten (name, email, telefon)
- `fahrzeug` - Fahrzeugdaten (marke, modell, baujahr, kunde_id)
- `werkstatt` - Werkstattinformationen (name, adresse, plz, ort)
- `auftrag` - Service-Aufträge (beschreibung, status, fahrzeug_id, werkstatt_id)

---

## 🧪 Testing

### **API-Tests über Swagger UI**
1. Browser öffnen: http://localhost:8000/docs
2. Teste alle Endpoints interaktiv
3. Beispiel-Request für neuen Kunden:
```json
{
  "name": "Max Mustermann",
  "email": "max@example.com",
  "telefon": "+49 123 456789"
}
```

---

## 🚀 Deployment

### **Docker Services**
```bash
docker-compose up -d
```

**Laufende Container:**
- `projectswtm-develop-db-1` - PostgreSQL auf Port 5432
- `projectswtm-develop-backend-1` - FastAPI auf Port 8000
- `projectswtm-develop-frontend-1` - Vite auf Port 5173

---

## 📊 Status

| Feature | Status |
|---------|--------|
| CRUD für Kunden | ✅ Abgeschlossen |
| CRUD für Fahrzeuge | ✅ Abgeschlossen |
| CRUD für Werkstätten | ✅ Abgeschlossen |
| CRUD für Aufträge | ✅ Abgeschlossen |
| Error-Handling | ✅ Abgeschlossen |
| Pydantic V2 Migration | ✅ Abgeschlossen |
| API-Dokumentation | ✅ Abgeschlossen |
| Datenbank-Integration | ✅ Abgeschlossen |

---

## ⏭️ Nächste Schritte (Sprint 2)

Sprint 2 wird sich mit **Echtzeit-Chat-Funktionalität** beschäftigen:
- WebSocket/SSE Integration
- Chat-Nachrichten in Echtzeit anzeigen
- Frontend-Komponente für Chat-Interface

---

## 🔗 Nützliche Links

- API-Dokumentation: http://localhost:8000/docs
- Backend-API: http://localhost:8000
- Frontend: http://localhost:5173
- PostgreSQL: localhost:5432

---

**Erstellt:** 6. November 2025  
**Sprint:** 1 von 3  
**Team:** ProjectSWTM Development Team
