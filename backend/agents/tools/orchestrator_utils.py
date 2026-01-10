import json
import re
import unicodedata

def _normalize_text(text: str) -> str:
    text = text.strip().lower()
    text = text.replace("ß", "ss")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text

def _safe_json_loads(s: str) -> dict:
    try:
        s = s.replace("```json", "").replace("```", "").strip()
        start = s.find("{")
        end = s.rfind("}") + 1
        if start != -1 and end != -1:
            s = s[start:end]
        return json.loads(s)
    except json.JSONDecodeError:
        return {}
    
def _check_explicit_triggers(text: str) -> tuple[bool, str]:
    """Prüft ob User explizit einen Agenten-Wechsel wünscht."""
    t = _normalize_text(text)

    request_words = r"(?:bitte|bitte\s+mal|kannst\s*du|koennen\s*wir|kann\s*ich|ich\s*(?:will|moechte|mochte|brauch|brauche)|verbinde|wechsel|leite\s*mich\s*weiter|sprich\s*(?:mit|zu))"

    lawyer_kw = r"(?:anwalt|rechtsanwalt|rechtsberatung|rechtliche\s*hilfe|rechtshilfe|juristisch)"
    insurance_kw = r"(?:versicherung|schadensmeldung|schaden\s*melden|schadenfall|claim)"
    repair_kw = r"(?:werkstatt|werkstatttermin|reparatur|termin\s*(?:bei|in)\s*der\s*werkstatt|inspektion|olwechsel|service)"

    patterns: list[tuple[str, str]] = [
        ("lawyer", rf"\b{request_words}\b.*\b{lawyer_kw}\b|\b{lawyer_kw}\b.*\b(?:bitte|verbinde|wechsel)\b"),
        ("insurance", rf"\b(?:schadensmeldung|schaden\s*melden)\b|\b{request_words}\b.*\b{insurance_kw}\b|\b{insurance_kw}\b.*\b(?:bitte|verbinde|wechsel)\b"),
        ("repair", rf"\b(?:werkstatttermin)\b|\b{request_words}\b.*\b{repair_kw}\b|\b{repair_kw}\b.*\b(?:bitte|verbinde|wechsel)\b"),
    ]

    for agent, pat in patterns:
        if re.search(pat, t, flags=re.IGNORECASE):
            return (True, agent)

    return (False, "general")


def process_handover_signal(output_text: str):
    """Sucht nach dem Signal und gibt (Ziel-Agent, sauberer_Text) zurück."""
    match = re.search(r"\[TRIGGER_HANDOVER:\s*(\w+)\]", output_text)
    if match:
        target = match.group(1).lower()
        clean_text = re.sub(r"\[TRIGGER_HANDOVER:\s*\w+\]", "", output_text).strip()
        return target, clean_text
    return None, output_text
   