"""
routes/guardrails.py

API-Endpoints für Guardrails-Validierung
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from services.guardrails_service import validate_request, validate_response

router = APIRouter()


class ValidateInputRequest(BaseModel):
    user_input: str
    context: Optional[Dict[str, Any]] = None


class ValidateInputResponse(BaseModel):
    valid: bool
    filtered_input: Optional[str] = None
    warnings: List[str] = []
    blocked_reason: Optional[str] = None


class ValidateOutputRequest(BaseModel):
    ai_response: str
    context: Optional[Dict[str, Any]] = None


class ValidateOutputResponse(BaseModel):
    valid: bool
    filtered_output: Optional[str] = None
    warnings: List[str] = []
    blocked_reason: Optional[str] = None


@router.post("/validate/input", response_model=ValidateInputResponse)
def validate_user_input(req: ValidateInputRequest):
    """
    Validiert Nutzereingaben vor der Verarbeitung durch AI-Agenten.
    
    Beispiel:
    {
        "user_input": "Meine Kreditkarte ist 1234567812345678",
        "context": {}
    }
    """
    try:
        result = validate_request(req.user_input, req.context)
        return ValidateInputResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validierungsfehler: {str(e)}")


@router.post("/validate/output", response_model=ValidateOutputResponse)
def validate_ai_output(req: ValidateOutputRequest):
    """
    Validiert AI-Ausgaben vor der Rückgabe an den Nutzer.
    
    Beispiel:
    {
        "ai_response": "Ihre Police deckt Schäden bis 50.000€.",
        "context": {"expected_data": {...}}
    }
    """
    try:
        result = validate_response(req.ai_response, req.context)
        return ValidateOutputResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validierungsfehler: {str(e)}")


@router.get("/health")
def health_check():
    """Einfacher Health-Check für Guardrails-Service"""
    return {"status": "healthy", "service": "guardrails"}
