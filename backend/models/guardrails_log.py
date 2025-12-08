from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer
from sqlalchemy.sql import func
from database import Base

class GuardrailsLog(Base):
    """
    Logs von blockierten oder verdächtigen Nachrichten für das Support-Team.
    """
    __tablename__ = "guardrails_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    user_name = Column(String(255), nullable=True)
    user_email = Column(String(255), nullable=True)
    
    # Original-Nachricht
    original_message = Column(Text, nullable=False)
    
    # Gefilterte Nachricht (falls sensible Daten entfernt wurden)
    filtered_message = Column(Text, nullable=True)
    
    # Was wurde erkannt
    violation_type = Column(String(100), nullable=False)  # z.B. "THREAT", "SENSITIVE_DATA", "FORBIDDEN_TOPIC"
    severity = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Details
    blocked_reason = Column(Text, nullable=True)
    warnings = Column(Text, nullable=True)  # JSON-Array als String
    
    # Status
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(255), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    
    # Action taken
    action_taken = Column(String(100), nullable=True)  # z.B. "BLOCKED", "WARNED", "ALLOWED_WITH_FILTER"
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    def __repr__(self):
        return f"<GuardrailsLog {self.id}: {self.violation_type} - {self.severity}>"
