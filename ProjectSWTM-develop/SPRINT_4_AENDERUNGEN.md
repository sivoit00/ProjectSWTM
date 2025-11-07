# Sprint 4: Visualisierung & User-spezifische Aufträge

## Ziel
Eingeloggte Nutzer sollen ihre eigenen Aufträge visualisiert sehen können mit Diagrammen und Tabellen.

## Umgesetzte Features

### 1. Backend JWT Authentication (`main.py`)

**JWT Dependency Funktion:**
```python
def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db))
```
- ✅ Token aus Authorization Header extrahieren (`Bearer <token>`)
- ✅ JWT Token mit `jose.jwt.decode()` validieren
- ✅ `user_id` aus Token Payload extrahieren
- ✅ User aus Datenbank laden
- ✅ HTTPException 401 bei ungültigem/fehlendem Token
- ✅ Fehlerbehandlung für JWTError und ValueError

**Neue Imports:**
- `from fastapi import Header`
- `from jose import JWTError`
- `from typing import Optional`

### 2. User-Aufträge Endpoint (`main.py`)

**Route:** `GET /auftraege/me`

**Ablauf:**
1. JWT Token validieren mit `get_current_user()` Dependency
2. Kunde-Datensatz über User.email finden
3. Aufträge über Fahrzeug→Kunde Beziehung laden
4. Nur Aufträge des eingeloggten Users zurückgeben

**Besonderheit:**
- User-Tabelle und Kunde-Tabelle sind getrennt
- Verknüpfung über `User.email == Kunde.email`
- Falls User keinen Kunden hat → leere Liste zurück

```python
@app.get("/auftraege/me", response_model=list[schemas.Auftrag])
def get_my_auftraege(
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
)
```

### 3. Frontend: Recharts Installation

**Installation im Container:**
```bash
docker-compose exec frontend npm install recharts
```

**Installierte Version:** recharts (39 packages hinzugefügt)

### 4. Visualisierung Seite (`pages/Visualisierung.tsx`)

**Features:**
- ✅ JWT Token aus localStorage lesen
- ✅ API Call zu `GET /auftraege/me` mit Authorization Header
- ✅ Loading State mit Spinner
- ✅ Error Handling

**Komponenten:**

#### a) Stats-Overview (4 Karten)
- Gesamt-Anzahl aller Aufträge
- Anzahl "Offen" (gelber Border)
- Anzahl "In Bearbeitung" (blauer Border)
- Anzahl "Abgeschlossen" (grüner Border)

#### b) Kreisdiagramm (PieChart)
**Bibliothek:** `recharts`

**Komponenten:**
- `<PieChart>` - Container
- `<Pie>` - Kreisdiagramm mit Labels
- `<Cell>` - Farbige Segmente
- `<Tooltip>` - Hover-Infos
- `<Legend>` - Legende

**Daten:**
```javascript
const chartData = [
  { name: "Offen", value: count, color: "#facc15" },
  { name: "In Bearbeitung", value: count, color: "#3b82f6" },
  { name: "Abgeschlossen", value: count, color: "#22c55e" }
]
```

**Features:**
- Prozentzahlen als Labels
- Nur Segmente mit Wert > 0 anzeigen
- Responsive mit `<ResponsiveContainer>`

#### c) Auftragsliste Tabelle
**Spalten:**
- ID (#123)
- Beschreibung (Text)
- Status (Badge mit Farbe)
- Erstellt am (Datum formatiert)
- Kosten (in €, grün hervorgehoben)

**Features:**
- Staggered Fade-in Animationen (framer-motion)
- Hover-Effekte auf Tabellenzeilen
- Status-Badges mit Farben (gelb/blau/grün)
- "Keine Aufträge vorhanden" Fallback

### 5. Navigation (`Sidebar.tsx` & `App.tsx`)

**Sidebar:**
- Neuer Nav-Item: Visualisierung
- Icon: `BarChart3` (Lucide React)
- Path: `/visualisierung`

**App.tsx:**
- Neue Route: `<Route path="/visualisierung" element={<Visualisierung />} />`
- Import: `import Visualisierung from "./pages/Visualisierung"`

## Technische Details

### API Request Format
```javascript
fetch("http://localhost:8000/auftraege/me", {
  headers: {
    Authorization: `Bearer ${token}`
  }
})
```

### JWT Token Flow
1. User loggt sich ein → Token in localStorage gespeichert
2. Visualisierung-Seite lädt → Token aus localStorage lesen
3. API Request mit Authorization Header
4. Backend validiert Token → extrahiert user_id
5. Aufträge des Users werden geladen

### Datenbank-Beziehungen
```
User (email) 
  ↓ (email match)
Kunde (id)
  ↓ (kunde_id)
Fahrzeug (id)
  ↓ (fahrzeug_id)
Auftrag (beschreibung, status, kosten, ...)
```

## Status-Mapping
```javascript
"Offen" → Gelb (#facc15)
"In Bearbeitung" → Blau (#3b82f6)
"Abgeschlossen" → Grün (#22c55e)
```

## UI/UX Features
- **Dark Theme:** slate-900/950 Background
- **Framer Motion:** Staggered Animations
- **Responsive:** Grid-Layout passt sich an
- **Loading States:** Spinner während API Call
- **Error Handling:** Rote Error-Box bei Fehlern
- **Empty State:** "Keine Aufträge vorhanden" Message

## Sicherheit
- ✅ JWT Token erforderlich für Zugriff
- ✅ Backend validiert Token bei jedem Request
- ✅ Nur eigene Aufträge sichtbar
- ✅ Keine Aufträge anderer User zugänglich

## Testen

### 1. User mit Aufträgen erstellen
```bash
# 1. User registrieren
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "max@example.com", "password": "test123", "name": "Max"}'

# 2. Kunde mit gleicher Email erstellen (über Swagger UI /docs)
# 3. Fahrzeug für Kunden erstellen
# 4. Auftrag für Fahrzeug erstellen
```

### 2. Frontend testen
1. Login mit `max@example.com` / `test123`
2. Sidebar → "Visualisierung" klicken
3. Prüfen:
   - Stats-Karten zeigen korrekte Zahlen
   - Kreisdiagramm zeigt Status-Verteilung
   - Tabelle zeigt alle Aufträge des Users
   - Keine Aufträge anderer User sichtbar

### 3. Auth testen
1. Logout
2. Manuell zu `/visualisierung` navigieren
3. Error-Message: "Nicht angemeldet"

## Bekannte Einschränkungen
- User und Kunde sind getrennte Tabellen (Verknüpfung über Email)
- TypeScript Warnings bei recharts (implizites any)
- Keine Protected Route Middleware (kommt in Sprint 5)
- Dashboard Stats sind noch Dummy-Daten (nicht user-spezifisch)

## Nächste Schritte (Sprint 5)
- [ ] Protected Routes für alle authentifizierten Seiten
- [ ] AuthContext für globales User-Management
- [ ] User.kunde_id Relationship in DB
- [ ] Real-time Dashboard Stats
- [ ] Auftrag-Details Modal
- [ ] Auftrag erstellen/bearbeiten Funktionen
