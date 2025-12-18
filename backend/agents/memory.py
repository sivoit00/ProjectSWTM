
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

global_store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in global_store:
        global_store[session_id] = ChatMessageHistory()
    return global_store[session_id]


def clear_session_history(session_id: str) -> None:
    """Clear chat history for a given session id.

    Centralized helper so routes/agents don't need to manipulate `global_store` directly.
    """
    try:
        if session_id in global_store:
            del global_store[session_id]
    except Exception:
        # Best-effort: clearing memory must never crash the request path.
        pass