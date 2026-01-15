import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_TO = os.environ.get("SMTP_TO") # Test-Adresse

def send_email_via_smtp(to_email: str, subject: str, body: str) -> str:
    """ Zentrale Funktion zum Versenden von E-Mails. """
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        return "Fehler: SMTP Konfiguration fehlt in .env"

    try:
        msg = EmailMessage()
        msg["From"] = SMTP_USER
        msg["To"] = SMTP_TO  # An Test-Adresse senden
        msg["Subject"] = subject
        msg.set_content(body)

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            
        return f"E-Mail erfolgreich versendet an {SMTP_TO})."

    except Exception as e:
        log.error(f"SMTP Fehler: {e}")
        return f"Fehler beim E-Mail-Versand: {str(e)}"