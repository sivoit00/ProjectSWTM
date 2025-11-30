import imaplib
import email
from email.header import decode_header
import re
import os
import logging
from langchain_core.messages import SystemMessage
from agents.memory import global_store

log = logging.getLogger(__name__)

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")
IMAP_USER = os.environ.get("SMTP_USER")
IMAP_PASS = os.environ.get("SMTP_PASS")

def check_inbox_for_replies():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(IMAP_USER, IMAP_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()

        if not email_ids:
            return

        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding or "utf-8")
                    
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

                        if session_id in global_store:
                            clean_body = body.strip()[:1500]
                            sys_msg = SystemMessage(content=f"UPDATE: Neue E-Mail Antwort eingegangen.\nBetreff: {subject}\nInhalt:\n{clean_body}")
                            global_store[session_id].add_message(sys_msg)
            
        mail.close()
        mail.logout()
        
    except Exception as e:
        log.error(f"IMAP Error: {e}")