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
from models.customer import Customer

log = logging.getLogger(__name__)

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
IMAP_USER = os.environ.get("SMTP_USER")
IMAP_PASS = os.environ.get("SMTP_PASS")

_last_imap_auth_failure_ts: float = 0.0
_imap_auth_backoff_seconds: float = 60.0
_logged_missing_imap_creds: bool = False

def get_user_id_by_customer_ref(db, ref_id: str):
    if len(ref_id) > 30 and ref_id in global_store:
        return ref_id

    if ref_id.isdigit():
        try:
            c_id = int(ref_id)
            customer = db.query(Customer).filter(Customer.id == c_id).first()
            if customer and customer.user_id:
                return str(customer.user_id)
        except Exception:
            pass
            
    return None

def check_inbox_for_replies():
    db = SessionLocal() 
    try:
        global _last_imap_auth_failure_ts, _imap_auth_backoff_seconds, _logged_missing_imap_creds

        if not IMAP_USER or not IMAP_PASS:
            if not _logged_missing_imap_creds:
                log.warning("IMAP check skipped: missing SMTP_USER/SMTP_PASS.")
                _logged_missing_imap_creds = True
            return

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
                return
            raise
        
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')

        if not messages or messages[0] == b'':
            return

        email_ids = messages[0].split()

        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, "(BODY.PEEK[])")
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])

                    subject_header = msg["Subject"] or ""
                    decoded_list = decode_header(subject_header)
                    subject_parts = []
                    for content, encoding in decoded_list:
                        if isinstance(content, bytes):
                            subject_parts.append(content.decode(encoding or "utf-8", errors="ignore"))
                        else:
                            subject_parts.append(str(content))
                    subject = "".join(subject_parts)
                    
                    sender = msg.get("From", "Unbekannt")

                    match = re.search(r"Ref(?:-ID)?:\s*(.*?)]", subject, re.IGNORECASE)
                    
                    if match:
                        external_ref = match.group(1).strip()
                        internal_user_id = get_user_id_by_customer_ref(db, external_ref)
                        
                        if internal_user_id:
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

                            if internal_user_id in global_store:
                                try:
                                    sys_msg = SystemMessage(content=f"UPDATE: Neue E-Mail Antwort.\nBetreff: {subject}\nInhalt:\n{clean_body}")
                                    global_store[internal_user_id].add_message(sys_msg)
                                except Exception:
                                    pass

                            try:
                                new_notif = Notification(
                                    user_id=internal_user_id, 
                                    title=f"Antwort von {sender}",
                                    message=subject[:100],
                                    type="EMAIL_REPLY",
                                    data={
                                        "sender": sender,
                                        "subject": subject,
                                        "body": clean_body,
                                        "ref_used": external_ref
                                    },
                                    is_read=False
                                )
                                db.add(new_notif)
                                db.commit()
                                
                                log.info(f"Notification gespeichert: {internal_user_id} (Ref: {external_ref})")

                                mail.store(e_id, '+FLAGS', '\\Seen')

                            except Exception as e:
                                log.error(f"Fehler DB/Store: {e}")
                                db.rollback()
            
        mail.close()
        mail.logout()
        
    except Exception as e:
        log.error(f"IMAP Error: {e}")
    finally:
        db.close()