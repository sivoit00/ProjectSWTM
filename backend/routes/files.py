from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/files", tags=["files"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png", ".gif", ".bmp"}

os.makedirs(UPLOAD_DIR, exist_ok=True)

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS

@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload multiple files (images or PDFs)
    
    - Maximum 5 files per request
    - Maximum 10MB per file
    - Allowed types: PDF, JPG, PNG, GIF, BMP
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
