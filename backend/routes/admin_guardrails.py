"""
routes/admin_guardrails.py

Admin-Endpoints für das Support-Team zum Einsehen von Guardrails-Logs
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from database import SessionLocal
from models.guardrails_log import GuardrailsLog
from sqlalchemy import desc
from auth.dependencies import require_role

router = APIRouter()


class GuardrailsLogResponse(BaseModel):
    id: int
    user_id: Optional[str]
    user_name: Optional[str]
    user_email: Optional[str]
    original_message: str
    filtered_message: Optional[str]
    violation_type: str
    severity: str
    blocked_reason: Optional[str]
    warnings: Optional[str]
    reviewed: bool
    reviewed_by: Optional[str]
    reviewed_at: Optional[datetime]
    action_taken: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/logs", response_model=List[GuardrailsLogResponse])
def get_guardrails_logs(
    severity: Optional[str] = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    reviewed: Optional[bool] = Query(None, description="Filter by reviewed status"),
    limit: int = Query(50, le=500, description="Max number of logs to return"),
    skip: int = Query(0, description="Number of logs to skip"),
    current_user: dict = Depends(require_role("admin"))
):
    """
    Abrufen aller Guardrails-Logs für das Support-Team.
    Zeigt problematische Nachrichten von Nutzern.
    """
    try:
        db = SessionLocal()
        query = db.query(GuardrailsLog)
        
        # Filter anwenden
        if severity:
            query = query.filter(GuardrailsLog.severity == severity.upper())
        if reviewed is not None:
            query = query.filter(GuardrailsLog.reviewed == reviewed)
        
        # Sortierung: Neueste zuerst
        query = query.order_by(desc(GuardrailsLog.created_at))
        
        # Pagination
        logs = query.offset(skip).limit(limit).all()
        db.close()
        
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der Logs: {str(e)}")


@router.get("/logs/{log_id}", response_model=GuardrailsLogResponse)
def get_guardrails_log(
    log_id: int,
    current_user: dict = Depends(require_role("admin"))
):
    """Einzelnen Guardrails-Log abrufen"""
    try:
        db = SessionLocal()
        log = db.query(GuardrailsLog).filter(GuardrailsLog.id == log_id).first()
        db.close()
        
        if not log:
            raise HTTPException(status_code=404, detail="Log nicht gefunden")
        
        return log
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler: {str(e)}")


class ReviewLogRequest(BaseModel):
    reviewed_by: str
    notes: Optional[str] = None


@router.patch("/logs/{log_id}/review")
def review_log(
    log_id: int,
    req: ReviewLogRequest,
    current_user: dict = Depends(require_role("admin"))
):
    """
    Markiere einen Log als überprüft.
    Support-Team kann damit anzeigen, dass sie die Nachricht gesehen haben.
    """
    try:
        db = SessionLocal()
        log = db.query(GuardrailsLog).filter(GuardrailsLog.id == log_id).first()
        
        if not log:
            db.close()
            raise HTTPException(status_code=404, detail="Log nicht gefunden")
        
        log.reviewed = True
        log.reviewed_by = req.reviewed_by
        log.reviewed_at = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return {"ok": True, "message": f"Log {log_id} als überprüft markiert"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler: {str(e)}")


@router.get("/stats")
def get_guardrails_stats():
    """Statistiken über Guardrails-Verstöße für das Dashboard"""
    try:
        db = SessionLocal()
        
        # Gesamtzahl
        total = db.query(GuardrailsLog).count()
        
        # Nach Severity
        critical = db.query(GuardrailsLog).filter(GuardrailsLog.severity == "CRITICAL").count()
        high = db.query(GuardrailsLog).filter(GuardrailsLog.severity == "HIGH").count()
        medium = db.query(GuardrailsLog).filter(GuardrailsLog.severity == "MEDIUM").count()
        low = db.query(GuardrailsLog).filter(GuardrailsLog.severity == "LOW").count()
        
        # Unreviewed
        unreviewed = db.query(GuardrailsLog).filter(GuardrailsLog.reviewed == False).count()
        
        # Nach Typ
        from sqlalchemy import func
        by_type = db.query(
            GuardrailsLog.violation_type,
            func.count(GuardrailsLog.id).label('count')
        ).group_by(GuardrailsLog.violation_type).all()
        
        db.close()
        
        return {
            "total": total,
            "unreviewed": unreviewed,
            "by_severity": {
                "CRITICAL": critical,
                "HIGH": high,
                "MEDIUM": medium,
                "LOW": low
            },
            "by_type": {row.violation_type: row.count for row in by_type}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler: {str(e)}")
