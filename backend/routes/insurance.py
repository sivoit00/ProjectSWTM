
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from agents.insurance_agent import run_insurance_agent

router = APIRouter()

class InsuranceRunRequest(BaseModel):
    user_id: Optional[str]
    user_input: str
    context: Optional[Dict[str, Any]] = {}

class InsuranceRunResponse(BaseModel):
    ok: bool
    response: Optional[Any] = None
    category: Optional[str] = None
    data_used: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/insurance/run", response_model=InsuranceRunResponse)
def run_insurance(req: InsuranceRunRequest):
    """
    Trigger endpoint für den Insurance Agent.
    Beispiel-Body:
    {
      "user_id": "cust-123",
      "user_input": "Wie hoch ist meine Deckung bei Diebstahl?",
      "context": {}
    }
    """
    res = run_insurance_agent(user_input=req.user_input, user_id=req.user_id, context=req.context or {})
    if not res.get("ok"):
        raise HTTPException(status_code=500, detail=res.get("error", "unknown"))
    # structured answer (not just string)
    return {
        "ok": True,
        "response": res.get("response"),
        "category": res.get("category"),
        "data_used": res.get("data_used")
    }
