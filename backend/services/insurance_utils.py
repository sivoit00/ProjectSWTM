import os
import json
import logging
from typing import Dict, Any, Optional, List
from langchain.memory import ConversationBufferMemory

log = logging.getLogger(__name__)

conversation_memories: Dict[str, ConversationBufferMemory] = {}
session_states: Dict[str, Dict] = {}


def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="user_input",
            output_key="response"
        )
    return conversation_memories[session_id]


def load_state(session_id: str, user_context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if session_id in session_states:
        return session_states[session_id]

    fields = {
        "customer_id":        (user_context or {}).get("customer_id"),
        "damage_type":        (user_context or {}).get("damage_type"),
        "damage_date":        (user_context or {}).get("damage_date"),
        "damage_location":    (user_context or {}).get("damage_location"),
        "description":        (user_context or {}).get("description"),
        "vehicle":            (user_context or {}).get("vehicle"),
        "police_involved":    (user_context or {}).get("police_involved"),
        "third_party_involved": (user_context or {}).get("third_party_involved"),
        "estimated_damage":   (user_context or {}).get("estimated_damage"),
        "language":           (user_context or {}).get("language") or "de",
        "claim_id":           (user_context or {}).get("claim_id"),
    }

    state = {
        "fields": fields,
        "asked": {f: False for f in REQUIRED_FIELDS + OPTIONAL_FIELDS},
        "awaiting_submission": False,
        "last_claim_id": fields.get("claim_id")
    }

    session_states[session_id] = state
    return state


def save_state(session_id: str, state: Dict[str, Any]) -> None:
    session_states[session_id] = state

def load_template(name: str) -> str:
    here = os.path.dirname(__file__)
    path = os.path.join(here, "templates", name)
    if not os.path.exists(path):
        return (
            "You are an insurance assistant.\n\n"
            "CHAT HISTORY:\n{chat_history}\n\n"
            "CURRENT REQUEST:\n{user_input}\n\n"
            "Extract claim information and use CAPTURE_JSON."
        )

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_json_from_text(text: str) -> Optional[dict]:
    if not text:
        return None

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    snippet = text[start:end + 1]

    try:
        return json.loads(snippet)
    except Exception:
        try:
            cleaned = snippet.replace("'", '"')
            return json.loads(cleaned)
        except Exception:
            return None

def safe_string(x: Any) -> str:
    try:
        return json.dumps(x, indent=2, ensure_ascii=False)
    except Exception:
        return str(x)


def format_history(messages: List) -> str:
    if not messages:
        return "No previous messages."

    formatted = []
    for m in messages:
        try:
            role = getattr(m, "type", None) or m.get("role")
            content = getattr(m, "content", None) or m.get("content")

            if role in ["human", "user"]:
                formatted.append(f"User: {content}")
            elif role in ["assistant", "ai"]:
                formatted.append(f"Bot: {content}")
            else:
                formatted.append(f"{role}: {content}")
        except:
            continue

    return "\n".join(formatted)

REQUIRED_FIELDS = [
    "customer_id",
    "damage_type",
    "damage_date",
    "description"
]

OPTIONAL_FIELDS = [
    "damage_location",
    "vehicle",
    "police_involved",
    "third_party_involved",
    "estimated_damage",
    "language"
]

CAPTURE_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
