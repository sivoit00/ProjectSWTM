# Fahrzeugservice Backend – ProjectSWTM

Dies ist ein Projekt im Rahmen des Moduls **Softwaretechnik**.  
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
| Backend | 🐍 **FastAPI und Python** | REST-API Framework für schnelles Backend |
| Frontend | ⚛️ **React + TypeScript** | Moderne UI mit Vite |
| Datenbank | 🗄️ **PostgreSQL** | Relationale Datenbank |
| ORM | ⚙️ **SQLAlchemy** | Verknüpft Python-Klassen mit Datenbanktabellen |
| Container | 🐳 **Docker & Docker Compose** | Containerisierte Entwicklungsumgebung |
| Test & Doku | 🧪 **Swagger UI** | Interaktive Oberfläche für API-Tests |
| KI-Logik | 🤖 **(Geplant)** OpenAI / LangChain | Für automatische Texterkennung |

---

## 📊 Datenbankstruktur

**Tabellen:**
- `kunde` – speichert Kundendaten  
- `fahrzeug` – speichert Fahrzeugdaten  
- `werkstatt` – enthält Werkstattinformationen  
- `auftrag` – speichert Service-Aufträge  

---

## 🚀 Schnellstart mit Docker (Empfohlen)

### Voraussetzungen
- Docker installiert
- Docker Compose installiert

### Installation und Start

1. **Repository klonen:**
```bash
git clone <repository-url>
cd ProjectSWTM
```

2. **Alle Services starten:**
```bash
docker compose up -d
```

3. **Anwendung öffnen:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Dokumentation: http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Nützliche Docker-Befehle

**Container stoppen:**
```bash
docker compose down
```

**Logs anzeigen:**
```bash
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

**Datenbank-Shell öffnen:**
```bash
docker compose exec db psql -U postgres -d fahrzeugservice
```

**Backend-Shell öffnen:**
```bash
docker compose exec backend bash
```

**Datenbank zurücksetzen:**
```bash
docker compose down -v
docker compose up --build
```

---

## 🛠️ Lokale Entwicklung ohne Docker

### 1. Python Backend

1. **Python venv erstellen:**
```bash
python -m venv venv
```

2. **venv aktivieren:**
```bash
# Linux/Mac
source venv/bin/activate

# Windows PowerShell
.\venv\Scripts\Activate.ps1
```

3. **Abhängigkeiten installieren:**
```bash
pip install -r requirements.txt
```

4. **PostgreSQL lokal installieren und starten:**
```bash
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

5. **Datenbank erstellen:**
```bash
sudo -u postgres psql -c "CREATE DATABASE fahrzeugservice;"
sudo -u postgres psql -c "ALTER USER postgres WITH PASSWORD 'Aasal22!!';"
```

6. **Datenbank-Tabellen anlegen:**
```bash
python -c "from database import Base, engine; from models import *; Base.metadata.create_all(bind=engine); print('Tables created')"
```

7. **Server starten:**
```bash
uvicorn main:app --reload
```

### 2. React Frontend

1. **In Frontend-Verzeichnis wechseln:**
```bash
cd frontend
```

2. **Dependencies installieren:**
```bash
npm install
```

3. **Development Server starten:**
```bash
npm run dev
```

---

## 📁 Projektstruktur

```
ProjectSWTM/
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── services/      # API-Services
│   │   └── App.tsx        # Hauptkomponente
│   ├── Dockerfile
│   └── package.json
├── backend/
│   ├── main.py           # FastAPI Hauptdatei
│   ├── models.py         # SQLAlchemy Models
│   ├── database.py       # DB-Konfiguration
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml    # Docker Orchestrierung
└── README.md
```




## 🧪 API-Endpoints

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | `/kunden` | Alle Kunden abrufen |
| POST | `/kunden` | Neuen Kunden anlegen |
| GET | `/fahrzeuge` | Alle Fahrzeuge abrufen |
| POST | `/fahrzeuge` | Neues Fahrzeug anlegen |
| GET | `/werkstatt` | Alle Werkstätten abrufen |
| POST | `/werkstatt` | Neue Werkstatt anlegen |
| GET | `/auftraege` | Alle Aufträge abrufen |
| POST | `/auftraege` | Neuen Auftrag anlegen |

Vollständige Dokumentation: http://localhost:8000/docs

---

