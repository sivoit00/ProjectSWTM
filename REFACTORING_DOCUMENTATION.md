# 📋 Projekt-Refaktorierung Dokumentation

**Branch:** `feature/US2.6/Structure`  
**Datum:** 11. November 2025  
**Ziel:** Saubere Modulstruktur für bessere Teamarbeit und Wartbarkeit

---

## 🎯 Überblick

Das Projekt wurde vollständig refaktoriert, um eine **Clean Architecture** (Backend) und **Component-Based Architecture** (Frontend) zu implementieren. Alle Funktionen bleiben unverändert - nur die Struktur wurde verbessert.

---

## 🔧 Backend-Refaktorierung

### ❌ Vorher (Monolithisch)
```
backend/
├── main.py              # Alle Endpoints in einer Datei (~230 Zeilen)
├── models.py
├── schemas.py
└── database.py
```

**Probleme:**
- Alle API-Endpoints in `main.py`
- Geschäftslogik und HTTP-Layer vermischt
- Schwierig für parallele Entwicklung
- Keine klare Trennung der Verantwortlichkeiten

---

### ✅ Nachher (Clean Architecture)

```
backend/
├── main.py                    # Nur Router-Registrierung (~35 Zeilen)
│
├── routes/                    # HTTP-Endpoints (API-Layer)
│   ├── __init__.py
│   ├── kunden.py             # GET/POST /kunden
│   ├── fahrzeuge.py          # GET/POST /fahrzeuge
│   ├── auftraege.py          # GET/POST /auftraege
│   ├── werkstaetten.py       # GET/POST /werkstatt
│   ├── ki.py                 # POST /ki/auftrag
│   └── openai_route.py       # POST /openai/chat
│
├── services/                  # Geschäftslogik (Business Layer)
│   ├── __init__.py
│   ├── kunden_service.py
│   ├── fahrzeug_service.py
│   ├── auftrag_service.py
│   ├── werkstatt_service.py
│   ├── ki_service.py
│   └── openai_service.py
│
├── models.py                  # Datenbankmodelle (unverändert)
├── schemas.py                 # Pydantic-Schemas (unverändert)
└── database.py                # DB-Konfiguration (unverändert)
```

---

### 📊 Backend-Architektur (3-Schichten-Modell)

```
┌─────────────────────────────────────────┐
│         routes/ (HTTP-Layer)            │
│  - Empfängt HTTP-Requests               │
│  - Validiert Input (Pydantic)           │
│  - Ruft Services auf                    │
│  - Gibt HTTP-Response zurück            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      services/ (Business Layer)         │
│  - Geschäftslogik                       │
│  - Validierung                          │
│  - Datenverarbeitung                    │
│  - Ruft Datenbank auf                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        models.py (Data Layer)           │
│  - SQLAlchemy Models                    │
│  - Datenbankzugriff                     │
└─────────────────────────────────────────┘
```

---

### 🔍 Backend-Beispiel: Kunden-Endpoint

#### **routes/kunden.py** (HTTP-Layer)
```python
from fastapi import APIRouter, Depends
from services.kunden_service import KundenService

router = APIRouter(prefix="/kunden", tags=["Kunden"])

@router.get("", response_model=list[schemas.Kunde])
def get_kunden(db: Session = Depends(get_db)):
    """Alle Kunden abrufen"""
    return KundenService.get_all_kunden(db)
```

#### **services/kunden_service.py** (Business Layer)
```python
class KundenService:
    @staticmethod
    def get_all_kunden(db: Session):
        """Alle Kunden abrufen"""
        return db.query(models.Kunde).all()
```

#### **main.py** (Router-Registrierung)
```python
from routes import kunden, fahrzeuge, auftraege, werkstaetten, ki, openai_route

app = FastAPI(title="Fahrzeugservice API")

app.include_router(kunden.router)
app.include_router(fahrzeuge.router)
app.include_router(auftraege.router)
app.include_router(werkstaetten.router)
app.include_router(ki.router)
app.include_router(openai_route.router)
```

---

## 🔧 Wichtige Backend-Änderungen

### 1. Trennung: Aufträge ↔ Werkstätten
- **Vorher:** Beide in einer Datei vermischt
- **Nachher:** Separate Dateien
  - `routes/auftraege.py` → `/auftraege` Endpoints
  - `routes/werkstaetten.py` → `/werkstatt` Endpoints
  - `services/auftrag_service.py` → Auftrags-Logik
  - `services/werkstatt_service.py` → Werkstatt-Logik

### 2. Trennung: KI ↔ OpenAI
- **Vorher:** Beide in einer Datei
- **Nachher:** Separate Dateien
  - `routes/ki.py` → `/ki/auftrag` (KI-Auftragserstellung)
  - `routes/openai_route.py` → `/openai/chat` (Chat)
  - `services/ki_service.py` → KI-Logik
  - `services/openai_service.py` → OpenAI-Logik

### 3. Dependencies hinzugefügt
**requirements.txt:**
```
pydantic-settings==2.0.3
email-validator==2.1.0
```
Grund: Pydantic v2 Kompatibilität

---

## 🎨 Frontend-Refaktorierung

### ❌ Vorher (Unstrukturiert)
```
frontend/src/
├── App.tsx              # Alt
├── App_new.tsx          # Neu (Duplikat!)
├── pages/
│   ├── Dashboard.tsx
│   ├── KundenPage.tsx
│   ├── Chat.tsx         # Duplikat!
│   ├── ChatPage.tsx     # Duplikat!
│   └── ...
├── services/
│   ├── api.ts           # Alt
│   └── api_new.ts       # Neu (Duplikat!)
└── components/
    ├── ApiPage.tsx
    ├── common/
    └── features/        # Leer
```

**Probleme:**
- Duplikate: `App.tsx` / `App_new.tsx`
- Duplikate: `api.ts` / `api_new.ts`
- Pages direkt im `pages/` Ordner ohne Unterordner
- Unklare Struktur

---

### ✅ Nachher (Component-Based)

```
frontend/src/
├── App.tsx                   # ✅ Nur eine Version
│
├── pages/                    # Seiten in eigenen Ordnern
│   ├── Dashboard/
│   │   └── index.tsx
│   ├── Kunden/
│   │   └── index.tsx
│   ├── Fahrzeuge/
│   │   └── index.tsx
│   ├── Auftraege/
│   │   └── index.tsx
│   ├── Werkstaetten/
│   │   └── index.tsx
│   ├── Chat/
│   │   └── index.tsx
│   └── Home/
│       └── index.tsx
│
├── components/               # Wiederverwendbare Komponenten
│   ├── common/
│   │   ├── Sidebar.tsx
│   │   ├── PageHeader.tsx
│   │   ├── LoadingSpinner.tsx
│   │   ├── ErrorMessage.tsx
│   │   ├── ApiPage.tsx
│   │   └── index.ts
│   └── forms/               # Bereit für Formulare
│
├── services/                 # API-Services
│   └── api.ts               # ✅ Nur eine Version
│
├── layouts/
│   └── MainLayout.tsx
│
├── types/
│   └── index.ts
│
├── hooks/                    # Bereit für Custom Hooks
├── utils/                    # Bereit für Hilfsfunktionen
└── main.tsx
```

---

## 🔄 Frontend-Änderungen

### 1. Duplikate entfernt
| Vorher | Nachher |
|--------|---------|
| `App.tsx` (alt) + `App_new.tsx` | ✅ `App.tsx` |
| `api.ts` (alt) + `api_new.ts` | ✅ `api.ts` |
| `Chat.tsx` + `ChatPage.tsx` | ✅ `Chat/index.tsx` |

### 2. Pages reorganisiert
Jede Page hat jetzt ihren eigenen Ordner:
- `Dashboard.tsx` → `Dashboard/index.tsx`
- `KundenPage.tsx` → `Kunden/index.tsx`
- `FahrzeugePage.tsx` → `Fahrzeuge/index.tsx`
- usw.

**Vorteil:** Jede Page kann eigene Sub-Komponenten haben

### 3. Import-Pfade aktualisiert
```tsx
// Vorher
import { PageHeader } from '../components/common';
import { kundenAPI } from '../services/api_new';

// Nachher
import { PageHeader } from '../../components/common';
import { kundenAPI } from '../../services/api';
```

### 4. Ordner vorbereitet
- ✅ `components/forms/` - Für zukünftige Formulare
- ✅ `hooks/` - Für Custom React Hooks
- ✅ `utils/` - Für Hilfsfunktionen

---

## 📡 API-Endpoints (unverändert)

Alle Endpoints funktionieren wie vorher:

### Kunden
- `GET /kunden` - Alle Kunden
- `POST /kunden` - Kunde erstellen
- `GET /kunden/{id}/fahrzeuge` - Fahrzeuge eines Kunden

### Fahrzeuge
- `GET /fahrzeuge` - Alle Fahrzeuge
- `POST /fahrzeuge` - Fahrzeug erstellen
- `GET /fahrzeuge/{id}/auftraege` - Aufträge eines Fahrzeugs

### Werkstätten
- `GET /werkstatt` - Alle Werkstätten
- `POST /werkstatt` - Werkstatt erstellen

### Aufträge
- `GET /auftraege` - Alle Aufträge
- `POST /auftraege` - Auftrag erstellen
- `GET /auftraege/status/{status}` - Aufträge nach Status

### KI
- `POST /ki/auftrag` - KI-gestützter Auftrag
- `POST /openai/chat` - OpenAI Chat

### Dokumentation
- `GET /docs` - Swagger UI (http://localhost:8000/docs)

---

## 🚀 Dienste

Alle Dienste laufen über Docker Compose:

| Service | Port | Status |
|---------|------|--------|
| **Backend** (FastAPI) | 8000 | ✅ Running |
| **Frontend** (Vite) | 5173 | ✅ Running |
| **Database** (PostgreSQL) | 5432 | ✅ Running |
| **Keycloak** | 8080 | ✅ Running |

**Starten:**
```bash
docker-compose up -d
```

**Rebuild:**
```bash
docker-compose up --build -d
```

---

## ✅ Was funktioniert weiterhin

- ✅ Alle API-Endpoints
- ✅ Datenbankzugriffe
- ✅ CRUD-Operationen (Create, Read, Update, Delete)
- ✅ Frontend-Routing
- ✅ API-Kommunikation
- ✅ Keycloak-Integration (vorbereitet)
- ✅ OpenAI-Chat

---

## 🎯 Vorteile der neuen Struktur

### Backend
1. **Teamarbeit:** Entwickler können parallel an verschiedenen Services arbeiten
2. **Wartbarkeit:** Klare Trennung → einfacher zu verstehen
3. **Testbarkeit:** Services können einzeln getestet werden
4. **Skalierbarkeit:** Neue Endpoints einfach hinzufügen

### Frontend
1. **Übersichtlichkeit:** Jede Page in eigenem Ordner
2. **Wiederverwendbarkeit:** Common Components zentral
3. **Erweiterbarkeit:** Prepared für Forms, Hooks, Utils
4. **Konsistenz:** Ein API-Service, ein App.tsx

---

## 📝 Nächste Schritte (Optional)

### Backend
- [ ] Unit Tests für Services schreiben
- [ ] API Rate Limiting hinzufügen
- [ ] Logging verbessern
- [ ] Error Handling erweitern

### Frontend
- [ ] Create/Edit Modals für CRUD implementieren
- [ ] Form Validation (React Hook Form + Zod)
- [ ] Pagination für große Datenmengen
- [ ] Toast Notifications
- [ ] Keycloak-Login aktivieren

---

## 🔍 Wie finde ich was?

### "Ich will einen neuen API-Endpoint hinzufügen"
1. Service-Logik in `backend/services/[name]_service.py` schreiben
2. Route in `backend/routes/[name].py` erstellen
3. Router in `backend/main.py` registrieren

### "Ich will eine neue Page im Frontend"
1. Ordner erstellen: `frontend/src/pages/NewPage/`
2. Component: `frontend/src/pages/NewPage/index.tsx`
3. Route in `frontend/src/App.tsx` hinzufügen

### "Ich will eine wiederverwendbare Komponente"
→ `frontend/src/components/common/MyComponent.tsx`

### "Ich will eine API-Funktion hinzufügen"
→ `frontend/src/services/api.ts`

---

## 🎓 Architektur-Prinzipien

### Backend: Clean Architecture
- **Single Responsibility:** Jede Datei hat eine Aufgabe
- **Separation of Concerns:** Routes ↔ Services ↔ Models getrennt
- **Dependency Injection:** Database Session über `Depends(get_db)`

### Frontend: Component-Based
- **Atomic Design:** Pages → Layouts → Components
- **Separation:** Pages für Logik, Components für UI
- **DRY (Don't Repeat Yourself):** Common Components

---

## 📞 Support

**Probleme mit der Struktur?**
- Backend API-Dokumentation: http://localhost:8000/docs
- Frontend läuft: http://localhost:5173

**Container neu starten:**
```bash
docker-compose down
docker-compose up --build -d
```

---

**✅ Alle Funktionen bleiben gleich - nur die Struktur ist besser!**
