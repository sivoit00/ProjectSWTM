import os
import json
import time
import logging
from typing import Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agents.insurance_utils import (
    get_or_create_memory,
    load_state,
    save_state,
    load_template,
    extract_json_from_text,
    safe_string,
    format_history,
    REQUIRED_FIELDS,
    OPTIONAL_FIELDS,
    CAPTURE_FIELDS
)

from services.insurance_service import submit_claim

log = logging.getLogger(__name__)

def extract_fields(system_prompt: str, history: str, user_input: str, llm):
    extraction_call = [
        SystemMessage(content=system_prompt),
        HumanMessage(
            content=f"{history}\n\n{user_input}\n\nCAPTURE_JSON"
        )
    ]
    try:
        res = llm.invoke(extraction_call)
        json_obj = extract_json_from_text(res.content)
        return json_obj or {}
    except Exception as e:
        log.error(f"Extraction failed: {e}")
        return {}

def run_insurance_agent(
    user_input: str,
    session_id: str = "default",
    user_context: Optional[Dict[str, Any]] = None
) -> str:

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "API key missing"

    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")

    llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0)

    memory = get_or_create_memory(session_id)
    state = load_state(session_id, user_context)
    fields = state["fields"]
    asked = state["asked"]

    chat_history_list = memory.load_memory_variables({}).get("chat_history", [])
    chat_history_text = format_history(chat_history_list)

    template_text = load_template("insurance_classifier.md")
    system_prompt = (
        template_text
        .replace("{chat_history}", chat_history_text)
        .replace("{user_input}", user_input)
    )

    # 1. JSON-Extraktion
    extracted = extract_fields(system_prompt, chat_history_text, user_input, llm)
    for key, val in extracted.items():
        if key in CAPTURE_FIELDS and val not in [None, "", " "]:
            fields[key] = val

    # 2. Fehlende Pflichtfelder → Fragen
    for f in REQUIRED_FIELDS:
        if not fields.get(f):
            if not asked.get(f):
                asked[f] = True
                questions = {
                    "customer_id": "Wie lautet deine Kundennummer?",
                    "damage_type": "Worum handelt es sich für eine Art Schaden?",
                    "damage_date": "Wann ist der Schaden passiert?",
                    "damage_location": "Wo ist der Schaden passiert?",
                    "description": "Was ist genau passiert?",
                    "vehicle": "Welches Fahrzeug ist betroffen?"
                }
                reply = questions.get(f, "Kannst du mir diese Information bitte noch geben?")
                memory.save_context({"user_input": user_input}, {"response": reply})
                save_state(session_id, state)
                return reply

    # 3. Adaptive Zusatzfragen
    damage_type = (fields.get("damage_type") or "").lower()

    if "accident" in damage_type or "collision" in damage_type:
        if fields.get("third_party_involved") is None and not asked.get("third_party_involved"):
            asked["third_party_involved"] = True
            reply = "War jemand anderes beteiligt oder ist es reiner Eigenschaden?"
            memory.save_context({"user_input": user_input}, {"response": reply})
            save_state(session_id, state)
            return reply

    if "theft" in damage_type:
        if fields.get("police_involved") is None and not asked.get("police_involved"):
            asked["police_involved"] = True
            reply = "Wurde die Polizei informiert?"
            memory.save_context({"user_input": user_input}, {"response": reply})
            save_state(session_id, state)
            return reply

    if fields.get("estimated_damage") is None and not asked.get("estimated_damage"):
        asked["estimated_damage"] = True
        reply = "Hast du eine ungefähre Einschätzung der Schadenshöhe?"
        memory.save_context({"user_input": user_input}, {"response": reply})
        save_state(session_id, state)
        return reply

    # 4. Claim vollständig → einreichen und Nutzer informieren
    if not state.get("awaiting_submission"):
        claim_id = fields.get("claim_id") or f"CLM-{int(time.time())}"
        fields["claim_id"] = claim_id
        payload = {k: fields.get(k) for k in CAPTURE_FIELDS}

        try:
            result = submit_claim(payload)
            state["awaiting_submission"] = True
            state["last_claim_id"] = claim_id
            state["awaiting_workshop_decision"] = True 
            save_state(session_id, state)  

            reply = (
                f"Super — ich reiche den Schaden jetzt ein.\n\n"
                f"Fertig. Deine Schadens-ID: {claim_id}\n\n"
                f"Kurz zur Bestätigung:\n"
                f"- Kundennummer: {fields.get('customer_id')}\n"
                f"- Fahrzeug: {fields.get('vehicle')}\n"
                f"- Schaden: {fields.get('description')}\n"
                f"- Geschätzter Schaden: {fields.get('estimated_damage')} €\n"
                f"- Zeitpunkt: {fields.get('damage_date')}\n"
                f"- Ort: {fields.get('damage_location')}\n"
                f"- Keine weiteren Beteiligten, Polizei nicht involviert\n\n"
                "Möchtest du einen Werkstatttermin vereinbaren? (Ja/Nein)"
            )

        except Exception as e:
            state["awaiting_submission"] = False
            reply = "Der Schaden konnte wegen eines technischen Problems nicht gespeichert werden. Möchtest du es nochmal versuchen? (Ja/Nein)"

        memory.save_context({"user_input": user_input}, {"response": reply})
        save_state(session_id, state)
        return reply

    # 5. Normale Konversation nach Einreichung
    try:
        answer = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]).content
    except Exception:
        answer = "Ich kann dir gerade nicht antworten."

    memory.save_context({"user_input": user_input}, {"response": answer})
    save_state(session_id, state)

    return answer
