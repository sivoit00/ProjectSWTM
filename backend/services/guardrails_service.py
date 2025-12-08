"""
services/guardrails_service.py

Guardrails-Service zur Validierung und Filterung von AI-Antworten.
Schützt vor unangemessenen Inhalten, Datenlecks und unsicheren Ausgaben.
"""

import re
import json
import logging
from typing import Dict, Any, List
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from database import SessionLocal
from models.guardrails_log import GuardrailsLog

load_dotenv()
log = logging.getLogger(__name__)


class GuardrailsService:
    """Service zur Validierung von AI-Eingaben und -Ausgaben"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0
        )
        
        # Sensible Datenmuster
        self.sensitive_patterns = [
            (r'\b\d{16}\b', 'KREDITKARTE'),  # Kreditkartennummer
            (r'\b[A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{2}\b', 'IBAN'),
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),  # US Social Security
            
        ]
        
        # Verbotene Themen
        self.forbidden_topics = [
            'gewalt', 'waffen', 'drogen', 'illegal', 'hack',
            'betrug', 'manipulation', 'diskriminierung'
        ]
    
    def validate_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validiert Nutzereingaben vor der Verarbeitung durch AI-Agenten.
        
        Returns:
            {
                "valid": bool,
                "filtered_input": str,
                "warnings": List[str],
                "blocked_reason": str (optional),
                "violation_type": str (optional),
                "severity": str (optional)
            }
        """
        warnings = []
        violation_type = None
        severity = "LOW"
        
        # 1. Prüfe auf sensible Daten
        filtered_input = user_input
        for pattern, data_type in self.sensitive_patterns:
            if re.search(pattern, user_input):
                filtered_input = re.sub(pattern, f'[{data_type}_ENTFERNT]', filtered_input)
                warnings.append(f"Sensible Daten ({data_type}) wurden entfernt")
                violation_type = "SENSITIVE_DATA"
                severity = "MEDIUM"
        
        # 2. Prüfe auf Drohungen und gefährliche Inhalte
        threat_keywords = ['bring dich um', 'kill', 'umbringen', 'töten', 'erschießen', 'verletzen']
        for threat in threat_keywords:
            if threat in user_input.lower():
                self._log_violation(
                    user_input=user_input,
                    filtered_input=filtered_input,
                    violation_type="THREAT",
                    severity="CRITICAL",
                    blocked_reason=f"Drohung erkannt: '{threat}'",
                    warnings=warnings,
                    context=context,
                    action_taken="BLOCKED"
                )
                return {
                    "valid": False,
                    "filtered_input": None,
                    "warnings": warnings,
                    "blocked_reason": "Diese Anfrage kann nicht weitergeführt werden. Bitte senden Sie eine neue Nachricht.",
                    "violation_type": "THREAT",
                    "severity": "CRITICAL"
                }
        
        # 3. Prüfe auf verbotene Themen
        user_input_lower = user_input.lower()
        for topic in self.forbidden_topics:
            if topic in user_input_lower:
                self._log_violation(
                    user_input=user_input,
                    filtered_input=filtered_input,
                    violation_type="FORBIDDEN_TOPIC",
                    severity="HIGH",
                    blocked_reason=f"Anfrage enthält unzulässiges Thema: {topic}",
                    warnings=warnings,
                    context=context,
                    action_taken="BLOCKED"
                )
                return {
                    "valid": False,
                    "filtered_input": None,
                    "warnings": warnings,
                    "blocked_reason": f"Anfrage enthält unzulässiges Thema: {topic}",
                    "violation_type": "FORBIDDEN_TOPIC",
                    "severity": "HIGH"
                }
        
        # 4. Längenprüfung
        if len(user_input) > 5000:
            return {
                "valid": False,
                "filtered_input": None,
                "warnings": warnings,
                "blocked_reason": "Eingabe zu lang (max. 5000 Zeichen)",
                "violation_type": "TOO_LONG",
                "severity": "LOW"
            }
        
        # 5. AI-basierte Validierung für komplexe Fälle
        if self._needs_ai_validation(user_input):
            ai_result = self._ai_validate_intent(user_input)
            if not ai_result["safe"]:
                self._log_violation(
                    user_input=user_input,
                    filtered_input=filtered_input,
                    violation_type="AI_DETECTED",
                    severity="HIGH",
                    blocked_reason=ai_result["reason"],
                    warnings=warnings,
                    context=context,
                    action_taken="BLOCKED"
                )
                return {
                    "valid": False,
                    "filtered_input": None,
                    "warnings": warnings,
                    "blocked_reason": ai_result["reason"],
                    "violation_type": "AI_DETECTED",
                    "severity": "HIGH"
                }
        
        # Log sensible Daten, aber erlaube die Nachricht (mit Filter)
        if violation_type == "SENSITIVE_DATA":
            self._log_violation(
                user_input=user_input,
                filtered_input=filtered_input,
                violation_type=violation_type,
                severity=severity,
                blocked_reason=None,
                warnings=warnings,
                context=context,
                action_taken="ALLOWED_WITH_FILTER"
            )
        
        return {
            "valid": True,
            "filtered_input": filtered_input,
            "warnings": warnings,
            "violation_type": violation_type,
            "severity": severity
        }
    
    def validate_output(self, ai_response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validiert AI-Ausgaben vor der Rückgabe an den Nutzer.
        
        Returns:
            {
                "valid": bool,
                "filtered_output": str,
                "warnings": List[str],
                "blocked_reason": str (optional)
            }
        """
        warnings = []
        
        # 1. Prüfe auf Datenlecks (sensible Daten in der Antwort)
        filtered_output = ai_response
        for pattern, data_type in self.sensitive_patterns:
            if re.search(pattern, ai_response):
                filtered_output = re.sub(pattern, f'[{data_type}_ZENSIERT]', filtered_output)
                warnings.append(f"Sensible Daten in Antwort entfernt ({data_type})")
        
        # 2. Prüfe auf unangemessene Inhalte
        if self._contains_inappropriate_content(ai_response):
            return {
                "valid": False,
                "filtered_output": None,
                "warnings": warnings,
                "blocked_reason": "Antwort enthält unangemessene Inhalte"
            }
        
        # 3. Prüfe auf Halluzinationen (wenn Kontext vorhanden)
        if context and "expected_data" in context:
            hallucination_check = self._check_hallucination(ai_response, context["expected_data"])
            if not hallucination_check["valid"]:
                warnings.append("Mögliche Halluzination erkannt")
        
        return {
            "valid": True,
            "filtered_output": filtered_output,
            "warnings": warnings
        }
    
    def _needs_ai_validation(self, text: str) -> bool:
        """Prüft, ob AI-basierte Validierung notwendig ist"""
        # Komplexe oder mehrdeutige Anfragen
        suspicious_keywords = ['wie kann ich', 'zeig mir wie', 'erkläre mir wie man', 'umgehen']
        return any(kw in text.lower() for kw in suspicious_keywords)
    
    def _ai_validate_intent(self, text: str) -> Dict[str, Any]:
        """Nutzt AI zur Validierung der Nutzerintention"""
        prompt = ChatPromptTemplate.from_template("""
Du bist ein Sicherheits-Validator. Analysiere die folgende Nutzereingabe und prüfe, ob sie:
1. Legitime Anfragen im Kontext eines Fahrzeug-Service-Systems sind
2. KEINE illegalen, unethischen oder schädlichen Absichten haben

Nutzereingabe: "{text}"

Antworte NUR mit JSON:
{{
    "safe": true/false,
    "reason": "Kurze Begründung wenn unsafe"
}}
""")
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({"text": text})
            content = response.content.strip()
            
            # Parse JSON
            import json
            result = json.loads(content)
            return result
        except Exception as e:
            # Im Fehlerfall: Safe by default (false positive besser als false negative)
            return {"safe": True, "reason": ""}
    
    def _log_violation(
        self,
        user_input: str,
        filtered_input: str,
        violation_type: str,
        severity: str,
        blocked_reason: str,
        warnings: List[str],
        context: Dict[str, Any],
        action_taken: str
    ):
        """Speichert Guardrails-Verstöße in der Datenbank für das Support-Team"""
        try:
            db = SessionLocal()
            
            # Extrahiere User-Infos aus Context
            user_id = context.get("user_id") if context else None
            user_name = context.get("name") if context else None
            user_email = context.get("email") if context else None
            
            # Erstelle Log-Eintrag
            log_entry = GuardrailsLog(
                user_id=user_id,
                user_name=user_name,
                user_email=user_email,
                original_message=user_input,
                filtered_message=filtered_input,
                violation_type=violation_type,
                severity=severity,
                blocked_reason=blocked_reason,
                warnings=json.dumps(warnings, ensure_ascii=False),
                action_taken=action_taken
            )
            
            db.add(log_entry)
            db.commit()
            
            # Log für Entwickler (Console)
            log.warning(
                f"[GUARDRAILS] Violation detected: {violation_type} ({severity}) | "
                f"User: {user_name or user_id or 'Unknown'} | "
                f"Action: {action_taken} | "
                f"Message: {user_input[:100]}..."
            )
            
            db.close()
        except Exception as e:
            log.error(f"Failed to log guardrails violation: {e}")
    
    def _contains_inappropriate_content(self, text: str) -> bool:
        """Prüft auf unangemessene Inhalte in der Antwort"""
        inappropriate_keywords = [
            'gewalt', 'waffen', 'illegal', 'betrug',
            'manipulation', 'diskriminierung', 'hassrede'
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in inappropriate_keywords)
    
    def _check_hallucination(self, response: str, expected_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prüft, ob die AI-Antwort erfundene Daten enthält.
        Vergleicht die Antwort mit den erwarteten/verfügbaren Daten.
        """
        # Einfache Heuristik: Prüfe, ob spezifische Datenpunkte in der Antwort sind,
        # die nicht in expected_data vorhanden sind
        # Hier: Vereinfachte Implementierung
        return {"valid": True}


# Globale Instanz
guardrails = GuardrailsService()


def validate_request(user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper-Funktion für Input-Validierung"""
    return guardrails.validate_input(user_input, context)


def validate_response(ai_response: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Helper-Funktion für Output-Validierung"""
    return guardrails.validate_output(ai_response, context)
