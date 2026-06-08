"""
Brevo SMTP mailer — delivers the lead magnet to the user and notifies the owner.

Reuses the SMTP_* env vars already set on the Railway service (Brevo relay).
Pure stdlib (smtplib/email) — no extra dependency. Never raises to the caller
in a way that breaks the request; callers run it in a background task.
"""
import os
import smtplib
import ssl
from email.message import EmailMessage

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp-relay.brevo.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
SMTP_FROM = os.environ.get("SMTP_FROM", "noreply@adviseo.se")
FROM_NAME = os.environ.get("MAIL_FROM_NAME", "Vindkollen")
OWNER_EMAIL = os.environ.get("LEAD_NOTIFY_EMAIL", "simon@adviseo.se")


def configured() -> bool:
    return bool(SMTP_USER and SMTP_PASS)


def send_email(to, subject, html, text=None, attachments=None, reply_to=None, from_name=None):
    """Send one email. attachments = list of (filename, bytes, "mime/type").

    Returns (ok: bool, info: str). Logs to stdout; never raises.
    """
    if not configured():
        print("[mailer] NOT SENT — SMTP_USER/SMTP_PASS missing in env")
        return False, "smtp_not_configured"
    try:
        msg = EmailMessage()
        msg["From"] = f"{from_name or FROM_NAME} <{SMTP_FROM}>"
        msg["To"] = to
        msg["Subject"] = subject
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(text or "Den här e-posten visas bäst i en klient som stödjer HTML.")
        msg.add_alternative(html, subtype="html")
        for (fn, data, mime) in (attachments or []):
            maintype, _, subtype = mime.partition("/")
            msg.add_attachment(data, maintype=maintype, subtype=subtype or "octet-stream", filename=fn)
        ctx = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
            s.starttls(context=ctx)
            s.login(SMTP_USER, SMTP_PASS)
            s.send_message(msg)
        print(f"[mailer] sent '{subject}' -> {to}")
        return True, "sent"
    except Exception as exc:  # noqa: BLE001
        print(f"[mailer] SEND FAILED -> {to}: {exc}")
        return False, str(exc)


def notify_owner(subject, html, reply_to=None):
    """Notify the site owner (simon@adviseo.se) about a new lead."""
    return send_email(OWNER_EMAIL, subject, html, reply_to=reply_to)
