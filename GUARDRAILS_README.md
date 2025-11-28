# Guardrails System - Dokumentation

## Übersicht

Das Guardrails-System schützt den Chat automatisch vor unangemessenen Inhalten und sensiblen Daten. Es arbeitet unsichtbar im Hintergrund und loggt problematische Nachrichten für das Support-Team.

## Features

### 1. Automatische Content-Filterung
- **Drohungen**: "ich bring dich um", "kill", "töten", etc.
- **Sensible Daten**: Kreditkarten, IBAN, Telefonnummern, SSN
- **Verbotene Themen**: Gewalt, Waffen, Drogen, Betrug
- **AI-basierte Validierung**: Erkennt komplexe problematische Inhalte

### 2. Datenbank-Logging
Alle Verstöße werden in der Datenbank gespeichert:
- User-Informationen (ID, Name, Email)
- Original-Nachricht
- Gefilterte Nachricht
- Verstoß-Typ und Schweregrad
- Timestamp

### 3. Admin-Endpoints für Support-Team

#### Alle Logs abrufen
```http
GET /admin/guardrails/logs?severity=CRITICAL&reviewed=false&limit=50
```

**Query-Parameter:**
- `severity`: Filter nach LOW, MEDIUM, HIGH, CRITICAL
- `reviewed`: true/false - nur überprüfte/ungeprüfte Logs
- `limit`: Max. Anzahl der Ergebnisse (Standard: 50, Max: 500)
- `skip`: Pagination

**Response:**
```json
[
  {
    "id": 1,
    "user_id": "user-123",
    "user_name": "Max Mustermann",
    "user_email": "max@example.com",
    "original_message": "ich bring dich um",
    "filtered_message": "ich bring dich um",
    "violation_type": "THREAT",
    "severity": "CRITICAL",
    "blocked_reason": "Drohung erkannt: 'bring dich um'",
    "warnings": "[\"Drohung erkannt\"]",
    "reviewed": false,
    "reviewed_by": null,
    "reviewed_at": null,
    "action_taken": "BLOCKED",
    "created_at": "2025-11-28T12:00:00"
  }
]
```

#### Einzelnen Log abrufen
```http
GET /admin/guardrails/logs/{log_id}
```

#### Log als überprüft markieren
```http
PATCH /admin/guardrails/logs/{log_id}/review
Content-Type: application/json

{
  "reviewed_by": "support@example.com",
  "notes": "Kunde wurde kontaktiert"
}
```

#### Statistiken abrufen
```http
GET /admin/guardrails/stats
```

**Response:**
```json
{
  "total": 150,
  "unreviewed": 23,
  "by_severity": {
    "CRITICAL": 5,
    "HIGH": 12,
    "MEDIUM": 45,
    "LOW": 88
  },
  "by_type": {
    "THREAT": 5,
    "FORBIDDEN_TOPIC": 12,
    "SENSITIVE_DATA": 88,
    "AI_DETECTED": 45
  }
}
```

## Verstoß-Typen

| Typ | Schweregrad | Beispiel | Aktion |
|-----|-------------|----------|---------|
| `THREAT` | CRITICAL | "ich bring dich um" | Blockiert + Support-Alert |
| `FORBIDDEN_TOPIC` | HIGH | "wie kann ich hacken" | Blockiert |
| `SENSITIVE_DATA` | MEDIUM | Kreditkartennummer | Gefiltert (erlaubt) |
| `AI_DETECTED` | HIGH | Komplexe problematische Inhalte | Blockiert |
| `TOO_LONG` | LOW | >5000 Zeichen | Blockiert |

## Nutzer-Erfahrung

### Bei blockierten Nachrichten (CRITICAL)
```
⚠️ Ihre Nachricht enthält unangemessene Inhalte und wurde an unser 
Support-Team weitergeleitet. Bitte formulieren Sie Ihre Anfrage respektvoll.
```

### Bei sensiblen Daten (MEDIUM)
Die Nachricht wird **erlaubt**, aber sensible Daten werden automatisch entfernt:
- Input: "Meine Kreditkarte ist 1234567812345678"
- Gefiltert: "Meine Kreditkarte ist [KREDITKARTE_ENTFERNT]"

## Entwickler-Logging

Alle Verstöße werden auch in der Console geloggt:
```
[GUARDRAILS] Violation detected: THREAT (CRITICAL) | 
User: Max Mustermann | Action: BLOCKED | 
Message: ich bring dich um...
```

## Dashboard-Integration

Für ein Support-Dashboard können folgende Endpoints genutzt werden:
1. `/admin/guardrails/stats` - Übersicht der Verstöße
2. `/admin/guardrails/logs?reviewed=false&severity=CRITICAL` - Dringende Fälle
3. `/admin/guardrails/logs/{id}/review` - Log als überprüft markieren

## Testen

1. **Chat öffnen**: http://localhost:5173/chat
2. **Drohung senden**: "ich bring dich um"
3. **Log prüfen**: http://localhost:8000/admin/guardrails/logs
4. **Swagger UI**: http://localhost:8000/docs

## Datenbank-Schema

Tabelle: `guardrails_logs`

```sql
CREATE TABLE guardrails_logs (
    id INTEGER PRIMARY KEY,
    user_id VARCHAR(255),
    user_name VARCHAR(255),
    user_email VARCHAR(255),
    original_message TEXT NOT NULL,
    filtered_message TEXT,
    violation_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) DEFAULT 'MEDIUM',
    blocked_reason TEXT,
    warnings TEXT,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(255),
    reviewed_at DATETIME,
    action_taken VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Erweiterung

Um neue Regeln hinzuzufügen, bearbeite `backend/services/guardrails_service.py`:

```python
# Neue Drohungs-Keywords
threat_keywords = ['bring dich um', 'kill', 'umbringen', 'DEIN_NEUES_KEYWORD']

# Neue sensible Datenmuster
self.sensitive_patterns = [
    (r'\b\d{16}\b', 'KREDITKARTE'),
    (r'DEIN_REGEX_PATTERN', 'DATENTYP')
]
```
