import base64
from datetime import datetime
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup


def _header(message: dict, name: str) -> str:
    for h in message["payload"].get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def _decode_part(data: str) -> str:
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")


def _walk_parts(payload: dict) -> list[dict]:
    parts = [payload]
    stack = list(payload.get("parts", []))
    while stack:
        part = stack.pop()
        parts.append(part)
        stack.extend(part.get("parts", []))
    return parts


def _extract_body(payload: dict) -> str:
    plain_text = None
    html_text = None
    for part in _walk_parts(payload):
        body = part.get("body", {})
        data = body.get("data")
        if not data:
            continue
        mime_type = part.get("mimeType", "")
        if mime_type == "text/plain" and plain_text is None:
            plain_text = _decode_part(data)
        elif mime_type == "text/html" and html_text is None:
            html_text = _decode_part(data)

    if plain_text:
        return plain_text.strip()
    if html_text:
        return BeautifulSoup(html_text, "html.parser").get_text(separator="\n").strip()
    return ""


def extract_article(message: dict) -> dict:
    date_header = _header(message, "Date")
    try:
        received_at = parsedate_to_datetime(date_header) if date_header else None
    except (TypeError, ValueError):
        received_at = None

    return {
        "gmail_message_id": message["id"],
        "sender": _header(message, "From"),
        "subject": _header(message, "Subject") or "(no subject)",
        "received_at": received_at,
        "raw_text": _extract_body(message["payload"]),
    }
