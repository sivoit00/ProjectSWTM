# Sprint 6: Schnellzugriff-Buttons & Auftragsauswahl-Navigation

## Ziel
Die Schnellzugriff-Buttons im Dashboard funktionsfähig machen und eine vollständige Navigation für verschiedene Auftragstypen erstellen.

## Problem vorher
- Schnellzugriff-Buttons im Dashboard hatten keine Funktion
- Keine strukturierte Möglichkeit, verschiedene Auftragstypen zu erstellen
- User hatten keine Auswahlmöglichkeit für Auftragsarten

## Lösung
Implementierung einer Auftragsauswahl-Seite mit 5 verschiedenen Auftragstypen und entsprechenden Placeholder-Seiten für zukünftige Entwicklung.

---

## Umgesetzte Features

### 1. Routing erweitert (`App.tsx`)

**Neue Routen:**
```typescript
<Route path="/neuer-auftrag" element={<NeuerAuftragAuswahl />} />
<Route path="/auftrag/schadensmeldung" element={<SchadensmeldungForm />} />
<Route path="/auftrag/fahrzeug-registrieren" element={<FahrzeugRegistrieren />} />
<Route path="/auftrag/versicherung" element={<VersicherungAktualisieren />} />
<Route path="/auftrag/werkstatt" element={<WerkstattTermin />} />
<Route path="/auftrag/sonstiges" element={<SonstigerAuftrag />} />
```

**Importierte Komponenten:**
- `NeuerAuftragAuswahl` - Hauptauswahlseite
- `SchadensmeldungForm` - Schadensmeldungs-Formular
- `FahrzeugRegistrieren` - Fahrzeug-Registrierung
- `VersicherungAktualisieren` - Versicherungsdaten ändern
- `WerkstattTermin` - Werkstatttermin vereinbaren
- `SonstigerAuftrag` - Individuelle Aufträge

---

### 2. Auftragsauswahl-Seite (`NeuerAuftragAuswahl.tsx`)

**Design:**
- Grid-Layout mit 5 interaktiven Karten
- Moderne, dunkle UI mit Farbcodierung
- Hover-Effekte und Animationen
- Responsive Design (mobile-first)

**Auftragsoptionen:**

| Option | Icon | Farbe | Route |
|--------|------|-------|-------|
| Schadensmeldung einreichen | 📄 FileText | Rot | `/auftrag/schadensmeldung` |
| Neues Fahrzeug registrieren | 🚗 Car | Blau | `/auftrag/fahrzeug-registrieren` |
| Versicherung aktualisieren | 🛡️ Shield | Grün | `/auftrag/versicherung` |
| Werkstatttermin anfragen | 🔧 Wrench | Lila | `/auftrag/werkstatt` |
| Sonstigen Auftrag erstellen | ➕ Plus | Grau | `/auftrag/sonstiges` |

**Funktionalität:**
```typescript
const handleSelectOption = (route: string) => {
  navigate(route);
};
```

**UI-Features:**
- ✅ Framer Motion Animationen (staggered)
- ✅ Lucide React Icons
- ✅ Tailwind CSS Gradient Backgrounds
- ✅ Hover-Transformationen (scale, opacity)
- ✅ Info-Box mit Hinweisen zur Sicherheit

---

### 3. Placeholder-Seiten

Alle Placeholder-Seiten folgen einem einheitlichen Design-Pattern:

**Gemeinsame Features:**
- Zurück-Button zur Auftragsauswahl
- Icon-Header mit Farbcodierung
- Zentrierte Placeholder-Nachricht
- Liste der geplanten Features
- Konsistentes Dark-Theme

#### 3.1 Schadensmeldung (`SchadensmeldungForm.tsx`)

**Geplante Features:**
- Schadensbeschreibung mit Textfeld
- Foto-Upload für Schadensbilder
- Auswahl des betroffenen Fahrzeugs
- Datum und Ort des Schadens
- Direkter Versand an Versicherung

#### 3.2 Fahrzeug registrieren (`FahrzeugRegistrieren.tsx`)

**Geplante Features:**
- Eingabe von Marke und Modell
- Kennzeichen und Fahrgestellnummer
- Baujahr und Erstzulassung
- Kilometerstand
- Automatische Verknüpfung mit Account

#### 3.3 Versicherung aktualisieren (`VersicherungAktualisieren.tsx`)

**Geplante Features:**
- Versicherungsnummer ändern
- Versicherungsgesellschaft aktualisieren
- Deckungssumme anpassen
- Vertragslaufzeit verlängern
- Dokumente hochladen (Versicherungsschein)

#### 3.4 Werkstatttermin (`WerkstattTermin.tsx`)

**Geplante Features:**
- Auswahl des Fahrzeugs
- Terminvorschläge mit Kalenderansicht
- Art der Wartung auswählen (Inspektion, Reparatur, etc.)
- Werkstatt auswählen
- Automatische Terminbestätigung per Email

#### 3.5 Sonstiger Auftrag (`SonstigerAuftrag.tsx`)

**Geplante Features:**
- Freies Textfeld für Auftragsbeschreibung
- Priorität festlegen (niedrig, mittel, hoch)
- Dateien anhängen (Dokumente, Bilder)
- Kostenvoranschlag anfordern
- Automatische Weiterleitung an zuständige Abteilung

---

### 4. Dashboard-Buttons verlinkt (`Dashboard.tsx`)

**Vorher:**
```typescript
<button className="...">
  + Neuen Auftrag erstellen
</button>
```

**Nachher:**
```typescript
<button 
  onClick={() => navigate("/neuer-auftrag")}
  className="..."
>
  + Neuen Auftrag erstellen
</button>

<button 
  onClick={() => navigate("/auftrag/schadensmeldung")}
  className="..."
>
  Schadensmeldung einreichen
</button>

<button 
  onClick={() => navigate("/chat")}
  className="..."
>
  Chat öffnen
</button>
```

**Änderungen:**
- Import von `useNavigate` aus react-router-dom
- `onClick`-Handler für alle drei Buttons
- Navigation zu entsprechenden Routen

---

## Technische Details

### Navigation Flow

```
Dashboard
  ↓ Klick auf "Neuen Auftrag erstellen"
Auftragsauswahl (/neuer-auftrag)
  ↓ Klick auf Auftragstyp
Placeholder-Seite (/auftrag/[typ])
  ↓ Zurück-Button
Auftragsauswahl
```

### Component Structure

```
src/pages/
├── Dashboard.tsx (aktualisiert)
├── NeuerAuftragAuswahl.tsx (neu)
├── SchadensmeldungForm.tsx (neu)
├── FahrzeugRegistrieren.tsx (neu)
├── VersicherungAktualisieren.tsx (neu)
├── WerkstattTermin.tsx (neu)
└── SonstigerAuftrag.tsx (neu)
```

### Dependencies

**Verwendet:**
- `react-router-dom` - Navigation
- `framer-motion` - Animationen
- `lucide-react` - Icons
- `tailwindcss` - Styling

**Keine neuen Pakete installiert** - alle bereits vorhanden

---

## Akzeptanzkriterien ✅

| Kriterium | Status | Details |
|-----------|--------|---------|
| Routing funktioniert | ✅ | Alle 6 neuen Routen implementiert |
| Auftragsauswahl-Seite | ✅ | 5 Cards mit Navigation |
| Placeholder-Seiten | ✅ | Alle 5 Seiten erstellt |
| Dashboard-Navigation | ✅ | Alle 3 Buttons verlinkt |
| Zurück-Navigation | ✅ | Funktioniert auf allen Placeholder-Seiten |
| Responsive Design | ✅ | Mobile-optimiert |
| Animationen | ✅ | Smooth transitions |

---

## Testcases

### Test 1: Dashboard → Auftragsauswahl
**Schritte:**
1. Dashboard öffnen
2. Auf "Neuen Auftrag erstellen" klicken
3. Erwartung: `/neuer-auftrag` Seite öffnet sich

**Ergebnis:** ✅ Navigation funktioniert

### Test 2: Auftragstyp auswählen
**Schritte:**
1. Auftragsauswahl öffnen
2. Auf "Schadensmeldung einreichen" klicken
3. Erwartung: Placeholder-Seite öffnet sich

**Ergebnis:** ✅ Alle 5 Optionen funktionieren

### Test 3: Zurück-Navigation
**Schritte:**
1. Placeholder-Seite öffnen
2. Auf "Zurück zur Auswahl" klicken
3. Erwartung: Zurück zur Auftragsauswahl

**Ergebnis:** ✅ Zurück-Button funktioniert

### Test 4: Direktnavigation
**Schritte:**
1. Dashboard → "Schadensmeldung einreichen"
2. Erwartung: Direkt zur Schadensmeldungs-Seite

**Ergebnis:** ✅ Direktlink funktioniert

### Test 5: Chat-Button
**Schritte:**
1. Dashboard → "Chat öffnen"
2. Erwartung: Chat-Seite öffnet sich

**Ergebnis:** ✅ Navigation zu Chat funktioniert

---

## UI/UX Verbesserungen

### Design-Prinzipien

1. **Konsistenz:**
   - Alle Seiten nutzen Sidebar
   - Einheitliche Farbcodierung
   - Gleiche Schriftgrößen und Abstände

2. **Feedback:**
   - Hover-Effekte auf allen interaktiven Elementen
   - Transform-Animationen (scale)
   - Farbübergänge

3. **Navigation:**
   - Klare Breadcrumbs durch Zurück-Buttons
   - Intuitive Icons
   - Beschreibende Texte

4. **Accessibility:**
   - Große Click-Targets
   - Hoher Kontrast (Dark Theme)
   - Semantische HTML-Struktur

---

## Code-Beispiele

### Auftragsauswahl Card Component

```typescript
<motion.div
  key={option.id}
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: index * 0.1 }}
  onClick={() => handleSelectOption(option.route)}
  className="group cursor-pointer"
>
  <div className={`bg-gradient-to-br ${option.color} rounded-lg p-6 
                   hover:scale-105 hover:shadow-xl transition-all`}>
    <div className="text-white">{option.icon}</div>
    <h3 className="text-xl font-bold text-white">{option.title}</h3>
    <p className="text-gray-300 text-sm">{option.description}</p>
  </div>
</motion.div>
```

### Zurück-Button Pattern

```typescript
<button
  onClick={() => navigate("/neuer-auftrag")}
  className="flex items-center gap-2 text-gray-400 
             hover:text-white transition-colors"
>
  <ArrowLeft className="h-5 w-5" />
  <span>Zurück zur Auswahl</span>
</button>
```

---

## Änderungen im Detail

### Frontend
- **App.tsx:** 6 neue Routen hinzugefügt
- **Dashboard.tsx:** useNavigate importiert, onClick-Handler hinzugefügt
- **NeuerAuftragAuswahl.tsx:** Komplett neue Seite (170 Zeilen)
- **SchadensmeldungForm.tsx:** Placeholder (90 Zeilen)
- **FahrzeugRegistrieren.tsx:** Placeholder (90 Zeilen)
- **VersicherungAktualisieren.tsx:** Placeholder (90 Zeilen)
- **WerkstattTermin.tsx:** Placeholder (90 Zeilen)
- **SonstigerAuftrag.tsx:** Placeholder (90 Zeilen)

### Backend
- **Keine Änderungen** - Rein Frontend Sprint

---

## Performance

- **Bundle Size:** +15KB (durch neue Komponenten)
- **Lazy Loading:** Nicht implementiert (nicht notwendig bei aktueller Größe)
- **Code Splitting:** Automatisch durch Vite
- **Render Performance:** Optimiert durch React.memo (falls nötig)

---

## Bekannte Einschränkungen

- Placeholder-Seiten haben noch keine Backend-Anbindung
- Keine Formular-Validierung
- Keine Fehlerbehandlung für fehlgeschlagene Navigation
- Auth-Check fehlt (jeder kann Seiten aufrufen)

---

## Nächste Schritte (Sprint 7)

- [ ] Schadensmeldungs-Formular vollständig implementieren
- [ ] Backend-API für Auftragserstellung
- [ ] Formular-Validierung mit React Hook Form
- [ ] Datei-Upload Funktion
- [ ] Email-Benachrichtigungen
- [ ] Auth-Guards für geschützte Routen
- [ ] Fahrzeug-Registrierung mit DB-Anbindung

---

## Screenshots / Visuelle Beschreibung

### Auftragsauswahl
```
┌──────────────────────────────────────────────────┐
│  Welchen Auftrag möchten Sie erstellen?         │
│  Wählen Sie eine der folgenden Optionen         │
├──────────────────────────────────────────────────┤
│                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐         │
│  │ 📄 Scha│  │ 🚗 Fahr│  │ 🛡️ Vers│         │
│  │ dens-  │  │ zeug    │  │ icher-  │         │
│  │ meldung│  │ regis.  │  │ ung     │         │
│  └─────────┘  └─────────┘  └─────────┘         │
│                                                  │
│  ┌─────────┐  ┌─────────┐                       │
│  │ 🔧 Werk│  │ ➕ Sons│                       │
│  │ statt  │  │ tiges   │                       │
│  │ termin │  │ Auftrag │                       │
│  └─────────┘  └─────────┘                       │
└──────────────────────────────────────────────────┘
```

---

## Zusammenfassung

Sprint 6 hat erfolgreich eine vollständige Navigationsstruktur für Aufträge implementiert:

✅ **6 neue Seiten** erstellt  
✅ **3 Dashboard-Buttons** verlinkt  
✅ **5 Auftragstypen** definiert  
✅ **Einheitliches Design** umgesetzt  
✅ **Responsive & Animiert**  

Die Grundlage für zukünftige Feature-Implementierungen ist gelegt.
