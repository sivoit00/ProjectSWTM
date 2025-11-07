# Sprint 2: Login mit JWT & bcrypt

## Änderungen

### Backend (`main.py`)
1. **JWT Konfiguration**
   - `JWT_SECRET_KEY`: Geheimer Schlüssel für Token-Generierung
   - `JWT_ALGORITHM`: HS256
   - `JWT_EXPIRATION_MINUTES`: 60 Minuten

2. **Neue Imports**
   - `bcrypt`: Passwort-Hashing
   - `jose.jwt`: JWT Token-Generierung
   - `datetime`, `timedelta`: Token-Ablaufzeit

3. **Helper-Funktionen**
   - `create_access_token(data: dict)`: JWT Token mit Ablaufzeit erstellen
   - `hash_password(password: str)`: Passwort mit bcrypt hashen
   - `verify_password(plain_password, hashed_password)`: Passwort verifizieren

4. **Neue Endpoints**
   - `POST /login`: Login mit Email/Passwort, gibt JWT Token zurück
   - `POST /register`: User-Registrierung mit gehashtem Passwort

### Datenbank (`models.py`)
1. **User Model**
   - `id`: Primary Key
   - `email`: Unique, indexed (max 100 Zeichen)
   - `password_hash`: Gehashtes Passwort (max 255 Zeichen)
   - `name`: Optional (max 100 Zeichen)
   - `erstellt_am`: Datum der Erstellung

### Schemas (`schemas.py`)
1. **UserCreate**: Email, Passwort (plaintext), Name (optional)
2. **UserLogin**: Email, Passwort
3. **UserResponse**: id, email, name, erstellt_am (ohne Passwort!)
4. **Token**: access_token, token_type

### Dependencies (`requirements.txt`)
- `bcrypt==4.2.1`: Passwort-Hashing
- `python-jose[cryptography]==3.3.0`: JWT Token-Generierung

### Frontend (`frontend/src/pages/Login.tsx`)
1. **State Management**
   - `error`: Fehlermeldung anzeigen
   - `loading`: Loading-State während Login

2. **Login-Funktion**
   - `POST http://localhost:8000/login` mit Email/Passwort
   - Token in `localStorage.setItem("token", ...)` speichern
   - Redirect zu `/home` bei Erfolg
   - Fehlermeldung anzeigen bei Fehler

3. **UI-Updates**
   - Error-Message Box (rot mit Border)
   - Loading-State im Button ("Logging in...")
   - Disabled-Button während Login

## Sicherheit
- ✅ Passwörter werden **nie im Klartext** gespeichert
- ✅ bcrypt für Passwort-Hashing (Salt + Hash)
- ✅ JWT Token mit Ablaufzeit (60 Min)
- ✅ Token im localStorage gespeichert
- ⚠️ `JWT_SECRET_KEY` sollte in Produktion als Umgebungsvariable gesetzt werden

## API-Dokumentation

### POST /login
**Request:**
```json
{
  "email": "user@example.com",
  "password": "mypassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (400):**
```json
{
  "detail": "Ungültige Email oder Passwort"
}
```

### POST /register
**Request:**
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "name": "Max Mustermann"
}
```

**Response (200):**
```json
{
  "id": 1,
  "email": "newuser@example.com",
  "name": "Max Mustermann",
  "erstellt_am": "2025-01-07"
}
```

**Response (400):**
```json
{
  "detail": "Email bereits registriert"
}
```

## Testen

### 1. User registrieren
```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test123", "name": "Test User"}'
```

### 2. Login durchführen
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test123"}'
```

### 3. Frontend Login testen
1. Browser öffnen: `http://localhost:5173`
2. Email und Passwort eingeben
3. "Sign in" klicken
4. Bei Erfolg: Weiterleitung zu `/home`
5. Token im Browser-DevTools → Application → Local Storage prüfen

## Nächste Schritte (Sprint 3)
- Token-Validierung für geschützte Endpoints
- Logout-Funktion (Token löschen)
- Token-Refresh (neue Token ohne erneutes Login)
- Geschützte Routes im Frontend (AuthGuard)
