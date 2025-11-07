# Sprint 5: Automatische Kundenerstellung bei Registrierung

## Ziel
Bei der Registrierung soll automatisch ein Kunde-Datensatz mit gleicher Email angelegt werden, um die Verknüpfung zwischen User und Kunde herzustellen.

## Problem vorher
- User und Kunde waren getrennte Tabellen
- Nach Registrierung musste manuell ein Kunde angelegt werden
- Verknüpfung nur über Email-Matching möglich
- Dashboard zeigte nur Dummy-Daten

## Lösung
Automatische Kundenerstellung im `/register` Endpoint + User-Info API für Dashboard.

---

## Umgesetzte Features

### 1. Erweiterter Register Endpoint (`main.py`)

**Route:** `POST /register`

**Neue Funktionalität:**
```python
@app.post("/register", response_model=schemas.UserResponse)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. User erstellen (wie bisher)
    # 2. NEU: Automatisch Kunde anlegen
    new_kunde = models.Kunde(
        name=user_create.name or user_create.email,
        email=user_create.email,
        telefon=None
    )
```

**Validierung:**
- ✅ Prüft ob User-Email bereits existiert
- ✅ Prüft ob Kunde-Email bereits existiert
- ✅ HTTPException 400 bei Duplikaten

**Ablauf:**
1. Email-Duplikat-Check (User + Kunde)
2. User erstellen mit gehashtem Passwort
3. User in DB committen
4. **Kunde automatisch anlegen** mit gleicher Email
5. Kunde in DB committen
6. UserResponse zurückgeben

### 2. User-Info Endpoint (`main.py`)

**Route:** `GET /me`

**Rückgabe:**
```json
{
  "user": {
    "id": 1,
    "email": "max@example.com",
    "name": "Max Mustermann"
  },
  "kunde": {
    "id": 5,
    "name": "Max Mustermann",
    "email": "max@example.com",
    "telefon": null
  },
  "stats": {
    "fahrzeuge": 2,
    "auftraege": 3
  }
}
```

**Funktionalität:**
- ✅ JWT Token validieren mit `get_current_user()`
- ✅ Kunde über Email finden
- ✅ Anzahl Fahrzeuge zählen
- ✅ Anzahl Aufträge über Fahrzeug-Beziehung zählen
- ✅ Fallback wenn kein Kunde existiert (stats = 0)

### 3. Dashboard mit echten User-Daten (`Dashboard.tsx`)

**Neue Features:**
- ✅ `useEffect()` Hook zum Laden der User-Info
- ✅ API Call zu `GET /me` mit JWT Token
- ✅ Loading State während API Request
- ✅ Personalisierte Begrüßung: "Willkommen zurück, Max!"
- ✅ Email als Untertitel

**Stats-Karten aktualisiert:**
| Karte | Vorher | Nachher |
|-------|--------|---------|
| Kunden | Dummy "142" | "Mein Konto: Aktiv/Neu" |
| Fahrzeuge | Dummy "89" | Echte Anzahl aus API |
| Aufträge | Dummy "56" | Echte Anzahl aus API |
| Werkstätten | Dummy "12" | "Status: Aktiv/-" |

**TypeScript Interface:**
```typescript
interface UserInfo {
  user: { id, email, name }
  kunde: { id, name, email, telefon } | null
  stats: { fahrzeuge, auftraege }
}
```

---

## Technische Details

### Email-Verknüpfung
```
User.email (Login) <--> Kunde.email (Geschäftsdaten)
```

- Beide Tabellen haben `email` Spalte
- Bei Registrierung: User.email = Kunde.email
- Bei Aufträge-Abfrage: Kunde über Email matchen

### Duplicate Check
```python
# User-Check
existing_user = db.query(models.User).filter(
    models.User.email == email
).first()

# Kunde-Check
existing_kunde = db.query(models.Kunde).filter(
    models.Kunde.email == email
).first()
```

### Stats-Berechnung
```python
# Fahrzeuge zählen
fahrzeuge_count = db.query(models.Fahrzeug).filter(
    models.Fahrzeug.kunde_id == kunde.id
).count()

# Aufträge zählen (über Fahrzeug-Join)
auftraege_count = db.query(models.Auftrag).join(
    models.Fahrzeug
).filter(
    models.Fahrzeug.kunde_id == kunde.id
).count()
```

---

## Akzeptanzkriterien ✅

| Kriterium | Status | Details |
|-----------|--------|---------|
| Automatische Kundenerstellung | ✅ | Nach Registrierung existiert Kunde-Eintrag |
| Login zeigt Daten | ✅ | Dashboard zeigt Name, Email, Stats |
| Keine Duplicate-Kunden | ✅ | Email-Check für User UND Kunde |
| Dokumentation | ✅ | SPRINT_5_AENDERUNGEN.md erstellt |

---

## Testcases

### Test 1: Neue Registrierung
**Schritte:**
1. POST `/register` mit neuer Email
2. Prüfen: User erstellt
3. Prüfen: Kunde mit gleicher Email erstellt
4. Login mit User
5. Dashboard öffnen
6. Erwartung: Name + Email angezeigt, Stats = 0

**Ergebnis:** ✅ User + Kunde werden erstellt

### Test 2: Duplicate Email
**Schritte:**
1. POST `/register` mit Email "test@example.com"
2. POST `/register` ERNEUT mit "test@example.com"
3. Erwartung: HTTP 400 "Email bereits registriert"

**Ergebnis:** ✅ Fehler korrekt

### Test 3: Dashboard mit Daten
**Schritte:**
1. User mit Fahrzeugen + Aufträgen erstellen
2. Login
3. Dashboard öffnen
4. Erwartung: Echte Zahlen statt Dummy-Daten

**Ergebnis:** ✅ Stats korrekt geladen

---

## API Dokumentation

### POST /register
**Request:**
```json
{
  "email": "max@example.com",
  "password": "securepassword",
  "name": "Max Mustermann"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "max@example.com",
  "name": "Max Mustermann",
  "erstellt_am": "2025-11-07"
}
```

**Response (400):**
```json
{
  "detail": "Email bereits registriert"
}
```
oder
```json
{
  "detail": "Kunde mit dieser Email existiert bereits"
}
```

### GET /me
**Headers:**
```
Authorization: Bearer <jwt_token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "max@example.com",
    "name": "Max Mustermann"
  },
  "kunde": {
    "id": 5,
    "name": "Max Mustermann",
    "email": "max@example.com",
    "telefon": null
  },
  "stats": {
    "fahrzeuge": 2,
    "auftraege": 3
  }
}
```

**Response (401):**
```json
{
  "detail": "Nicht authentifiziert"
}
```

---

## Änderungen im Detail

### Backend (`main.py`)
**Zeilen ~120-156:** Register Endpoint erweitert
- Kunde-Duplikat-Check hinzugefügt
- Automatische Kunde-Erstellung nach User
- Name oder Email als Fallback für Kunde.name

**Zeilen ~158-200:** Neuer `/me` Endpoint
- JWT-geschützt mit `get_current_user()`
- Kunde-Lookup über Email
- Stats-Berechnung mit SQLAlchemy Count

### Frontend (`Dashboard.tsx`)
**Zeilen 1-50:** State & API Integration
- `useState<UserInfo>` für User-Daten
- `useEffect()` für initiales Laden
- `fetchUserInfo()` Funktion mit JWT Authorization

**Zeilen 60-80:** Dynamische Stats
- Stats basieren auf API-Response
- Fallback-Werte wenn keine Daten

**Zeilen 90-95:** Personalisierte Header
- Name in Überschrift wenn vorhanden
- Email als Untertitel

---

## Vorteile der Lösung

1. **Automatisierung:** Keine manuellen Schritte nach Registrierung
2. **Konsistenz:** User und Kunde immer synchron
3. **UX:** Personalisiertes Dashboard ab erstem Login
4. **Datenintegrität:** Duplicate-Checks verhindern Fehler
5. **Skalierbar:** Einfach um weitere Felder erweiterbar

---

## Bekannte Einschränkungen

- Telefon-Nummer fehlt bei Registrierung (kann später ergänzt werden)
- Keine Foreign Key Beziehung User↔Kunde (nur Email-Matching)
- Dashboard "Letzte Aktivitäten" noch Dummy-Daten
- Kunde kann nicht gelöscht werden wenn User existiert (keine Cascade)

---

## Nächste Schritte (Sprint 6)

- [ ] User.kunde_id Foreign Key hinzufügen
- [ ] Telefon-Feld im Register-Formular
- [ ] Letzte Aktivitäten aus echten DB-Daten
- [ ] User-Profil bearbeiten Funktion
- [ ] Kunde-Details-Seite
- [ ] Fahrzeug-Verwaltung für User
