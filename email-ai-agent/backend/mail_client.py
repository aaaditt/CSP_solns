"""
IMAP layer for email-ai-agent.

Deliberately has no imports from db.py or main.py/FastAPI - this file is the
only place that knows how to talk to the mailbox, so a later swap to the
Gmail API or Microsoft Graph only touches this module.
"""

import imaplib
import email
import email.message
import re
from email.header import decode_header
from email.utils import parsedate_to_datetime, parseaddr
from typing import cast

import config

BODY_SNIPPET_MAX_CHARS = 500


def _connect() -> imaplib.IMAP4_SSL:
    imap = imaplib.IMAP4_SSL(config.IMAP_HOST)
    imap.login(config.EMAIL_ADDRESS, config.EMAIL_APP_PASSWORD)
    imap.select("INBOX")
    return imap


def _decode(raw_header) -> str:
    if not raw_header:
        return ""
    parts = decode_header(raw_header)
    decoded = ""
    for text, charset in parts:
        if isinstance(text, bytes):
            decoded += text.decode(charset or "utf-8", errors="replace")
        else:
            decoded += text
    return decoded


def _strip_html(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_body(msg: email.message.Message) -> str:
    """Prefers the first text/plain part; falls back to stripped text/html."""
    plain: bytes | None = None
    html: bytes | None = None
    plain_charset = html_charset = "utf-8"

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition") or "")
            if "attachment" in disposition:
                continue
            if content_type == "text/plain" and plain is None:
                plain = cast(bytes, part.get_payload(decode=True))
                plain_charset = part.get_content_charset() or "utf-8"
            elif content_type == "text/html" and html is None:
                html = cast(bytes, part.get_payload(decode=True))
                html_charset = part.get_content_charset() or "utf-8"
    else:
        content_type = msg.get_content_type()
        payload = cast(bytes, msg.get_payload(decode=True))
        if content_type == "text/html":
            html = payload
            html_charset = msg.get_content_charset() or "utf-8"
        else:
            plain = payload
            plain_charset = msg.get_content_charset() or "utf-8"

    if plain is not None:
        return plain.decode(plain_charset, errors="replace").strip()

    if html is not None:
        return _strip_html(html.decode(html_charset, errors="replace"))

    return ""


def _parse_message(uid: str, raw: bytes) -> dict:
    msg = email.message_from_bytes(raw)

    sender_name, sender_email = parseaddr(_decode(msg.get("From")))
    subject = _decode(msg.get("Subject"))

    date_header = msg.get("Date")
    try:
        date = parsedate_to_datetime(date_header) if date_header else None
    except (TypeError, ValueError):
        date = None

    return {
        "imap_uid": uid,
        "sender": sender_name or sender_email,
        "sender_email": sender_email,
        "subject": subject,
        "date": date,
        "body_snippet": _extract_body(msg)[:BODY_SNIPPET_MAX_CHARS],
    }


def fetch_recent(n: int) -> list[dict]:
    """Returns up to n most-recently-arrived INBOX messages, newest first."""
    imap = _connect()
    try:
        typ, data = imap.uid("search", None, "ALL")
        if typ != "OK":
            raise RuntimeError(f"IMAP UID SEARCH failed: {typ}")

        uids = data[0].split()
        recent_uids = uids[-n:] if n < len(uids) else uids
        recent_uids.reverse()  # newest first

        results = []
        for uid in recent_uids:
            typ, msg_data = imap.uid("fetch", uid, "(RFC822)")
            if typ != "OK" or not msg_data or msg_data[0] is None:
                continue
            raw = msg_data[0][1]
            results.append(_parse_message(uid.decode(), raw))
        return results
    finally:
        imap.logout()


def fetch_full_body(uid: str) -> str:
    """Live IMAP fetch of the full plain-text body for one uid (not persisted)."""
    imap = _connect()
    try:
        typ, msg_data = imap.uid("fetch", uid, "(RFC822)")
        if typ != "OK" or not msg_data or msg_data[0] is None:
            raise ValueError(f"Email with uid {uid} not found (deleted or moved)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        return _extract_body(msg)
    finally:
        imap.logout()


if __name__ == "__main__":
    emails = fetch_recent(20)
    for e in emails:
        print(f"{e['date']}  |  {e['sender']} <{e['sender_email']}>  |  {e['subject']}")
