import imaplib
import email
from email.header import decode_header
import re
import os
import logging
import time
from langchain_core.messages import SystemMessage
from agents.memory import global_store
from database import SessionLocal
from models.notifications import Notification

log = logging.getLogger(__name__)

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
IMAP_USER = os.environ.get("SMTP_USER")
IMAP_PASS = os.environ.get("SMTP_PASS")

_last_imap_auth_failure_ts: float = 0.0
_imap_auth_backoff_seconds: float = 60.0
_logged_missing_imap_creds: bool = False

def check_inbox_for_replies():
    db = SessionLocal() 
    try:
        global _last_imap_auth_failure_ts, _imap_auth_backoff_seconds, _logged_missing_imap_creds

        # If credentials are not configured, skip quietly after one log.
        if not IMAP_USER or not IMAP_PASS:
            if not _logged_missing_imap_creds:
                log.warning("IMAP check skipped: missing SMTP_USER/SMTP_PASS (used for IMAP login).")
                _logged_missing_imap_creds = True
            return

        # Backoff after authentication failures to avoid spamming logs every 60 seconds.
        now = time.time()
        if _last_imap_auth_failure_ts and (now - _last_imap_auth_failure_ts) < _imap_auth_backoff_seconds:
            return

        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        try:
            mail.login(IMAP_USER, IMAP_PASS)
        except imaplib.IMAP4.error as e:
            msg = str(e)
            if "AUTHENTICATIONFAILED" in msg.upper():
                _last_imap_auth_failure_ts = now
                _imap_auth_backoff_seconds = min(_imap_auth_backoff_seconds * 2, 3600.0)
                log.error(
                    "IMAP authentication failed; backing off for %.0fs (max 3600s).",
                    _imap_auth_backoff_seconds,
                )
                return
            raise
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')

        if not messages or messages[0] == b'':
            return

        email_ids = messages[0].split()

        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    
                    sender = msg.get("From", "Unbekannt")

                    match = re.search(r"Ref(?:-ID)?:\s*(.*?)]", subject)
                    
                    if match:
                        session_id = match.group(1).strip()

                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    payload = part.get_payload(decode=True)
                                    if payload:
                                        body = payload.decode(errors="ignore")
                                    break
                        else:
                            payload = msg.get_payload(decode=True)
                            if payload:
                                body = payload.decode(errors="ignore")

                        clean_body = body.strip()[:1500]

                        if session_id in global_store:
                            try:
                                sys_msg = SystemMessage(content=f"UPDATE: Neue E-Mail Antwort eingegangen.\nBetreff: {subject}\nInhalt:\n{clean_body}")
                                global_store[session_id].add_message(sys_msg)
                                log.info(f"Email zu global_store hinzugefügt: {session_id}")
                            except Exception as e:
                                log.error(f"Fehler beim Update global_store: {e}")

                        try:
                            new_notif = Notification(
                                user_id=session_id, 
                                title=f"Antwort von {sender}",
                                message=subject[:100],
                                type="EMAIL_REPLY",
                                data={
                                    "sender": sender,
                                    "subject": subject,
                                    "body": clean_body
                                },
                                is_read=False
                            )
                            db.add(new_notif)
                            db.commit()
                            log.info(f"Notification in DB gespeichert für User/Session: {session_id}")
                        except Exception as e:
                            log.error(f"Fehler beim Speichern der Notification in DB: {e}")
                            db.rollback()
            
        mail.close()
        mail.logout()
        
    except Exception as e:
        log.error(f"IMAP Error: {e}")
    finally:
        db.close()