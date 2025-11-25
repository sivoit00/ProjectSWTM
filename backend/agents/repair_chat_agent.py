from typing import Optional, List, Dict
import os
from langchain_openai import ChatOpenAI
from langchain import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain_tavily import TavilySearch
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from agents.email_service import send_email, create_workshop_recommendation_html, format_workshop_recommendation_email, parse_workshops_from_text

import logging

log = logging.getLogger(__name__)

conversation_memories: Dict[str, ConversationBufferMemory] = {}
session_user_emails: Dict[str, str] = {}


def get_or_create_memory(session_id: str) -> ConversationBufferMemory:
    """Gets or creates a memory for a session"""
    if session_id not in conversation_memories:
        mem = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            input_key="user_input",
            output_key="response"
        )

        # try to hydrate memory from persisted chat messages
        try:
            db = SessionLocal()
            msgs = db.query(models.ChatMessage).filter(models.ChatMessage.user_id == session_id).order_by(models.ChatMessage.timestamp).all()
            for m in msgs:
                try:
                    if m.sender.lower() in ("user", "human"):
                        mem.chat_memory.add_user_message(m.message)
                    else:
                        mem.chat_memory.add_ai_message(m.message)
                except Exception:
                    # memory backend may not expose chat_memory helpers
                    pass
        except Exception as e:
            log.exception("Error hydrating memory for session %s: %s", session_id, e)
        finally:
            try:
                db.close()
            except Exception:
                pass

        conversation_memories[session_id] = mem
    return conversation_memories[session_id]


def clear_session_memory(session_id: str):
    """Deletes the memory of a session"""
    if session_id in conversation_memories:
        del conversation_memories[session_id]
    if session_id in session_user_emails:
        del session_user_emails[session_id]

    # Also remove persisted chat messages for this session
    try:
        db = SessionLocal()
        db.query(models.ChatMessage).filter(models.ChatMessage.user_id == session_id).delete()
        db.commit()
    except Exception as e:
        log.exception("Failed to clear persisted messages for session %s: %s", session_id, e)
    finally:
        try:
            db.close()
        except Exception:
            pass


def set_user_email(session_id: str, email: str) -> None:
    """Store user's email address for a specific session."""
    session_user_emails[session_id] = email


def get_user_email(session_id: str) -> Optional[str]:
    """Retrieve user's email address for a specific session."""
    return session_user_emails.get(session_id)


def run_repair_agent_with_memory(user_query: str, session_id: str = "default") -> str:
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
    
    model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    llm = ChatOpenAI(openai_api_key=api_key, model_name=model_name, temperature=0.3)
    
    memory = get_or_create_memory(session_id)
   
    classification_template = """You are Agent 1, a classification agent for vehicle service requests.

CHAT HISTORY:
{chat_history}

CURRENT REQUEST: {user_input}

Your task: 
1. CONSIDER the previous conversation
2. Analyze the current request in the context of the history
3. Decide if it should be forwarded to Agent 2 (Workshop Search Agent)

IMPORTANT: 
- If the user is responding to a previous question, use that context
- If information is missing (e.g. location), ask for it
- If enough info is available, forward

Return the following format:

CATEGORY: [WORKSHOP_SEARCH or OTHER or INQUIRY or EMAIL_REQUEST]

FORWARD: [YES or NO or MORE_INFO_NEEDED]

User wants email: [YES or NO]
User email address: [extract if provided, otherwise NONE]

EXTRACTED PARAMETERS (also from history):
- Location/ZIP: [if available]
- Vehicle type: [if available]
- Special requirements: [e.g. "good reviews", "cheap"]

REASONING: [Why this decision?]

INSTRUCTION FOR AGENT 2: [What should Agent 2 do specifically?]

Examples:
- User: "Find workshop" → INQUIRY (city missing), User wants email: NO, User email address: NONE
- User: "Berlin" (after previous question) → WORKSHOP_SEARCH, User wants email: NO, User email address: NONE
- User: "Send me results by email" → WORKSHOP_SEARCH, User wants email: YES, User email address: NONE
- User: "my email is john@example.com" → OTHER, User wants email: NO, User email address: john@example.com
- User: "john@example.com" → OTHER, User wants email: NO, User email address: john@example.com
- User: "Email results to test@gmail.com" → WORKSHOP_SEARCH, User wants email: YES, User email address: test@gmail.com
- User: "How often oil change?" → OTHER, User wants email: NO, User email address: NONE
"""
    
    # New flow: the orchestrator is responsible for routing. This function no longer runs
    # the previous Agent 1 classifier. Instead we use light heuristics and direct searches
    # or a general LLM reply depending on the user input and chat history.

    chat_history = memory.load_memory_variables({}).get("chat_history", [])
    history_text = format_chat_history(chat_history)

    response = ""

    # helpers
    import re

    def extract_email(text: str) -> Optional[str]:
        m = re.search(r"([\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,6})", text)
        return m.group(1) if m else None

    def likely_workshop_query(text: str) -> bool:
        keywords = ["werkstatt", "werkstätten", "autowerkstatt", "repair", "reparatur", "werkstatt in", "finde", "find", "service", "inspektion", "tire", "reifen"]
        t = text.lower()
        return any(k in t for k in keywords)

    def extract_location(text: str) -> Optional[str]:
        # try postal code
        m = re.search(r"\b(\d{5})\b", text)
        if m:
            return m.group(1)
        # try 'in <city>' pattern
        m2 = re.search(r"in\s+([A-Za-zÄÖÜäöüß\- ]{2,40})", text)
        if m2:
            return m2.group(1).strip()
        return None

    # extract email if present in user_query and store it
    user_email_candidate = extract_email(user_query)
    if user_email_candidate:
        set_user_email(session_id, user_email_candidate)
        response += f"✅ Email address saved: {user_email_candidate}\n\n"

    wants_email = bool(re.search(r"\b(email|e-mail|send|mail)\b", user_query.lower())) or bool(user_email_candidate)

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

    # fallback: general answer using LLM (no internal Agent 1 classifier)
    general_template = """You are a vehicle service assistant.

CHAT HISTORY:
{chat_history}

CURRENT REQUEST:
{user_input}

Answer the question in a friendly and helpful manner.
Consider the context from the chat history.
Answer in English.
"""

    general_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            template=general_template,
            input_variables=["chat_history", "user_input"]
        )
    )

    general_result = general_chain.invoke({
        "chat_history": history_text,
        "user_input": user_query
    })

    response += general_result["text"]

    memory.save_context({"user_input": user_query}, {"response": response})

    return response
    
  
    if email_match:
        extracted_email = email_match.group(1)
        if extracted_email and extracted_email != "NONE":
            response += f"\n\n✅ Email address saved: {extracted_email}"
    
    memory.save_context(
        {"user_input": user_query},
        {"response": response}
    )
    
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
            max_results=5,
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
