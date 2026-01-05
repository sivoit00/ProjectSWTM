import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from database import SessionLocal
from models.chat_message import ChatMessage
from models.chat_conversation import ChatConversation
from schemas.chat_message_schema import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse
from schemas.chat_conversation_schema import ChatConversationResponse, ChatConversationRename

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/chat", tags=["chat"])


def _derive_conversation_title(raw_message: str) -> Optional[str]:
    if not raw_message:
        return None

    msg = " ".join(raw_message.strip().split())
    if not msg:
        return None

    lower = msg.lower()
    if lower.startswith("e-mail update") or lower.startswith("email update"):
        return None
    if re.match(r"^\[\d+\s+file\(s\)\s+uploaded\]$", msg):
        return None

    msg = msg.strip("\"'“”„“”")
    if not msg:
        return None

    stopwords = {
        "a", "an", "and", "are", "can", "could", "do", "for", "i", "im", "in", "is", "it", "me", "my",
        "please", "the", "to", "we", "with", "you",
        "aber", "als", "am", "an", "auch", "auf", "aus", "bei", "bin", "bis", "bitte", "das", "dass",
        "der", "die", "dich", "dir", "du", "ein", "eine", "einen", "einem", "einer", "er", "es", "euch",
        "für", "hab", "habe", "hat", "hatte", "hätten", "ich", "ihr", "ihre", "ihren", "ihrem", "ihres",
        "im", "in", "ist", "ja", "kann", "kannst", "können", "könnt", "mal", "man", "mein", "meine",
        "meinen", "meinem", "meiner", "mich", "mit", "muss", "müssen", "musst", "nach", "noch", "oder",
        "sein", "seine", "seinen", "seinem", "seiner", "sind", "so", "soll", "sollen", "sollte", "sollten",
        "um", "und", "uns", "unser", "unsere", "unter", "vom", "von", "war", "waren", "was", "weil",
        "wer", "wie", "wir", "wird", "wurde", "werden", "wollte", "zu", "zum", "zur",
    }

    keywords = {
        "werkstatt", "werkstatttermin", "termin", "unfall", "versicherung", "anwalt", "schaden", "gutachten",
        "rechnung", "kfz", "auto", "fahrzeug", "polizei", "gegner", "haftpflicht", "kasko",
    }

    # Tokenize (keep numbers and simple time tokens like 14, 14:00)
    tokens = re.findall(r"[A-Za-zÄÖÜäöüß0-9]+(?:[:.][0-9]+)?", msg)
    if not tokens:
        return None

    def is_noise(token: str) -> bool:
        t = token.strip().lower()
        if not t:
            return True
        if t in stopwords:
            return True
        # Drop very short filler tokens, keep numbers.
        if len(t) <= 2 and not any(ch.isdigit() for ch in t):
            return True
        return False

    # Prefer starting from the first domain keyword if present.
    kw_index: Optional[int] = None
    for idx, tok in enumerate(tokens):
        if tok.lower() in keywords:
            kw_index = idx
            break

    max_words = 4
    max_chars = 48

    picked: list[str] = []

    if kw_index is not None:
        # Collect forward from the keyword.
        for tok in tokens[kw_index:]:
            if is_noise(tok):
                continue
            if tok not in picked:
                picked.append(tok)
            if len(picked) >= max_words:
                break
        # If still short, prepend relevant words from before the keyword.
        if len(picked) < max_words:
            before: list[str] = []
            for tok in reversed(tokens[:kw_index]):
                if is_noise(tok):
                    continue
                if tok not in picked and tok not in before:
                    before.append(tok)
                if len(before) + len(picked) >= max_words:
                    break
            picked = list(reversed(before)) + picked
    else:
        for tok in tokens:
            if is_noise(tok):
                continue
            if tok not in picked:
                picked.append(tok)
            if len(picked) >= max_words:
                break

    if len(picked) < 2:
        return None

    title = " ".join(picked)
    title = title[:1].upper() + title[1:]
    if len(title) > max_chars:
        title = title[: max_chars - 1].rstrip() + "…"
    return title


def _get_or_create_conversation(db: Session, user_id: str, conversation_id: str) -> ChatConversation:
    conv = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .filter(ChatConversation.conversation_id == conversation_id)
        .first()
    )
    if conv:
        return conv

    conv = ChatConversation(
        user_id=user_id,
        conversation_id=conversation_id,
        title=None,
    )
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


def _touch_conversation(
    db: Session,
    user_id: str,
    conversation_id: str,
    *,
    title_if_missing: Optional[str] = None,
) -> None:
    conv = _get_or_create_conversation(db, user_id, conversation_id)
    if title_if_missing and (conv.title is None or str(conv.title).strip() == ""):
        conv.title = title_if_missing
    conv.updated_at = datetime.utcnow()
    db.commit()

@router.post("/save", response_model=ChatMessageResponse)
def save_chat_message(message: ChatMessageCreate, db: Session = Depends(get_db)):
    """Save a chat message to database"""
    conversation_id = message.conversation_id or "default"

    title_candidate: Optional[str] = None
    if (message.sender or "").strip().lower() in {"user", "customer", "human"}:
        title_candidate = _derive_conversation_title(message.message)

    db_message = ChatMessage(
        user_id=message.user_id,
        conversation_id=conversation_id,
        sender=message.sender,
        message=message.message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)

    _touch_conversation(db, message.user_id, conversation_id, title_if_missing=title_candidate)
    return db_message

@router.get("/history/{user_id}", response_model=ChatHistoryResponse)
def get_chat_history(
    user_id: str,
    limit: int = 100,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get chat history for a specific user"""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if conversation_id:
        query = query.filter(ChatMessage.conversation_id == conversation_id)

    messages = (
        query.order_by(ChatMessage.timestamp.asc())
        .limit(limit)
        .all()
    )
    
    return {
        "messages": messages,
        "total": len(messages)
    }

@router.delete("/history/{user_id}")
def clear_chat_history(
    user_id: str,
    conversation_id: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Clear chat history for a user (optionally scoped to one conversation)."""
    query = db.query(ChatMessage).filter(ChatMessage.user_id == user_id)
    if conversation_id:
        query = query.filter(ChatMessage.conversation_id == conversation_id)

    deleted = query.delete()
    db.commit()
    return {"deleted": deleted, "message": "Chat history cleared"}


@router.get(
    "/conversations/{user_id}/details",
    response_model=List[ChatConversationResponse],
)
def list_conversations(user_id: str, db: Session = Depends(get_db)):
    """Return known conversations for a user.

    Also backfills ChatConversation rows for any conversation_ids that exist in chat_messages.
    """
    conv_ids = [
        row[0]
        for row in (
            db.query(ChatMessage.conversation_id)
            .filter(ChatMessage.user_id == user_id)
            .distinct()
            .all()
        )
        if row[0]
    ]

    for cid in conv_ids:
        _get_or_create_conversation(db, user_id, cid)

    conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .order_by(ChatConversation.updated_at.desc())
        .all()
    )
    return conversations


@router.patch(
    "/conversations/{user_id}/{conversation_id}",
    response_model=ChatConversationResponse,
)
def rename_conversation(
    user_id: str,
    conversation_id: str,
    payload: ChatConversationRename,
    db: Session = Depends(get_db),
):
    conv = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .filter(ChatConversation.conversation_id == conversation_id)
        .first()
    )
    if not conv:
        conv = ChatConversation(user_id=user_id, conversation_id=conversation_id, title=None)
        db.add(conv)

    conv.title = payload.title
    conv.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conv)
    return conv


@router.delete("/conversations/{user_id}/{conversation_id}")
def delete_conversation(user_id: str, conversation_id: str, db: Session = Depends(get_db)):
    deleted_messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.user_id == user_id)
        .filter(ChatMessage.conversation_id == conversation_id)
        .delete()
    )

    deleted_conversations = (
        db.query(ChatConversation)
        .filter(ChatConversation.user_id == user_id)
        .filter(ChatConversation.conversation_id == conversation_id)
        .delete()
    )

    db.commit()
    return {
        "deleted_messages": deleted_messages,
        "deleted_conversations": deleted_conversations,
    }
