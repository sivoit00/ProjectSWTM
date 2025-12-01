from typing import Optional, List, Dict
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain.tools import tool
from database import SessionLocal
import models
from langchain_tavily import TavilySearch
from agents.email_service import send_email, create_workshop_recommendation_html, format_workshop_recommendation_email

conversation_memories: Dict[str, ConversationBufferMemory] = {}
session_user_emails: Dict[str, str] = {}
session_states: Dict[str, Dict] = {}


def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="user_input",
            output_key="response",
        )
    return conversation_memories[session_id]


def clear_session_memory(session_id: str):
    if session_id in conversation_memories:
        del conversation_memories[session_id]
    if session_id in session_user_emails:
        del session_user_emails[session_id]
    if session_id in session_states:
        del session_states[session_id]


def is_session_active(session_id: str) -> bool:
    """Lightweight indicator used by orchestrator. Returns True if session has any chat history saved."""
    mem = conversation_memories.get(session_id)
    if not mem:
        return False
    try:
        history = mem.load_memory_variables({}).get("chat_history", [])
        return bool(history)
    except Exception:
        return False


def set_user_email(session_id: str, email: str) -> None:
    session_user_emails[session_id] = email


def get_user_email(session_id: str) -> Optional[str]:
    return session_user_emails.get(session_id)


@tool
def db_search_workshops(query: str) -> str:
    """Searches local DB for workshops that match city, zip, or name. Returns formatted text list (English)."""
    db = SessionLocal()
    try:
        workshops = db.query(models.Werkstatt).all()
        if not workshops:
            return "❌ No workshops found in the database."

        q = (query or "").lower()
        filtered = []
        for w in workshops:
            if (w.ort and w.ort.lower() in q) or (w.plz and str(w.plz) in q) or (w.name and w.name.lower() in q):
                filtered.append(w)
        if not filtered:
            filtered = workshops[:10]
            prefix = "ℹ️ No exact match. Available workshops:\n"
        else:
            prefix = f"✅ Found workshops ({len(filtered)}):\n"

        lines = [prefix]
        for w in filtered:
            lines.append(f"  • {w.name}\n    📍 {w.adresse}, {w.plz} {w.ort}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Database error: {e}"
    finally:
        db.close()


@tool
def web_search_workshops(query: str) -> str:
    """Searches the web via Tavily for car workshops. Returns a concise formatted list with name, url, contacts (English)."""
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        return "⚠️ Internet search unavailable (missing TAVILY_API_KEY)."
    try:
        search = TavilySearch(api_key=tavily_api_key, max_results=3, search_depth="basic", include_answer=False)
        results = search.run(query)
        # Normalize results to a list of dicts
        items: List[Dict] = []
        if isinstance(results, list):
            items = results
        elif isinstance(results, dict):
            items = results.get("results") or []
        else:
            # Fallback: show raw text
            text = str(results).strip()
            return f"🌐 Web search: {query}\n{text}" if text else f"🌐 Web search: {query}\n(no details available)"

        lines = [f"🌐 Web search: {query}"]
        for it in items[:3]:
            name = it.get("title") or it.get("name") or "Werkstatt"
            url = it.get("url") or it.get("link") or ""
            content = (it.get("content") or it.get("snippet") or "").strip()
            lines.append(f"• {name}\n   🔗 {url}\n   {content[:160]}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Web search failed: {e}"


def format_chat_history(messages: List) -> str:
    if not messages:
        return "Keine bisherigen Nachrichten."
    formatted = []
    for msg in messages:
        if hasattr(msg, "type"):
            if msg.type == "human":
                formatted.append(f"User: {msg.content}")
            elif msg.type == "ai":
                formatted.append(f"Bot: {msg.content}")
    return "\n".join(formatted) if formatted else "Keine bisherigen Nachrichten."


def build_appointment_email_content(state: Dict, lang: str) -> tuple[str, str, str]:
    name = state["fields"].get("user_name") or "Customer"
    service = state["fields"].get("service") or "Service"
    vehicle = state["fields"].get("vehicle") or "Vehicle"
    preferred_date = state["fields"].get("preferred_date") or ""
    phone = state["fields"].get("phone") or ""
    user_email_value = state["fields"].get("user_email") or ""
    damage_line = ""
    if state["fields"].get("had_accident") and state["fields"].get("damage_description"):
        damage_line = (
            f"Damage description: {state['fields']['damage_description']}"
            if lang.startswith("en")
            else f"Schadensbeschreibung: {state['fields']['damage_description']}"
        )
    subject = (
        f"Appointment Request: {service} for {name}"
        if lang.startswith("en")
        else f"Terminanfrage: {service} für {name}"
    )
    if lang.startswith("en"):
        body = (
            """Dear Sir or Madam,

I would like to schedule an appointment for {service} for my vehicle ({vehicle}).
Preferred date/time: {preferred_date}
{damage_line}

Please contact me at {phone} or {user_email} to confirm.

Kind regards,
{name}
"""
        ).format(
            service=service,
            vehicle=vehicle,
            preferred_date=preferred_date,
            damage_line=damage_line,
            phone=phone,
            user_email=user_email_value,
            name=name,
        )
    else:
        body = (
            """Sehr geehrte Damen und Herren,

ich möchte einen Termin für {service} für mein Fahrzeug ({vehicle}) vereinbaren.
Wunschtermin: {preferred_date}
{damage_line}

Bitte kontaktieren Sie mich zur Bestätigung unter {phone} oder {user_email}.

Mit freundlichen Grüßen
{name}
"""
        ).format(
            service=service,
            vehicle=vehicle,
            preferred_date=preferred_date,
            damage_line=damage_line,
            phone=phone,
            user_email=user_email_value,
            name=name,
        )
    html_body = create_workshop_recommendation_html(name, state.get("last_results", ""))
    return subject, body, html_body


def run_repair_agent_with_memory(user_query: str, session_id: str = "default", user_context: Optional[Dict] = None) -> str:
    """Minimal agent using tools for DB and web search. Retains per-user memory and optional email sending."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    model_name = os.getenv("OPENAI_MODEL", "gpt-5")
    llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0)

    memory = get_or_create_memory(session_id)

    try:
        if user_context and isinstance(user_context, dict):
            email_from_ctx = user_context.get("email") or user_context.get("user_email")
            if email_from_ctx:
                set_user_email(session_id, email_from_ctx)
    except Exception:
        pass

    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    history_text = format_chat_history(chat_history)

    # Load prompt from templates/repair_general.md as requested
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    system_path = os.path.join(templates_dir, "repair_general.md")
    
    with open(system_path, "r", encoding="utf-8") as f:
        raw_template = f.read()

    # Prepare session-state backed placeholders with safe defaults
    state_data = {
        "user_name": (user_context or {}).get("name") or "",
        
        "phone": (user_context or {}).get("phone") or "",
        "vehicle": (user_context or {}).get("vehicle") or "",
        "service": (user_context or {}).get("service") or "",
        "preferred_date": (user_context or {}).get("preferred_date") or "",
        "damage_description": (user_context or {}).get("damage_description") or "",
        "optional_damage_line": "",
        "location": (user_context or {}).get("location") or "",
    }
    if state_data["damage_description"]:
        state_data["optional_damage_line"] = f"Schadensbeschreibung: {state_data['damage_description']}"

    # Inject placeholders without raising errors if absent
    system_content = raw_template
    for key, val in state_data.items():
        system_content = system_content.replace("{" + key + "}", str(val))

    
    system = SystemMessage(content=system_content)

    # Initialize state for template-driven flow
    state = session_states.get(session_id) or {
        "fields": {
            "user_name": (user_context or {}).get("name") or "",
            "user_email": get_user_email(session_id) or (user_context or {}).get("email") or "",
            "phone": state_data.get("phone", ""),
            "vehicle": state_data.get("vehicle", ""),
            "service": state_data.get("service", ""),
            "preferred_date": state_data.get("preferred_date", ""),
            "location": state_data.get("location", ""),
            "had_accident": None,
            "damage_description": state_data.get("damage_description", ""),
            "language": "en",
        },
        "asked_accident": False,
        "asked_damage": False,
        "search_done": False,
        "email_sent": False,
        "awaiting_email_confirmation": False,
        "confirmed_to_send": False,
        "last_results": "",
    }

    # First, ask the LLM to capture structured fields based on the template
    q = user_query.strip()
    import json as _json
    capture_template = system_content + "\n\nCAPTURE_JSON"
    cap_msg = llm.invoke([
        SystemMessage(content=capture_template),
        HumanMessage(content=f"Historie:\n{history_text}\n\nAnfrage:\n{q}")
    ])
    try:
        cap = _json.loads(cap_msg.content)
        for k in ["user_name", "user_email", "phone", "vehicle", "service", "preferred_date", "location", "had_accident", "damage_description", "language"]:
            v = cap.get(k)
            if v is False or (v and not (isinstance(v, str) and v.strip() == "")):
                state["fields"][k] = v
    except Exception:
        pass

    # Language helper
    lang = (state["fields"].get("language") or "en").lower()
    def t(en: str, de: str) -> str:
        return en if lang.startswith("en") else de

    # Ask accident question once
    if not state.get("asked_accident") and state["fields"].get("had_accident") is None:
        ask = t("Did you have an accident with the vehicle? (yes/no)", "Hatten Sie einen Unfall mit dem Fahrzeug? (ja/nein)")
        state["asked_accident"] = True
        session_states[session_id] = state
        memory.save_context({"user_input": user_query}, {"response": ask})
        return ask
    # If accident is true, ask damage once
    if state["fields"].get("had_accident") is True and not state.get("asked_damage") and not state["fields"].get("damage_description"):
        ask = t("Could you briefly describe the damage?", "Können Sie den Schaden kurz beschreiben?")
        state["asked_damage"] = True
        session_states[session_id] = state
        memory.save_context({"user_input": user_query}, {"response": ask})
        return ask

    # Build brief confirmation line from known details
    bits = []
    if state["fields"].get("vehicle"): bits.append(t("vehicle:", "Fahrzeug:") + f" {state['fields']['vehicle']}")
    if state["fields"].get("service"): bits.append(t("service:", "Service:") + f" {state['fields']['service']}")
    if state["fields"].get("preferred_date"): bits.append(t("appointment:", "Termin:") + f" {state['fields']['preferred_date']}")
    if state["fields"].get("location"): bits.append(t("location:", "Ort/PLZ:") + f" {state['fields']['location']}")
    confirm_line = (t("Understood — ", "Verstanden — ") + ", ".join(bits) + ".") if bits else ""

    # Collect next missing field (email is asked only after search)
    order = ["user_name", "phone", "vehicle", "preferred_date", "location", "service"]
    prompts = {
        "user_name": t("What is your name?", "Wie ist Ihr Name?"),
        "phone": t("What is your phone number?", "Wie lautet Ihre Telefonnummer?"),
        "vehicle": t("What is your vehicle (make, model, year)?", "Welches Fahrzeug (Marke, Modell, Baujahr)?"),
        "preferred_date": t("What is your preferred date/time?", "Welcher Wunschtermin (Datum/Uhrzeit)?"),
        "location": t("Which city or ZIP should I search in?", "In welcher Stadt oder PLZ soll ich suchen?"),
        "service": t("What service do you need (e.g., inspection, oil change, tires, brakes, diagnostics)?", "Welche Leistung benötigen Sie (z. B. Inspektion, Ölwechsel, Reifen, Bremsen, Diagnose)?"),
    }
    for field in order:
        if not state["fields"].get(field):
            ask = (confirm_line + " " + prompts[field]).strip()
            session_states[session_id] = state
            memory.save_context({"user_input": user_query}, {"response": ask})
            return ask

    # Run search once (after service + location are known)
    if not state.get("search_done"):
        query_text = f"{state['fields']['service']} {state['fields']['location']}".strip()
        db_text = db_search_workshops.invoke({"query": query_text})
        web_text = web_search_workshops.invoke({"query": query_text})
        combined = f"{db_text}\n\n{web_text}".strip()
        state["search_done"] = True
        state["last_results"] = combined
        state["awaiting_email_confirmation"] = True
        prompt = t(
            "Here are workshop suggestions. Would you like me to create and send the appointment request email now? (yes/no)",
            "Hier sind Werkstattvorschläge. Soll ich jetzt die Terminanfrage per E-Mail erstellen und senden? (ja/nein)",
        )
        response = combined + "\n\n" + prompt
        session_states[session_id] = state
        memory.save_context({"user_input": user_query}, {"response": response})
        return response

    # After search: confirm and send email
    if state.get("search_done") and not state.get("email_sent"):
        # If user already confirmed earlier and now provided an email, send immediately
        recipient_now = state["fields"].get("user_email") or get_user_email(session_id)
        if state.get("confirmed_to_send") and recipient_now:
            subject, body, html_body = build_appointment_email_content(state, lang)
            success, message = send_email(recipient_now, subject, body, html_body)
            state["email_sent"] = success
            session_states[session_id] = state
            resp = (("✅ Email sent to " if lang.startswith("en") else "✅ E-Mail gesendet an ") + recipient_now) if success else (("⚠️ Failed to send: " if lang.startswith("en") else "⚠️ Versand fehlgeschlagen: ") + message)
            memory.save_context({"user_input": user_query}, {"response": resp})
            return resp

        lower = q.lower()
        if any(tk in lower for tk in ["yes", "ok", "okay", "sure", "please", "go ahead", "do it", "ja", "sende", "abschicken", "schicken"]):
            state["awaiting_email_confirmation"] = False
            state["confirmed_to_send"] = True
            recipient = state["fields"].get("user_email") or get_user_email(session_id)
            if not recipient:
                ask = t("Please provide the email address to send the appointment request to.", "Bitte geben Sie die E-Mail-Adresse an, an die ich die Terminanfrage senden soll.")
                session_states[session_id] = state
                memory.save_context({"user_input": user_query}, {"response": ask})
                return ask
            # Email available immediately -> send now
            subject, body, html_body = build_appointment_email_content(state, lang)
            success, message = send_email(recipient, subject, body, html_body)
            state["email_sent"] = success
            session_states[session_id] = state
            resp = (("✅ Email sent to " if lang.startswith("en") else "✅ E-Mail gesendet an ") + recipient) if success else (("⚠️ Failed to send: " if lang.startswith("en") else "⚠️ Versand fehlgeschlagen: ") + message)
            memory.save_context({"user_input": user_query}, {"response": resp})
            return resp
        elif any(tk in lower for tk in ["no", "nein", "stop", "cancel", "wait"]):
            ask = "What would you like to change: service, location, date, vehicle, or email?" if lang.startswith("en") else "Was möchten Sie anpassen: Service, Ort, Termin, Fahrzeug oder E-Mail?"
            session_states[session_id] = state
            memory.save_context({"user_input": user_query}, {"response": ask})
            return ask

    # Fallback: answer under the template
    result = llm.invoke([system, HumanMessage(content=f"Historie:\n{history_text}\n\nAnfrage:\n{q}")])
    text = result.content
    memory.save_context({"user_input": user_query}, {"response": text})
    return text
