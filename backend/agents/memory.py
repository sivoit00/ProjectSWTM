
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

# Ein globaler Speicher für ALLE Sessions (Anwalt, Werkstatt, etc.)
# Key = Session-ID (z.B. "lawyer_user@mail.com" oder "repair_user@mail.com")
global_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in global_store:
        global_store[session_id] = ChatMessageHistory()
    return global_store[session_id]