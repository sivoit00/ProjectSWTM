# Session-basiertes Agent-Routing System

## Übersicht

Das neue Routing-System ermöglicht es, dass spezialisierte Agenten (Werkstatt, Anwalt, Versicherung) aktiv bleiben und das Gespräch führen, bis der User explizit das Thema wechselt. Tom springt nicht mehr automatisch nach jeder Nachricht zurück.

## Architektur

### 1. Session Manager (`agents/session_manager.py`)

Verwaltet den Session-State pro User:

```python
{
    "active_agent": "chatbot",  # Aktueller Agent
    "conversation_count": 0,     # Anzahl Nachrichten
    "last_intent": None          # Letzter Intent
}
```

**Key Functions:**
- `get_active_agent(session_id)` - Holt aktuellen Agent
- `set_active_agent(session_id, agent)` - Setzt neuen Agent
- `reset_session(session_id)` - Zurück zu Tom

### 2. Intent Detector (`agents/intent_detector.py`)

Keyword-basierte Intent-Erkennung ohne LLM-Overhead:

**Erkannte Intents:**
- `repair` - Werkstatt/Reparatur Keywords
- `lawyer` - Rechts/Anwalt Keywords  
- `insurance` - Versicherungs Keywords
- `reset` - Zurück zu Tom

**Funktionsweise:**
```python
detect_intent_from_message("Ich brauche eine Werkstatt")
# → "repair"

should_switch_agent("chatbot", "repair")
# → True (Wechsel zu Repair Agent)

should_switch_agent("repair", "repair")  
# → False (Bleibe bei Repair Agent)
```

### 3. Router (`agents/kiClone.py`)

Persistentes Routing mit Session-State:

**Flow:**
1. Hole `active_agent` aus Session
2. Erkenne Intent aus User-Message
3. Prüfe ob Agent-Wechsel nötig
4. Leite an entsprechenden Agent weiter
5. Agent bleibt aktiv für nächste Nachricht

**Wichtig:** 
- Kein automatischer Rücksprung zu Tom
- Tom nur bei neuem Intent oder Reset

### 4. Orchestrator (`routes/ki_orchestrator.py`)

Timeline-Events angepasst:

**Events:**
- `agent_assigned` - NUR bei echtem Agent-Wechsel
- `agent_message` - Bei jeder Agent-Antwort
- `internal` - GuardRails (gefiltert im Frontend)

## Verwendung

### Frontend: Session-ID übergeben

```typescript
const res = await api.sendToKI({ 
  message: userMessage,
  session_id: sessionId  // Wichtig für persistentes Routing
});
```

### Agent-Wechsel

**Automatisch bei Keywords:**
```
User: "Ich brauche eine Werkstatt"
→ Wechsel zu Repair Agent
→ Timeline zeigt: "Werkstatt Assistent übernimmt Ihre Anfrage"

User: "Welche Werkstätten gibt es in Berlin?"
→ KEIN Wechsel, Repair Agent antwortet direkt
→ Timeline zeigt nur: "Werkstatt Assistent hat geantwortet"
```

**Manueller Reset:**
```
User: "zurück zu tom"
→ Session Reset
→ Nächste Nachricht geht an Tom
```

## Vorteile

✅ **Keine Änderung der Agenten-Logik** - Agents bleiben unverändert  
✅ **Minimale Backend-Änderungen** - Nur Routing angepasst  
✅ **Persistent** - Agent bleibt aktiv über mehrere Nachrichten  
✅ **Schnell** - Keyword-basiert, keine LLM-Calls für Intent  
✅ **Übersichtlich** - Timeline zeigt nur relevante Events  

## Testing

```python
# Test Session Management
from agents.session_manager import get_active_agent, set_active_agent

session_id = "test-user-123"
assert get_active_agent(session_id) == "chatbot"  # Default

set_active_agent(session_id, "repair")
assert get_active_agent(session_id) == "repair"  # Persistent
```

```python
# Test Intent Detection
from agents.intent_detector import detect_intent_from_message

assert detect_intent_from_message("Ich brauche eine Werkstatt") == "repair"
assert detect_intent_from_message("Anwalt gesucht") == "lawyer"
assert detect_intent_from_message("Hallo") == None  # Kein Intent
```

## Erweiterung

Um neue Agenten hinzuzufügen:

1. **Intent Keywords** in `intent_detector.py`:
```python
INTENT_KEYWORDS = {
    "new_agent": ["keyword1", "keyword2", ...],
    ...
}
```

2. **Agent Handler** in `kiClone.py`:
```python
if target_agent == "new_agent":
    res = handle_new_agent(user_message, user_context)
    return wrap_response("new_agent", res, agent_changed)
```

3. **Timeline Events** in `ki_orchestrator.py`:
```python
elif agent_type == "new_agent":
    add_step(agent_type, "working", "Neuer Agent übernimmt", "agent_assigned")
```
