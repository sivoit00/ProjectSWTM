from typing import Optional, List, Dict
import os
from langchain_openai import ChatOpenAI
from langchain import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
import pathlib
from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain_tavily import TavilySearch
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from agents.email_service import send_email, create_workshop_recommendation_html, format_workshop_recommendation_email, parse_workshops_from_text

conversation_memories: Dict[str, ConversationBufferMemory] = {}
session_user_emails: Dict[str, str] = {}
session_states: Dict[str, dict] = {}


TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


def _load_template_file(name: str) -> str:
    p = os.path.join(TEMPLATES_DIR, name)
    try:
        with open(p, "r", encoding="utf-8") as fh:
            return fh.read()
    except Exception:
        return ""


def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Gets or creates a memory for a session"""
    if session_id not in conversation_memories:
        conversation_memories[session_id] = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="user_input",
            output_key="response"
        )
    return conversation_memories[session_id]


def clear_session_memory(session_id: str):
    """Deletes the memory of a session"""
    if session_id in conversation_memories:
        del conversation_memories[session_id]
    if session_id in session_user_emails:
        del session_user_emails[session_id]
    if session_id in session_states:
        del session_states[session_id]


def set_user_email(session_id: str, email: str) -> None:
    """Store user's email address for a specific session."""
    session_user_emails[session_id] = email


def get_user_email(session_id: str) -> Optional[str]:
    """Retrieve user's email address for a specific session."""
    return session_user_emails.get(session_id)


def is_session_active(session_id: str) -> bool:
    """Return True if there is an in-progress (not done) appointment workflow for this session."""
    state = session_states.get(session_id)
    if not state:
        return False
    return state.get('phase') not in (None, 'done')


def run_repair_agent_with_memory(user_query: str, session_id: str = "default", user_context: Optional[Dict] = None) -> str:
    """
    Sequential Chain with 2 agents + conversational memory:
    
    AGENT 1 (Classification Agent):
    - Receives the request
    - Has access to chat history
    - Analyzes if it's about workshop search
    - Extracts relevant parameters (ZIP, city, vehicle type)
    - Decides: Forward to Agent 2 or answer directly
    
    AGENT 2 (Workshop Search Agent):
    - Only activated for workshop searches
    - Knows the previous conversation
    - Searches the internet for workshops
    - Searches the local database
    - Combines both sources into a recommendation
    
    Memory:
    - Stores all messages in the session
    - session_id enables multiple parallel conversations
    - Chat history is considered with every request
    
    Example Flow:
    User 1: "Find me a workshop"
    Bot 1: "In which city are you searching?"
    User 2: "Berlin"  ← Agent remembers previous question
    Bot 2: "Here are workshops in Berlin..."
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    
    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    llm = ChatOpenAI(openai_api_key=api_key, model_name=model_name, temperature=0.3)
    
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
   

    response = ""

   
    import re

    def extract_email(text: str) -> Optional[str]:
        m = re.search(r"([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,6})", text)
        return m.group(1) if m else None

    def likely_workshop_query(text: str) -> bool:
        keywords = ["werkstatt", "werkstätten", "autowerkstatt", "repair", "reparatur", "werkstatt in", "finde", "find", "service", "inspektion", "tire", "reifen"]
        t = text.lower()
        return any(k in t for k in keywords)

    def is_appointment_request(text: str) -> bool:
        t = text.lower()
        keywords = ["termin", "vereinbaren", "termin vereinbaren", "appointment", "book", "wanna book", "termin anfrage", "terminanfrage"]
        return any(k in t for k in keywords)

    def persist_session_state(session_id: str, state: dict):
        session_states[session_id] = state

    def load_session_state(session_id: str) -> dict:
        return session_states.get(session_id, {})

    def extract_phone(text: str) -> Optional[str]:
        import re as _re
        if not text:
            return None
        t = text.strip()
        
        m = _re.search(r"(\+?\d[\d\s\-/()]{4,}\d)|(^\d{6,}$)", t)
        if m:
            phone = m.group(0)
            phone_norm = _re.sub(r"[\s\-()]+", "", phone)
            return phone_norm
        return None

    def extract_location(text: str) -> Optional[str]:
      
        m = re.search(r"\b(\d{5})\b", text)
        if m:
            return m.group(1)
       
        m2 = re.search(r"in\s+([A-Za-zÄÖÜäöüß\- ]{2,40})", text)
        if m2:
            return m2.group(1).strip()
       
        single = re.fullmatch(r"[A-Za-zÄÖÜäöüß\-]{2,40}", text.strip())
        if single:
            return text.strip()
        return None

    def extract_service(text: str) -> Optional[str]:
        if not text:
            return None
        t = text.lower()
        
        services = [
            "inspektion", "ölwechsel", "bremsen", "reifen", "tüv", "klimaanlage",
            "diagnose", "wartung", "service", "kundendienst"
        ]
        for s in services:
            if s in t:
                return s.capitalize()
       
        import re as _re
        if _re.fullmatch(r"[A-Za-zÄÖÜäöüß]+", text.strip()) and len(text.strip()) <= 30:
            return text.strip().capitalize()
        return None

    def extract_preferred_date(text: str) -> Optional[str]:
        """Extract a date/time expression (German style like 01.12, 01.12.2025 13:00, 1.12 13 Uhr). Returns normalized string."""
        if not text:
            return None
        import re as _re
        t = text.strip()
        
        date_pattern = r"(\b\d{1,2}[\.\-/]\d{1,2}(?:[\.\-/]\d{2,4})?)"
        time_pattern = r"(\b\d{1,2}[:\.]\d{2}\b|\b\d{1,2}\s*Uhr\b)"
        dt_pattern = _re.compile(fr"{date_pattern}(?:\s+um\s+{time_pattern}|\s+{time_pattern})?", _re.IGNORECASE)
        m = dt_pattern.search(t)
        if m:
            
            return _re.sub(r"\s+", " ", m.group(0)).strip()
       
        time_only = _re.search(time_pattern, t)
        if time_only:
            return time_only.group(0)
       
        if _re.fullmatch(r"(heute|morgen|übermorgen|nachmittag|vormittag|abend)", t.lower()):
            return t.lower()
        return None

   
    user_email_candidate = extract_email(user_query)
    if user_email_candidate:
        set_user_email(session_id, user_email_candidate)
        response += f"✅ Email address saved: {user_email_candidate}\n\n"

    wants_email = bool(re.search(r"\b(email|e-mail|send|mail)\b", user_query.lower())) or bool(user_email_candidate)

  
    existing_state = load_session_state(session_id)
    in_progress = bool(existing_state) and existing_state.get('phase') != 'done'

   
    if is_appointment_request(user_query) or is_appointment_request(history_text) or in_progress:
        state = load_session_state(session_id)

       
        if not state:
            state = {"phase": "collect_info", "data": {}, "candidates": []}

     
        base_fields = ["user_name", "user_email", "phone", "vehicle", "had_accident", "damage_description", "service", "preferred_date", "location"]
        required_fields = base_fields

        
        if user_context and isinstance(user_context, dict):
            if user_context.get("name"):
                state["data"]["user_name"] = user_context.get("name")
            if user_context.get("email"):
                state["data"]["user_email"] = user_context.get("email")

        
        email_candidate = extract_email(user_query)
        if email_candidate:
            state["data"]["user_email"] = email_candidate

        location_candidate = extract_location(user_query)
        if location_candidate:
            state["data"]["location"] = location_candidate

        phone_candidate = extract_phone(user_query)
        if phone_candidate:
            state["data"]["phone"] = phone_candidate

        service_candidate = None
        if not state["data"].get("service"):
            service_candidate = extract_service(user_query)
            if service_candidate:
                state["data"]["service"] = service_candidate

        preferred_date_candidate = None
        if not state["data"].get("preferred_date"):
            preferred_date_candidate = extract_preferred_date(user_query)
            if preferred_date_candidate:
                state["data"]["preferred_date"] = preferred_date_candidate

        
        def extract_accident_answer(text: str):
            if not text:
                return None
            t = text.lower()
            yes_tokens = ["ja", "j", "hatte einen unfall", "unfall", "crash", "kollision"]
            no_tokens = ["nein", "n", "kein unfall", "keinen unfall"]
            for y in yes_tokens:
                if y in t:
                    return True
            for n in no_tokens:
                if n in t:
                    return False
            return None

        # Early capture of accident yes/no to avoid repeating the question
        if state["data"].get("had_accident") is None:
            accident_answer = extract_accident_answer(user_query)
            if accident_answer is not None:
                state["data"]["had_accident"] = accident_answer
                # Persist updated state immediately
                persist_session_state(session_id, state)
    
        if state["data"].get("had_accident") is True and not state["data"].get("damage_description"):
           
            import re as _rex
            if extract_accident_answer(user_query) is None:
                
                if len(user_query.strip()) >= 5:
                    state["data"]["damage_description"] = user_query.strip()

       
        import re as _re
        vmatch = _re.search(r"(\b[A-Za-z]{2,}\b)\s*(\d{4})", user_query)
        if vmatch and "vehicle" not in state["data"]:
            state["data"]["vehicle"] = f"{vmatch.group(1)} {vmatch.group(2)}"

      
        # Load central template for generating phrasing
        general_template = _load_template_file("repair_general.md") or """
You are a vehicle service assistant.

CHAT HISTORY:
{chat_history}

CURRENT REQUEST:
{user_input}

Answer the question in a friendly and helpful manner.
Consider the context from the chat history.
Answer in German unless user requests English.
"""

        # Prepare optional damage line and partial variables to satisfy template placeholders
        optional_damage_line = ""
        if state["data"].get("had_accident") is True and state["data"].get("damage_description"):
            optional_damage_line = f"Schadensbeschreibung: {state['data'].get('damage_description')}"

        general_chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                template=general_template,
                input_variables=["chat_history", "user_input"],
                partial_variables={
                    "user_name": state["data"].get("user_name", ""),
                    "user_email": state["data"].get("user_email", ""),
                    "phone": state["data"].get("phone", ""),
                    "vehicle": state["data"].get("vehicle", ""),
                    "service": state["data"].get("service", ""),
                    "preferred_date": state["data"].get("preferred_date", ""),
                    "damage_description": state["data"].get("damage_description", ""),
                    "optional_damage_line": optional_damage_line,
                }
            )
        )

        def ask_with_template(missing_field: str, state_data: dict) -> str:
            # Build a concise instruction leveraging the template to phrase the question
            field_map = {
                "user_name": "Bitte Ihren vollständigen Namen angeben.",
                "user_email": "Bitte Ihre E-Mail-Adresse für Rückmeldungen angeben.",
                "phone": "Unter welcher Telefonnummer können Sie erreicht werden?",
                "vehicle": "Welches Fahrzeug (Marke, Modell, Baujahr) betrifft die Anfrage?",
                "had_accident": "Hatten Sie einen Unfall mit dem Fahrzeug? (ja/nein)",
                "damage_description": "Bitte beschreiben Sie kurz die entstandenen Schäden.",
                "service": "Aus welchem Grund soll der Termin vereinbart werden? (z.B. Inspektion, Ölwechsel, Bremsen, TÜV, Diagnose)",
                "preferred_date": "Welches Datum / Zeit bevorzugen Sie für den Termin?",
                "location": "In welcher Stadt oder Postleitzahl suchen Sie?"
            }
            base = field_map.get(missing_field, f"Bitte geben Sie {missing_field} an.")
            instruction = f"{base} Kontext: {state_data}"
            result = general_chain.invoke({
                "chat_history": history_text,
                "user_input": instruction
            })
            return result.get("text") or base

        if state.get("phase") == "collect_info":
            for field in required_fields:
               
                # Skip damage description if no accident
                if field == "damage_description" and state["data"].get("had_accident") is False:
                    continue
                if not state["data"].get(field):
                    # If field is had_accident and user already answered in this message, do not re-ask
                    if field == "had_accident" and state["data"].get("had_accident") is not None:
                        continue
                    question = ask_with_template(field, state["data"]) 
                    persist_session_state(session_id, state)
                    memory.save_context({"user_input": user_query}, {"response": question})
                    return question

            
            state["phase"] = "present_options"
            persist_session_state(session_id, state)

        if state.get("phase") == "present_options":
            # Build search query and gather candidates from DB and web
            loc = state["data"].get("location")
            damage_part = state["data"].get("damage_description") or ""
            query_for_search = f"{state['data'].get('service')} {damage_part} {loc}".strip()
            db_results, workshops_list = search_workshops_in_db(query_for_search, "WORKSHOP_SEARCH", history_text)
            web_results = search_workshops_in_web(query_for_search, "WORKSHOP_SEARCH")

            import json as _json
            candidates = []
            try:
                parsed = _json.loads(web_results)
                results = parsed.get("results", [])
                for r in results:
                    candidates.append(r)
            except Exception:
                candidates = []

            # add DB workshops as candidates
            for w in workshops_list:
                try:
                    candidates.append({
                        "name": w.name,
                        "url": getattr(w, "homepage", "") or "",
                        "content": f"{w.adresse}, {w.plz} {w.ort}",
                        "phone": getattr(w, "telefon", None) or getattr(w, "phone", None) or None,
                        "email": getattr(w, "email", None) or None,
                        "score": 0.5
                    })
                except Exception:
                    continue

            # dedupe and limit to 3
            seen = set()
            unique = []
            for c in candidates:
                key = (c.get("name"), c.get("email"), c.get("url"))
                if key in seen:
                    continue
                seen.add(key)
                unique.append(c)
                if len(unique) >= 3:
                    break

            state["candidates"] = unique
            state["phase"] = "await_selection"
            persist_session_state(session_id, state)

            if not unique:
                response_text = "Leider konnte ich keine geeigneten Werkstätten in Ihrer Nähe finden. Möchten Sie eine größere Suche versuchen?"
                memory.save_context({"user_input": user_query}, {"response": response_text})
                return response_text

            # present options
            lines = ["Ich habe folgende 3 Werkstätten gefunden:"]
            for i, c in enumerate(unique, 1):
                name = c.get("name") or f"Werkstatt {i}"
                phone = c.get("phone") or "keine Nummer"
                email = c.get("email") or "keine E-Mail"
                snippet = (c.get("content") or "")[:140]
                lines.append(f"{i}) {name} — 📞 {phone} — ✉️ {email}\n   {snippet}")

            lines.append("Bitte wählen Sie eine Werkstatt per Nummer (z.B. 1) oder geben Sie 'abbrechen'.")
            message = "\n".join(lines)
            memory.save_context({"user_input": user_query}, {"response": message})
            return message

        # awaiting selection
        if state.get("phase") == "await_selection":
            # if user now replies with a number, handle selection
            import re as __re
            sel = None
            m = __re.search(r"\b([1-3])\b", user_query)
            if m:
                sel = int(m.group(1)) - 1
                candidates = state.get('candidates', [])
                if 0 <= sel < len(candidates):
                    chosen = candidates[sel]
                    # confirm sending
                    state['chosen'] = chosen
                    state['phase'] = 'confirm_send'
                    persist_session_state(session_id, state)
                    confirm = f"Möchten Sie, dass ich jetzt eine Terminanfrage an {chosen.get('name')} schicke (E-Mail: {chosen.get('email')}) für {state['data'].get('service')} am {state['data'].get('preferred_date')}?"
                    memory.save_context({"user_input": user_query}, {"response": confirm})
                    return confirm

            # else, not a valid selection
            message = "Bitte wählen Sie eine gültige Nummer aus der Liste (1-3), oder geben Sie weitere Informationen an."
            memory.save_context({"user_input": user_query}, {"response": message})
            return message

        if state.get('phase') == 'confirm_send':
            # user confirms
            if user_query.strip().lower() in ['ja', 'j', 'yes', 'bestätigen', 'ok']:
                chosen = state.get('chosen')
                if not chosen or not chosen.get('email'):
                    message = "Die ausgewählte Werkstatt hat keine E-Mail-Adresse. Möchten Sie eine andere Werkstatt wählen oder möchten Sie, dass ich die Telefonnummer anzeige?"
                    memory.save_context({"user_input": user_query}, {"response": message})
                    return message

                # compose email
                user_name = state['data'].get('user_name')
                phone = state['data'].get('phone')
                email = state['data'].get('user_email')
                subject = f"Terminanfrage: {state['data'].get('service')} für {user_name}"
                damage_line = ""
                if state['data'].get('had_accident') is True and state['data'].get('damage_description'):
                    damage_line = f"Schadensbeschreibung: {state['data'].get('damage_description')}"
                body_lines = [
                    "Sehr geehrte Damen und Herren,",
                    "",
                    f"ich möchte gerne einen Termin für {state['data'].get('service')} für mein Fahrzeug ({state['data'].get('vehicle')}) vereinbaren.",
                    f"Bevorzugtes Datum/Zeit: {state['data'].get('preferred_date')}",
                    damage_line,
                    "",
                    f"Bitte kontaktieren Sie mich unter {phone} oder {email} zur Bestätigung.",
                    "",
                    "Mit freundlichen Grüßen",
                    f"{user_name}"
                ]
                body_lines = [l for l in body_lines if l is not None and l != ""]
                body = "\n".join(body_lines)
                html_body = None
                success, msg = send_email(chosen.get('email'), subject, body, html_body)
                if success:
                    state['phase'] = 'done'
                    state['sent'] = {'to': chosen.get('email'), 'subject': subject, 'body': body}
                    persist_session_state(session_id, state)
                    reply = f"✅ E-Mail gesendet an {chosen.get('name')} ({chosen.get('email')}). Ich melde mich, sobald es eine Antwort gibt."
                else:
                    reply = f"⚠️ Fehler beim Senden der E-Mail: {msg}"
                memory.save_context({"user_input": user_query}, {"response": reply})
                return reply
            else:
                memory.save_context({"user_input": user_query}, {"response": "Okay, der Versand wurde abgebrochen. Möchten Sie eine andere Werkstatt wählen?"})
                # Return to selection of existing candidates
                state['phase'] = 'await_selection'
                persist_session_state(session_id, state)
                return "Abgebrochen. Bitte wählen Sie eine andere Werkstatt (1-3)."

    # Decide if the user requests a workshop search
    if likely_workshop_query(user_query) or likely_workshop_query(history_text):
        location = extract_location(user_query) or extract_location(history_text)

        if not location:
            # Ask for missing location information
            response += "In welcher Stadt oder Postleitzahl soll ich nach Werkstätten suchen?"
            memory.save_context({"user_input": user_query}, {"response": response})
            return response

        # perform DB + web searches
        db_results, workshops_list = search_workshops_in_db(user_query + f" {location}", "WORKSHOP_SEARCH", history_text)
        web_results = search_workshops_in_web(user_query + f" {location}", "WORKSHOP_SEARCH")

        # build a friendly combined response
        # web_results may be a JSON string with {'query':..., 'results':[...]} (from search_workshops_in_web)
        web_text = ""
        try:
            import json
            parsed = json.loads(web_results)
            results = parsed.get('results') if isinstance(parsed, dict) else parsed
            if results and isinstance(results, list):
                web_lines = [f"🌐 Internet search results for: {parsed.get('query','')}"]
                for w in results:
                    name = w.get('name') or w.get('title') or 'Unnamed workshop'
                    url = w.get('url') or ''
                    phone = w.get('phone') or ''
                    email = w.get('email') or ''
                    score = w.get('score', 0)
                    content = (w.get('content') or '').strip()
                    snippet = (content[:160] + '...') if content and len(content) > 160 else content

                    web_lines.append(f"• {name}")
                    if url:
                        web_lines.append(f"    🔗 {url}")
                    if phone:
                        web_lines.append(f"    📞 {phone}")
                    if email:
                        web_lines.append(f"    ✉️ {email}")
                    web_lines.append(f"    ⭐ Score: {round(float(score),3)}")
                    if snippet:
                        web_lines.append(f"    {snippet}")
                    web_lines.append("")

                web_text = "\n".join(web_lines)
            else:
                web_text = str(web_results)
        except Exception:
            web_text = str(web_results)

        combined = f"{db_results}\n\n{web_text}"
        response += combined

        if wants_email:
            user_email = get_user_email(session_id)
            if user_email:
                subject, body = format_workshop_recommendation_email("Customer", combined)
                html_body = create_workshop_recommendation_html("Customer", combined)
                success, message = send_email(user_email, subject, body, html_body)
                if success:
                    response += f"\n\n✅ {message}"
                else:
                    response += f"\n\n⚠️ {message}"
            else:
                response += "\n\n⚠️ Um die Ergebnisse per E-Mail zu erhalten, bitte zuerst Ihre E-Mail-Adresse angeben."

        memory.save_context({"user_input": user_query}, {"response": response})
        return response

    # fallback: general answer using a lightweight inline LLM prompt loaded from markdown
    general_template = _load_template_file("repair_general.md") or """You are a vehicle service assistant.

CHAT HISTORY:
{chat_history}

CURRENT REQUEST:
{user_input}

Answer the question in a friendly and helpful manner.
Consider the context from the chat history.
Answer in German unless user requests English.
"""

    # Provide empty partials for optional placeholders used in the markdown template
    general_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            template=general_template,
            input_variables=["chat_history", "user_input"],
            partial_variables={
                "user_name": "",
                "user_email": "",
                "phone": "",
                "vehicle": "",
                "service": "",
                "preferred_date": "",
                "damage_description": "",
                "optional_damage_line": "",
            }
        )
    )

    general_result = general_chain.invoke({
        "chat_history": history_text,
        "user_input": user_query
    })

    response += general_result["text"]

    memory.save_context({"user_input": user_query}, {"response": response})

    return response




def format_chat_history(messages: List) -> str:
    """Formats the chat history for the prompt"""
    if not messages:
        return "No previous messages yet."
    
    formatted = []
    for msg in messages:
        if hasattr(msg, 'type'):
            if msg.type == 'human':
                formatted.append(f"User: {msg.content}")
            elif msg.type == 'ai':
                formatted.append(f"Bot: {msg.content}")
    
    return "\n".join(formatted) if formatted else "No previous messages yet."


def search_workshops_in_db(user_query: str, classification: str, chat_history: str) -> tuple[str, list]:
    """Searches the workshop database (with context from history)
    
    Returns:
        tuple: (formatted_string, workshops_list)
    """
    db = SessionLocal()
    try:
        query_lower = user_query.lower()
        combined_text = f"{user_query} {classification} {chat_history}".lower()
        
        # Use the project's Werkstatt model (German naming)
        workshops = db.query(models.Werkstatt).all()
        
        if not workshops:
            return "❌ No workshops available in our database.", []
        
        
        filtered = []
        for w in workshops:
            city_match = w.ort and w.ort.lower() in combined_text 
            zip_match = w.plz and str(w.plz) in combined_text  
            name_match = w.name and w.name.lower() in combined_text
            
            if city_match or zip_match or name_match:
                filtered.append(w)
        
        if not filtered:
            filtered = workshops[:10]
            prefix = "ℹ️ No exact match. All available workshops:\n"
        else:
            prefix = f"✅ Found workshops in our database ({len(filtered)}):\n"
        
        result = prefix
        for w in filtered:
            order_count = len(w.auftraege) if hasattr(w, 'auftraege') else 0  
            result += f"  • {w.name}\n"
            result += f"    📍 {w.adresse}, {w.plz} {w.ort}\n"  
            result += f"    📊 Orders: {order_count}\n"
            result += f"    🆔 ID: {w.id}\n\n"
        
        return result, filtered
        
    except Exception as e:
        return f"❌ Database access error: {str(e)}", []
    finally:
        db.close()


def search_workshops_in_web(user_query: str, classification: str) -> str:
    """Searches the internet for workshops"""
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_api_key:
        return "⚠️ Internet search not available (TAVILY_API_KEY missing in .env)"

    try:
        search_query = extract_search_query(user_query, classification)

        search = TavilySearch(
            api_key=tavily_api_key,
            max_results=3,
            search_depth="basic",
            include_answer=True
        )

        results = search.run(search_query)

        # Normalize results into a list of workshop dicts
        workshops: list[dict] = []

        # If the tool returns a Python/list-like structure already, try to use it
        if isinstance(results, list):
            raw_list = results
        else:
            # try to parse structured dicts from text using existing parser
            raw_list = parse_workshops_from_text(str(results))

        # raw_list may be list of dicts with keys title/url/content/score
        for item in raw_list:
            # item may already be a dict from Tavily; if not, ensure keys exist
            if not isinstance(item, dict):
                continue
            title = item.get('title') or item.get('name') or item.get('name') or item.get('title') or ''
            url = item.get('url') or item.get('link') or ''
            content = item.get('content') or item.get('description') or item.get('snippet') or ''
            score = item.get('score') or item.get('relevance') or 0

            # extract phone and email if present in content
            phone = None
            email = None
            import re
            phone_match = re.search(r"(\+?\d[\d\s\-/()]{6,}\d)", content)
            if phone_match:
                phone = phone_match.group(1).strip()
            email_match = re.search(r"([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,6})", content)
            if email_match:
                email = email_match.group(1)

            ws = {
                'name': title.strip(),
                'url': url,
                'content': content.strip(),
                'score': float(score) if isinstance(score, (int, float, str)) and str(score) != '' else 0.0,
                'phone': phone,
                'email': email,
            }
            workshops.append(ws)

        # If parse_workshops_from_text returned minimal data (no scores), try to compute a simple score
        if workshops and all((not w.get('score') or w.get('score') == 0) for w in workshops):
            for w in workshops:
                s = 0.0
                if w.get('url'):
                    s += 0.05
                if w.get('phone'):
                    s += 0.02
                if 'review' in (w.get('content') or '').lower():
                    s += 0.03
                w['score'] = round(s + 0.01, 4)

        # sort by score desc and limit to 3
        workshops_sorted = sorted(workshops, key=lambda x: x.get('score', 0), reverse=True)[:3]

        # Return structured JSON string for downstream processing
        import json
        return json.dumps({'query': search_query, 'results': workshops_sorted}, ensure_ascii=False)

    except Exception as e:
        return f"❌ Internet search failed: {str(e)}"


def extract_search_query(user_query: str, classification: str) -> str:
    """Creates optimized search query for internet"""
    location = None
    
    if "Location/ZIP:" in classification:
        lines = classification.split("\n")
        for line in lines:
            if "Location/ZIP:" in line:
                location = line.split("Location/ZIP:")[1].strip().replace("[", "").replace("]", "")
                break
    
    if location and location.lower() not in ["none", "not available", "n/a"]:
        return f"car workshop auto repair {location} reviews recommendation"
    else:
        return f"car workshop {user_query}"
