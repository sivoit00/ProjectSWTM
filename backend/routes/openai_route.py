from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from pydantic import BaseModel
from services.werkstatt_web_agent import run_werkstatt_agent_sequential
import traceback

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LangChainRequest(BaseModel):
    message: str


class WerkstattAgentRequest(BaseModel):
    query: str


@router.post("/langchain/chat")
def langchain_chat(req: LangChainRequest, db: Session = Depends(get_db)):
    try:
        answer = run_werkstatt_agent_sequential(req.message)

        ki = KIAktion(nachricht=req.message, antwort=answer, auftrag_id=None)
        db.add(ki)
        db.commit()
        db.refresh(ki)

        return {"response": answer}
    except Exception as e:
        tb = traceback.format_exc()
        print("LangChain call failed:", tb)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/werkstatt-agent/search")
def werkstatt_agent_search(req: WerkstattAgentRequest, db: Session = Depends(get_db)):
    try:
        answer = run_werkstatt_agent_sequential(req.query)

        ki = KIAktion(nachricht=req.query, antwort=answer, auftrag_id=None)
        db.add(ki)
        db.commit()
        db.refresh(ki)

        return {
            "response": answer,
            "agent_type": "sequential_werkstatt_agent"
        }
    except Exception as e:
        tb = traceback.format_exc()
        print("Werkstatt-Agent call failed:", tb)
        raise HTTPException(status_code=500, detail=str(e))
