from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import List, Optional
import os
import uuid
from datetime import datetime
from auth.dependencies import get_current_user
from pydantic import BaseModel
import asyncio
import logging
import requests

from services import pgvector_instance
from services.build_vector_db import update_database

router = APIRouter(prefix="/files", tags=["files"])

log = logging.getLogger(__name__)

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webm",
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".ogg",
    ".mp4",
    ".txt"
}

AUDIO_EXTENSIONS = {".webm", ".wav", ".mp3", ".m4a", ".aac", ".ogg", ".mp4"}

os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def is_audio_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in AUDIO_EXTENSIONS


class TranscribeRequest(BaseModel):
    stored_filename: str
    language: Optional[str] = None


def _transcribe_with_openai(file_path: str, model: str, language: Optional[str]) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ist nicht konfiguriert")

    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {api_key}"}

    data: dict = {"model": model}
    if language:
        data["language"] = language

    with open(file_path, "rb") as f:
        files = {"file": (os.path.basename(file_path), f)}
        resp = requests.post(url, headers=headers, data=data, files=files, timeout=90)

    if resp.status_code >= 400:
        raise RuntimeError(f"Transcription failed: {resp.status_code} {resp.text}")

    payload = resp.json()
    text = (payload.get("text") or "").strip()
    if not text:
        raise RuntimeError("Empty transcription result")
    return text


@router.post("/transcribe")
async def transcribe_file(
    req: TranscribeRequest,
    current_user: dict = Depends(get_current_user),
):
    """Transcribe an already uploaded audio file and return its text."""

    stored = (req.stored_filename or "").strip()
    if not stored:
        raise HTTPException(400, "stored_filename is required")

    if not is_audio_file(stored):
        raise HTTPException(400, "Only audio files can be transcribed")

    file_path = os.path.join(UPLOAD_DIR, stored)
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")

    model = os.getenv("OPENAI_TRANSCRIBE_MODEL", "whisper-1")
    try:
        text = await asyncio.to_thread(_transcribe_with_openai, file_path, model, req.language)
        return {"success": True, "text": text, "model": model}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload multiple files (images, text files or PDFs)
    
    - Maximum 5 files per request
    - Maximum 10MB per file
    - Allowed types: PDF, Images, Text files, and common Audio formats
    """
    if len(files) > 5:
        raise HTTPException(400, "Maximum 5 files allowed per upload")
    
    uploaded_files = []
    
    for file in files:
        # Validate extension
        if not is_allowed_file(file.filename):
            raise HTTPException(400, f"File type not allowed: {file.filename}")
        
        # Read and validate size
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(400, f"File too large: {file.filename} (max 10MB)")
        
        # Generate unique filename
        file_ext = os.path.splitext(file.filename)[1]
        unique_name = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_name)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        uploaded_files.append({
            "filename": file.filename,
            "stored_filename": unique_name,
            "size": len(content),
            "uploaded_at": datetime.now().isoformat()
        })

    
    async def _refresh_vector_index():
        try:
            db = pgvector_instance.get()
            await asyncio.to_thread(update_database, db)
            log.info("Vector index updated after file upload ✅")
        except Exception as e:
            log.error(f"Vector index update failed after upload: {e}")

    try:
        asyncio.create_task(_refresh_vector_index())
    except RuntimeError:
        # Falls kein laufender Event-Loop vorhanden ist (z.B. bei Tests), synchron ausführen
        try:
            db = pgvector_instance.get()
            update_database(db)
        except Exception as e:
            log.error(f"Synchronous vector index update failed: {e}")

    return {
        "success": True,
        "files": uploaded_files
    }

@router.get("/uploads/{filename}")
async def get_file(filename: str):
    """Retrieve an uploaded file"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(404, "File not found")
    
    return FileResponse(file_path)
