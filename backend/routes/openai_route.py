from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from services.openai_service import OpenAIService
from pydantic import BaseModel

router = APIRouter(prefix="/openai", tags=["OpenAI Chat"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class OpenAIRequest(BaseModel):
    message: str

@router.post("/chat")
def openai_chat(req: OpenAIRequest, db: Session = Depends(get_db)):
    return OpenAIService.openai_chat(req.message, db)
