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
    """Searches local DB for workshops that match city, zip, or name. Returns formatted text list."""
    db = SessionLocal()
    try:
        workshops = db.query(models.Werkstatt).all()
        if not workshops:
            return "❌ Keine Werkstätten in der Datenbank."

        q = (query or "").lower()
        filtered = []
        for w in workshops:
            if (w.ort and w.ort.lower() in q) or (w.plz and str(w.plz) in q) or (w.name and w.name.lower() in q):
                filtered.append(w)
        if not filtered:
            filtered = workshops[:10]
            prefix = "ℹ️ Keine exakte Übereinstimmung. Verfügbare Werkstätten:\n"
        else:
            prefix = f"✅ Gefundene Werkstätten ({len(filtered)}):\n"

        lines = [prefix]
        for w in filtered:
            lines.append(f"  • {w.name}\n    📍 {w.adresse}, {w.plz} {w.ort}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Datenbankfehler: {e}"
    finally:
        db.close()


@tool
def web_search_workshops(query: str) -> str:
    """Searches the web via Tavily for car workshops. Returns a concise formatted list with name, url, contacts."""
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    if not tavily_api_key:
        return "⚠️ Internet-Suche nicht verfügbar (TAVILY_API_KEY fehlt)."
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
            return f"🌐 Websuche: {query}\n{text}" if text else f"🌐 Websuche: {query}\n(keine Details verfügbar)"

        lines = [f"🌐 Websuche: {query}"]
        for it in items[:3]:
            name = it.get("title") or it.get("name") or "Werkstatt"
            url = it.get("url") or it.get("link") or ""
            content = (it.get("content") or it.get("snippet") or "").strip()
            lines.append(f"• {name}\n   🔗 {url}\n   {content[:160]}")
        return "\n".join(lines)
    except Exception as e:
        return f"❌ Websuche fehlgeschlagen: {e}"


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

    # Initialize minimal session state for gating
    state = session_states.get(session_id) or {
        "fields": {
            "service": state_data.get("service",""),
            "location": state_data.get("location",""),
            "user_email": get_user_email(session_id) or (user_context or {}).get("email") or "",
            "phone": state_data.get("phone",""),
            "vehicle": state_data.get("vehicle",""),
        },
        "phase": "collect"
    }

    # Let the LLM decide intent (search vs general, wants_email) without keywords
    q = user_query.strip()
    intent_prompt = (
        "Decide based on the request whether a workshop search should be performed."
        "Return a JSON with fields: search (true/false), wants_email (true/false), query (string)."
        "Consider the conversation history. Respond ONLY with JSON."
    )
    intent_msg = llm.invoke([
        SystemMessage(content=intent_prompt),
        HumanMessage(content=f"Historie:\n{history_text}\n\nAnfrage:\n{q}")
    ])
    import json as _json
    wants_email = False
    search_intent = False
    llm_query = q
    try:
        decision = _json.loads(intent_msg.content)
        search_intent = bool(decision.get("search", False))
        wants_email = bool(decision.get("wants_email", False))
        llm_query = decision.get("query") or q
    except Exception:
        # Fallback: default to no-search
        search_intent = False
        wants_email = False
        llm_query = q

    # Try structured capture to fill missing fields before acting
    import json as _json
    capture_template = system_content + "\n\nCAPTURE_JSON"
    cap_msg = llm.invoke([
        SystemMessage(content=capture_template),
        HumanMessage(content=f"Historie:\n{history_text}\n\nAnfrage:\n{q}")
    ])
    try:
        cap = _json.loads(cap_msg.content)
        for k in ["service","location","user_email","phone","vehicle"]:
            v = cap.get(k)
            if v and not (isinstance(v,str) and v.strip()==""):
                state["fields"][k] = v
    except Exception:
        pass

    # Gate search: require service and location
    need_service = not state["fields"].get("service")
    need_location = not state["fields"].get("location")
    if search_intent:
        if need_location:
            # Location is essential for meaningful results
            ask = "In welcher Stadt oder Postleitzahl soll ich suchen?"
            session_states[session_id] = state
            memory.save_context({"user_input": user_query}, {"response": ask})
            return ask
        # Run search when we have location; include service if available
        parts = [state["fields"].get("service"), state["fields"].get("location")]
        search_query = " ".join([p for p in parts if p]).strip()
        if not search_query:
            search_query = state["fields"].get("location")
        db_text = db_search_workshops.invoke({"query": search_query})
        web_text = web_search_workshops.invoke({"query": llm_query or search_query})
        combined = f"{db_text}\n\n{web_text}".strip()

        response = combined
        if wants_email:
            user_email = state["fields"].get("user_email") or get_user_email(session_id)
            if user_email:
                subject, body = format_workshop_recommendation_email("Kunde", combined)
                html_body = create_workshop_recommendation_html("Kunde", combined)
                success, message = send_email(user_email, subject, body, html_body)
                if success:
                    response += f"\n\n✅ {message}"
                else:
                    response += f"\n\n⚠️ {message}"
            else:
                response += "\n\n⚠️ Um die Ergebnisse per E-Mail zu erhalten, bitte zuerst Ihre E-Mail-Adresse angeben."

        session_states[session_id] = state
        memory.save_context({"user_input": user_query}, {"response": response})
        return response

    # General reply when not searching
    result = llm.invoke([system, HumanMessage(content=f"Historie:\n{history_text}\n\nAnfrage:\n{llm_query}")])
    text = result.content
    memory.save_context({"user_input": user_query}, {"response": text})
    return text
