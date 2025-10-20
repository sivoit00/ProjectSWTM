# Fahrzeugservice Backend – ProjectSWTM

Dies ist ein Backend-Projekt im Rahmen des Moduls **Softwaretechnik**.  
Ziel ist die Entwicklung eines einfachen **Fahrzeugservice-Systems**, das  
Kunden, Fahrzeuge, Werkstätten und Aufträge verwaltet.  
Das System enthält außerdem einen **KI-Endpunkt**, der automatisch Aufträge erstellen kann.

---

## 🧩 Projektübersicht

Das System soll Kundendaten, Fahrzeuge und Werkstätten speichern  
und automatisch Aufträge generieren, wenn ein Kunde ein Problem meldet.

Beispiel:
> „Ich hatte gestern einen Motorschaden, bitte prüfen."

Der KI-Endpunkt erstellt dann automatisch einen neuen Auftrag mit Status **offen**,  
verknüpft ihn mit der passenden Werkstatt und fügt ihn in die Datenbank ein.

---

## 🧱 Technologien

| Ebene | Technologie | Beschreibung |
|--------|--------------|--------------|
| Backend | 🐍 **FastAPI** | REST-API Framework für schnelles Backend |
| Datenbank | 🗄️ **PostgreSQL** | Relationale Datenbank |
| ORM | ⚙️ **SQLAlchemy** | Verknüpft Python-Klassen mit Datenbanktabellen |
| Test & Doku | 🧪 **Swagger UI** | Interaktive Oberfläche für API-Tests |
| KI-Logik | 🤖 **(Geplant)** OpenAI / LangChain | Für automatische Texterkennung |

---

## 📊 Datenbankstruktur

**Tabellen:**
- `kunde` – speichert Kundendaten  
- `fahrzeug` – speichert Fahrzeugdaten  
- `werkstatt` – enthält Werkstattinformationen  
- `auftrag` – speichert Service-Aufträge  
- `ki_aktionen` – speichert automatisierte Aktionen

---

## Schnellstart

1. Python venv erstellen (falls noch nicht):

```powershell
python -m venv venv
```

2. venv aktivieren:

```powershell
.\venv\Scripts\Activate.ps1
```

3. Abhängigkeiten installieren:

```powershell
pip install -r requirements.txt
```

4. Datenbank-Tabellen anlegen:

```powershell
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine); print('create_all executed')"
```

5. Server starten:

```powershell
uvicorn main:app --reload
```

6. OpenAPI UI öffnen:

```
http://127.0.0.1:8000/docs
```