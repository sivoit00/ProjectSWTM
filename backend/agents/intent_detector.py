"""
Intent-Detection für Themenwechsel
Erkennt, ob der User ein neues Thema startet
"""
import logging
from typing import Optional

log = logging.getLogger(__name__)

# Keyword-basierte Intent-Erkennung (schnell, keine LLM-Calls nötig)
INTENT_KEYWORDS = {
    "repair": [
        "werkstatt", "reparatur", "service", "termin", "inspektion",
        "ölwechsel", "reifenwechsel", "bremsen", "motor", "werkstattsuche",
        "empfehlung werkstatt", "wo kann ich", "suche werkstatt", "autowerkstatt",
        "reparieren", "kaputt", "defekt", "wartung", "tüv", "hauptuntersuchung",
        "auto reparatur", "mechaniker", "kfz", "autowerkstätten"
    ],
    "lawyer": [
        "anwalt", "rechtsanwalt", "rechtsfrage", "unfall", "bußgeld",
        "vertrag", "rechtlich", "klage", "gericht", "anzeige",
        "jurist", "recht", "rechtshilfe", "rechtsberatung", "anwälte",
        "verkehrsunfall", "unfallgegner", "rechtsstreit", "rechtsbeistand"
    ],
    "insurance": [
        "versicherung", "police", "schaden", "schadensmeldung", "prämie",
        "deckung", "versichert", "kasko", "haftpflicht", "versicherungsfall",
        "erstattung", "versicherungsstatus", "versicherungen", "versicherungsschutz",
        "schadensregulierung", "gutachten", "unfallschaden", "versicherter"
    ]
}

# Reset-Keywords (zurück zu Tom)
RESET_KEYWORDS = [
    "zurück zu tom", "wieder tom", "anderes thema", "themenwechsel",
    "stop", "abbruch", "ende", "neu starten", "von vorne"
]


def detect_intent_from_message(message: str) -> Optional[str]:
    """
    Erkennt Intent basierend auf Keywords in der Nachricht.
    Gibt None zurück wenn kein eindeutiger Intent erkannt wird.
    
    Returns:
        - "repair", "lawyer", "insurance" bei erkanntem Intent
        - "reset" bei Reset-Keywords
        - None wenn kein Intent erkannt
    """
    message_lower = message.lower().strip()
    
    # Prüfe Reset-Keywords zuerst
    for keyword in RESET_KEYWORDS:
        if keyword in message_lower:
            log.info(f"Reset-Intent erkannt: '{keyword}' in '{message[:50]}'")
            return "reset"
    
    # Zähle Matches für jeden Intent
    intent_scores = {}
    
    for intent, keywords in INTENT_KEYWORDS.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            if keyword in message_lower:
                score += 1
                matched_keywords.append(keyword)
        
        if score > 0:
            intent_scores[intent] = score
            log.debug(f"Intent '{intent}' Score: {score} (Keywords: {matched_keywords})")
    
    # Wenn keine Matches, kein Intent erkannt
    if not intent_scores:
        return None
    
    # Wähle Intent mit höchstem Score
    best_intent = max(intent_scores.items(), key=lambda x: x[1])
    
    # Nur wenn Score >= 1 (mindestens 1 Keyword), Intent zurückgeben
    # Reduziert von 2 auf 1 für bessere Erkennung
    if best_intent[1] >= 1:
        log.info(f"Intent erkannt: '{best_intent[0]}' (Score: {best_intent[1]})")
        return best_intent[0]
    
    log.debug(f"Intent-Score zu niedrig: {best_intent[0]} = {best_intent[1]} (benötigt >= 1)")
    return None


def should_switch_agent(current_agent: str, detected_intent: Optional[str]) -> bool:
    """
    Entscheidet, ob ein Agent-Wechsel stattfinden soll.
    
    Returns:
        True wenn gewechselt werden soll, False sonst
    """
    # Kein Intent erkannt → Bleib beim aktuellen Agent (Tom bleibt Tom)
    if detected_intent is None:
        return False
    
    # Reset-Keyword → Zurück zu Tom
    if detected_intent == "reset":
        return True
    
    # Wenn Tom aktiv ist und spezieller Intent erkannt → Wechsle
    if current_agent == "chatbot":
        return True
    
    # Wenn bereits ein spezialisierter Agent aktiv ist:
    # - Wechsle NUR wenn ein ANDERER Intent erkannt wird
    # - Bleib beim Agent wenn GLEICHER Intent oder KEIN Intent
    return current_agent != detected_intent
