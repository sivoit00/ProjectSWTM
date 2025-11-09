# Verändere niemals bestehenden Code oder ändere niemals die Struktur davon, außer ich erlaube es dir.
# Benutze immer Context7 um code zu generieren 

# Tech Stack

Dieses Projekt ist eine Full-Stack-Webanwendung mit einem **FastAPI Backend** (Python, SQLAlchemy, PostgreSQL), das über REST-APIs mit einem **React Frontend** (TypeScript, Vite, Tailwind CSS) kommuniziert. Die gesamte Infrastruktur wird über **Docker Compose** orchestriert, wobei drei Services (PostgreSQL-Datenbank, FastAPI-Server auf Port 8000, Vite-Dev-Server auf Port 5173) in separaten Containern laufen.



# Todo die erledigt werden müssen
## Abgeschlossen oder noch offen = Status
du findest die zu erledingende aufgabe unter (sprint(nummer des sprintes)) und direkt darunter den status ob sie erledigt ist (Abgeschlossen / noch offen)
Bearbeite immer nur einen Sprint nach dem anderen.

# sprint 1 
## Abgeschlossen
Als Entwickler möchte ich API- und DB-Struktur einrichten, um spätere Integration vorzubereiten

**Umgesetzte Features:**
- ✅ Vollständige CRUD-Operationen (Create, Read, Update, Delete) für alle Entitäten
- ✅ REST-Endpoints: Kunden, Fahrzeuge, Werkstätten, Aufträge
- ✅ GET-Endpoints für Listen und einzelne Ressourcen mit ID
- ✅ PUT-Endpoints zum Aktualisieren bestehender Daten
- ✅ DELETE-Endpoints zum Löschen von Ressourcen
- ✅ Error-Handling mit 404-Status für nicht existierende Ressourcen
- ✅ Deutsche Fehlermeldungen für bessere UX
- ✅ Pydantic V2 Migration: `orm_mode` → `from_attributes`
- ✅ SQLAlchemy Models mit Relationships (Kunde→Fahrzeug, Fahrzeug→Auftrag, Werkstatt→Auftrag)
- ✅ Datenbankanbindung über PostgreSQL (Docker Container)
- ✅ API-Dokumentation verfügbar unter http://localhost:8000/docs
# sprint 2
## noch offen

Login 
In PostgreSQL sicherstellen, dass es eine Tabelle gibt, in der Nutzer gespeichert sind.
Falls keine existiert: Kunde-Tabelle verwenden.
Wichtig: Passwort muss gehasht (bcrypt) gespeichert werden, kein Klartext.

FastAPI Login-Endpoint erstellen:

Route: POST /login

Parameter: email, password

Ablauf:

Nutzer in DB suchen

Passwort mit bcrypt.verify prüfen

Wenn korrekt → JWT Token generieren

Return: { token: <jwt_token> }

Fehlerfall → HTTP 400 "Login fehlgeschlagen"

FastAPI Konfiguration ergänzen:

JWT Secret Key definieren

Router in main.py includen

React Login-Formular verknüpfen:

Beim Klick auf "Sign in" soll ein fetch() an /login gesendet werden.

Wenn Login erfolgreich: localStorage.setItem("token", token) speichern

Danach Redirect auf /dashboard

Optional: Middleware in React, die prüft:

Ist token in localStorage?

Wenn nein → redirect /login

Bitte den Code direkt vollständig liefern, nicht nur erklären.
Keine Dummy-Implementierungen.
Keine Klartext-Passwörter.
JWT & bcrypt müssen wirklich funktionieren.

# sprint 3
## noch offen 
Sprint 3 – Navigation & Seitenstruktur

# sprint 4

Backend Informationen:

Es gibt bereits eine Datenbank mit Tabellen für kunde, fahrzeug, auftrag, etc.

Ein eingeloggter Benutzer bekommt ein JWT im localStorage.

API Endpoints existieren, u.a.:
GET /auftraege → gibt alle Aufträge zurück.

Was ich jetzt brauche (bitte programmieren):
1. Backend

Erstelle einen neuen Endpoint:

GET /auftraege/user/{user_id}


Dieser Endpoint soll nur die Aufträge des eingeloggten Nutzers zurückgeben.
Nutze das JWT, um die User-ID zu identifizieren.

2. Frontend

Verwende React + Vite.

Erstelle eine neue Seite: src/pages/Visualisierung.jsx

Hole die Auftragsdaten des Nutzers mit dem gespeicherten Token (Authorization: Bearer TOKEN)

Stelle die Daten in zwei Bereichen dar:

a) Diagramm

Installiere eine Diagramm-Bibliothek:

npm install recharts


Erstelle ein Kreisdiagramm (PieChart), das zeigt:

Anzahl „offen“

Anzahl „in Bearbeitung“

Anzahl „abgeschlossen“

b) Auftragsliste

Tabelle oder Karten, die anzeigen:

Beschreibung

Werkstatt

Erstellungsdatum

Status

Kosten (falls vorhanden)

3. Navigation

Auf der Home-Seite existiert bereits ein Dashboard-Layout.

Füge einen Button oder Icon hinzu:

Visualisierung


Beim Klick → leite zur neuen Seite /visualisierung weiter.

4. Bedingungen

Die Visualisierungs-Seite soll nur sichtbar sein, wenn der Nutzer eingeloggt ist.

Wenn kein Token vorhanden → redirect zu /login.

Akzeptanzkriterien

Die Visualisierungs-Seite lädt automatisch Daten aus dem Backend.

Der Status der Aufträge wird im Diagramm korrekt angezeigt.

Alle Daten stammen aus der echten Datenbank.

Navigation funktioniert ohne Fehler.

Bitte gib mir den fertigen Code:

Backend Route

Frontend React-Komponenten

Navigation/Button

Beispiel für Diagramm & Tabelle

Copilot soll Codevorschläge für unser **Full-Stack Fahrzeugservice-System** liefern, die **lesbar, sicher und wartbar** sind.  
Diese Standards gelten für FastAPI Backend, React Frontend und Docker-Infrastruktur.


# sprint 5
Wenn sich ein neuer Benutzer registriert (/register), soll automatisch ein Eintrag in der Kunde-Tabelle erstellt werden, damit der User nach Login direkt mit seinen Daten arbeiten kann.

Was aktuell passiert

/register erstellt nur einen User in der User-Tabelle.

In der Kunde-Tabelle muss der Eintrag manuell erstellt werden.

Dadurch sieht man im Dashboard keine Fahrzeuge / Aufträge nach Login.

Was umgebaut werden soll

Beim erfolgreichen Registrieren:

User wird wie gewohnt erstellt (inkl. Passwort-Hashing)

Direkt danach:

Ein Kunde-Datensatz wird automatisch angelegt

Attribute wie:

{
  "name": "<Vorname Nachname oder Email>",
  "email": "<email des Users>",
  "telefon": null (erstmal optional)
}


Die Verknüpfung läuft über Email (User.email = Kunde.email)

## Backend Aufgaben

Modify /register Endpoint in FastAPI:

Nach erfolgreichem Erstellen eines Users → create_kunde() mit derselben Email ausführen.

Modelle prüfen:

Kunde: Name (String), Email (String), Telefon (optional).

## Akzeptanzkriterien (Definition of Done)

| Kriterium                     | Erfüllt wenn…                                                                |
| ----------------------------- | ---------------------------------------------------------------------------- |
| Automatische Kundenerstellung | Nach Registrierung existiert ein Kunde-Eintrag in der DB                     |
| Login zeigt Daten             | Nach Login sieht der User seine eigenen Daten im Dashboard (falls vorhanden) |
| Keine Duplicate-Kunden        | Registrierung prüft, ob Kunde bereits existiert                              |
| Dokumentation                 | Funktion in README oder SPRINT_5_NOTES.md beschrieben                        |

## Testcases
| Test                                 | Erwartetes Ergebnis                                 |
| ------------------------------------ | --------------------------------------------------- |
| `/register` neuer User               | User + Kunde wird erstellt                          |
| `/register` gleiche Email erneut     | Fehler: "User/Kunde existiert bereits"              |
| Login danach → `/dashboard` aufrufen | Dashboard zeigt persönliche Infos (falls vorhanden) |


# sprint 6
Ich möchte in meinem Dashboard (React + Vite) die Schnellzugriff-Buttons funktionsfähig machen.

Aktueller Zustand:
Die Buttons "Neuen Auftrag erstellen", "Schadensmeldung einreichen" und "Chat öffnen" sind sichtbar, aber haben noch keine Navigation.

Ziel

Wenn der Nutzer auf „+ Neuen Auftrag erstellen“ klickt, soll er auf eine neue Seite weitergeleitet werden:

/neuer-auftrag


Dort soll eine Auswahlseite angezeigt werden, auf der der Nutzer zwischen folgenden Auftragsarten wählen kann:

Schadensmeldung einreichen

Neues Fahrzeug registrieren

Versicherung aktualisieren

Werkstatttermin anfragen

Sonstigen Auftrag erstellen

Diese sollen als visuelle Karten (Cards) oder Buttons dargestellt werden (modern, dunkel, passend zum aktuellen UI).

Beim Klick auf eine Option → Weiterleitung zu Placeholder-Seiten, die später befüllt werden:

/auftrag/schadensmeldung
/auftrag/fahrzeug-registrieren
/auftrag/versicherung
/auftrag/werkstatt
/auftrag/sonstiges

Technische Anforderungen

Routing erweitern:

Datei: src/App.jsx oder src/router.jsx

Neue Routen für alle oben genannten Pfade hinzufügen.

Neue Seite erstellen:
Datei erstellen:

src/pages/NeuerAuftragAuswahl.jsx


Inhalt:

Überschrift: „Welchen Auftrag möchten Sie erstellen?“

Grid mit 5 Auswahlkarten

Jede Karte enthält:

Icon (optional)

Titel

kurzen Beschreibungstext

onClick → Navigiert zur passenden Route

Schnellzugriff Buttons in Dashboard verlinken

In Dashboard.jsx sicherstellen, dass:

<button onClick={() => navigate('/neuer-auftrag')}>


Placeholder-Seiten erstellen
Beispiel:

src/pages/SchadensmeldungForm.jsx


Vorerst nur Text:

<h1>Schadensmeldung Formular (kommt später)</h1>

Ergebnis

Klick auf Schnellzugriff → Auswahlseite → Auftragstyp auswählen → Placeholder-Seite öffnet sich.

Noch keine Backend-Anbindung nötig, nur Navigation/UI.

🎯 Zielzustand (in einem Satz)

Es soll eine funktionierende Navigationsstruktur entstehen, damit ein Nutzer neue Aufträge erstellen und zwischen verschiedenen Auftragstypen wählen kann.
---

## Backend-Spezifisch (FastAPI + SQLAlchemy + PostgreSQL)
- **FastAPI**: Nutze async/await für DB-Operationen, type hints für Request/Response models
- **SQLAlchemy**: Verwende das bestehende `models.py` Schema, keine redundanten Model-Definitionen
- **Pydantic**: Schemas in `schemas.py` erweitern, nicht neu erstellen
- **Database**: Immer `get_db()` Dependency für Session-Management verwenden
- **CORS**: Bestehende CORS-Konfiguration respektieren (Frontend: localhost:5173)
- **Error Handling**: HTTPException mit aussagekräftigen Status Codes und Messages

---

## Frontend-Spezifisch (React + TypeScript + Vite + Tailwind)
- **TypeScript**: Strenge Typisierung, Interfaces für API-Responses definieren
- **React**: Funktionale Komponenten, moderne Hooks (useState, useEffect, useContext)
- **Tailwind CSS**: Konsistente Utility-Classes, keine Custom-CSS-Dateien
- **API-Calls**: Axios in `services/api.ts` verwenden, keine Fetch direkt in Komponenten
- **Routing**: React Router für Navigation, bestehende Page-Struktur erweitern
- **Components**: Wiederverwendbare UI-Komponenten in `components/` Ordner

---

## Docker & Infrastruktur
- **Docker Compose**: Bestehende Services (db, backend:8000, frontend:5173) respektieren
- **Environment**: Umgebungsvariablen für DB-Verbindung und API-Keys verwenden
- **Ports**: Backend Port 8000, Frontend Port 5173, PostgreSQL Port 5432 beibehalten

---

## Projekt-spezifische Patterns
- **Schadensmeldung**: Alle Damage-Reports durch bestehende DB-Models abbilden
- **Chat-System**: Real-time Features über WebSocket/SSE implementieren
- **API-Struktur**: RESTful Endpoints unter `/api/v1/` Prefix organisieren
- **Fehlerbehandlung**: Konsistente Error-Responses mit deutschen Fehlermeldungen

---

## Sicherheit & Validierung
- **Input-Validation**: Pydantic Models für alle API-Eingaben
- **SQL-Injection**: Nur SQLAlchemy ORM, keine Raw-SQL-Queries
- **Environment-Secrets**: API-Keys (OpenAI) über Umgebungsvariablen laden
- **CORS**: Nur Frontend-Origin (localhost:5173) in Entwicklung erlauben

---

## Code-Qualität & Stil
- **Python**: PEP8, Type Hints, Docstrings für öffentliche Funktionen
- **TypeScript**: ESLint-Konfiguration befolgen, strikte Typisierung
- **Kommentare**: Deutsche Kommentare für Business-Logik, englische für technische Details
- **Naming**: Deutsche Begriffe für Domain-Models (Schadensmeldung, Fahrzeug, etc.)

---

## Testing & Development
- **Backend**: FastAPI TestClient für API-Tests verwenden
- **Frontend**: React Testing Library für Komponenten-Tests
- **Docker**: Entwicklung über `docker-compose up` für alle Services
- **Hot Reload**: Vite Dev Server und FastAPI auto-reload aktiviert

---

*Copilot soll Code für unser Fahrzeugservice-System schreiben, der nahtlos in die bestehende FastAPI/React-Architektur integriert.*

---

## Code-Stil
- Befolge **Projektkonventionen** (Formatierung, Benennungen, Imports).  
- Schreibe **klaren, kommentierten Code** – besonders bei komplexer Logik.  
- Nutze **sprechende Variablen- und Funktionsnamen**.  
- Kein „magischer Code“: vermeide unverständliche One-Liner oder Tricks.

---

## Architektur & Struktur
- Vorschläge müssen **bestehende Module respektieren**, keine Duplikate erzeugen.  
- Bevorzugt **Funktionen und Klassen** statt losem Skriptcode.  
- Immer **Single Responsibility Principle** (eine Funktion = eine Aufgabe).  
- Kein automatisches Erstellen unnötiger Dateien oder Verzeichnisse.

---

## Sicherheit & Qualität
- Keine sensiblen Daten hardcoden (Passwörter, Tokens, Keys).  
- Eingaben immer **validieren** und auf **Fehlerfälle prüfen**.  
- Vorschläge sollen **sauberes Error-Handling** enthalten.  
- Keine veralteten, unsicheren oder experimentellen APIs.

---

## Dokumentation & Kommentare
- Jede öffentliche Funktion: **kurze Docstring-Beschreibung** (Zweck, Parameter, Rückgabe).  
- Komplexe Algorithmen: **Inline-Kommentar**, kein Roman.  
- Copilot soll keine generischen Textblöcke, sondern **konkrete Erklärungen** erzeugen.

---

## Zusammenarbeit mit dem Entwickler
- Vorschläge sollen **Ergänzungen**, keine vollständigen Umschreibungen sein.  
- Wenn Kontext unklar ist: **keine Vermutungen** → auf vorhandene Patterns achten.  
- Immer **bestehenden Stil imitieren**, nicht ersetzen.

---

## Performance & Effizienz
- Bevorzuge **klare, effiziente Lösungen** statt Micro-Optimierungen.  
- Keine unnötigen Schleifen, Kopien oder komplexen Datentypen.  
- Keine Logging- oder Debug-Ausgaben in Produktivcode.

---

## Sprache & Tools
- Kommentarsprache: **Deutsch oder Englisch**, je nach Projektstandard.  
- Für JS/TS/React: bevorzugt **ES6+ Syntax** und funktionale Patterns.  
- Für Python: **type hints**, **PEP8-Konventionen**, **logging statt print()**.  

---

# GitHub push order 

Wenn ein sprint abgeschlossen worden ist frage mich ob wir den Sprint abschließen sollen und führe folgende Befehle aus. 

- Git status
- Git add . 
- git commit -m "Sinnvolle Nachricht die den Commit beschriebt und die Änderungen zusammenfasst"
- git push 
**Ändere nach dem abschließen eines Sprintes den Status auf Abgeschlossen, erstelle eine Neue Datei mit der Änderung des Sprintes**

*Copilot soll Code schreiben, der aussieht, als hätte ihn ein erfahrener Entwickler mit Bedacht geschrieben.*
