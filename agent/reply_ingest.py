"""
Pulls BJ's replies to the daily email into brain/INBOX.md -- the same Unprocessed section he'd
write into by hand, just filled by a lower-friction front door: hit reply, write a sentence, done.
Everything downstream (Brain.inbox(), the prompt, mark_inbox_processed()) is unchanged.

Reuses the same Gmail account and credentials the report is sent from (SMTP_USERNAME/PASSWORD, a
Gmail App Password) over IMAP rather than SMTP -- an App Password grants full mail-protocol access
once generated, so no new secret should be needed. IMAP access does have to be turned on once in
that Gmail account's own settings (Settings -> See all settings -> Forwarding and POP/IMAP ->
Enable IMAP) -- a one-time manual step nothing here can do for you. IMAP_USERNAME/IMAP_PASSWORD
env vars override the SMTP ones if a different mailbox or credential is ever wanted.

State (the last IMAP UID processed) lives in brain/reference/reply-ingest-state.json, same pattern
as everything else under brain/reference/. UIDs, not the \\Seen flag, are what decides what's new --
relying on \\Seen would break the moment a human reads the email in Gmail's own UI before this runs.
"""
import email
import imaplib
import json
import os
import re
from datetime import date
from email.header import decode_header
from pathlib import Path

from brain import Brain

IMAP_HOST = "imap.gmail.com"
STATE_PATH = Path(__file__).resolve().parent.parent / "brain" / "reference" / "reply-ingest-state.json"

# Matches build_subject()'s SUBJECT_PREFIX in email_report.py -- only replies to the daily report
# thread count, not anything else that happens to land in this inbox.
SUBJECT_MARKER = "SNP Daily"

NOISE_FROM_SUBSTRINGS = ("mailer-daemon", "postmaster", "noreply", "no-reply")

# Where a reply's new text ends and the quoted original begins. Covers Gmail web/mobile ("On ...
# wrote:", "> " prefixes) and Outlook-style quoted header blocks -- the common cases, not every
# client. Worst case on an unrecognized client: the quoted original gets ingested along with the
# real reply, which is noisier but not wrong.
_QUOTE_MARKERS = [
    r"^On .+ wrote:\s*$",
    r"^-{2,}\s*Original Message\s*-{2,}\s*$",
    r"^From:\s.+$",
    r"^Sent from my (iPhone|iPad|Android)",
]


def _load_state() -> dict:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {"last_uid": 0}


def _save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _decode(value) -> str:
    if not value:
        return ""
    parts = decode_header(value)
    out = []
    for text, enc in parts:
        if not isinstance(text, bytes):
            out.append(text)
            continue
        try:
            out.append(text.decode(enc or "utf-8", errors="replace"))
        except (LookupError, TypeError):
            # A header can claim a pseudo-charset like "unknown-8bit" that Python's codecs don't
            # recognize -- fall back rather than let one malformed header crash the whole run.
            out.append(text.decode("utf-8", errors="replace"))
    return "".join(out)


def _decode_payload(payload: bytes, charset: str) -> str:
    try:
        return payload.decode(charset or "utf-8", errors="replace")
    except (LookupError, TypeError):
        # Same defensive fallback as _decode() -- an unrecognized declared charset shouldn't
        # crash ingestion; getting the text approximately right beats losing the message.
        return payload.decode("utf-8", errors="replace")


def _plain_text_body(msg: "email.message.Message") -> str:
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and not part.get_filename():
                payload = part.get_payload(decode=True)
                return _decode_payload(payload, part.get_content_charset()) if payload else ""
        for part in msg.walk():
            if part.get_content_type() == "text/html" and not part.get_filename():
                payload = part.get_payload(decode=True)
                html = _decode_payload(payload, part.get_content_charset()) if payload else ""
                return re.sub(r"<[^>]+>", " ", html)
        return ""
    payload = msg.get_payload(decode=True)
    return _decode_payload(payload, msg.get_content_charset()) if payload else ""


def strip_quoted_reply(body: str) -> str:
    """Keep only what was actually typed, dropping the quoted original message beneath it."""
    lines = body.replace("\r\n", "\n").split("\n")
    cut = len(lines)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(">"):
            cut = i
            break
        if any(re.match(pattern, stripped, re.IGNORECASE) for pattern in _QUOTE_MARKERS):
            cut = i
            break
    return "\n".join(lines[:cut]).strip()


def _is_noise(msg: "email.message.Message", from_addr: str) -> bool:
    auto_submitted = msg.get("Auto-Submitted")
    if auto_submitted and auto_submitted.strip().lower() != "no":
        return True
    lowered = (from_addr or "").lower()
    return any(s in lowered for s in NOISE_FROM_SUBSTRINGS)


def ingest_replies(host: str = IMAP_HOST) -> dict:
    """
    Pull any new replies to the daily report since the last run and drop them into
    brain/INBOX.md's Unprocessed section. Call this BEFORE Brain().inbox() is read, so a reply
    that arrived overnight is picked up by the same run that reads the inbox for that day.

    Returns {"available": bool, "ingested": int, "reason": str | None}.
    """
    username = os.environ.get("IMAP_USERNAME") or os.environ.get("SMTP_USERNAME") or ""
    password = os.environ.get("IMAP_PASSWORD") or os.environ.get("SMTP_PASSWORD") or ""
    if not username or not password:
        return {"available": False, "ingested": 0, "reason": "no IMAP/SMTP credentials configured"}

    state = _load_state()
    last_uid = int(state.get("last_uid", 0))

    conn = None
    try:
        conn = imaplib.IMAP4_SSL(host)
        conn.login(username, password)
        conn.select("INBOX", readonly=False)

        # UID SEARCH rather than "UNSEEN" -- \Seen flips the moment a human reads the email in
        # Gmail's own UI, which would silently hide it from this before it's ever ingested.
        typ, data = conn.uid("search", None, f"UID {last_uid + 1}:*")
        if typ != "OK":
            return {"available": False, "ingested": 0, "reason": f"IMAP search failed: {typ}"}

        # Gmail can re-include the boundary UID even when nothing new exists past it.
        uids = sorted(u for u in (int(x) for x in (data[0].split() if data and data[0] else [])) if u > last_uid)

        entries = []
        highest_seen = last_uid
        for uid in uids:
            typ, msg_data = conn.uid("fetch", str(uid), "(RFC822)")
            highest_seen = max(highest_seen, uid)
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = _decode(msg.get("Subject"))
            from_addr = _decode(msg.get("From"))

            if SUBJECT_MARKER.lower() not in subject.lower():
                continue
            if _is_noise(msg, from_addr):
                continue

            body = strip_quoted_reply(_plain_text_body(msg))
            if not body:
                continue

            today = date.today().isoformat()
            # One bullet per reply, shaped exactly like a hand-written INBOX.md note, so it flows
            # through Brain.inbox() / mark_inbox_processed() completely unchanged.
            entries.append(f"- {today} — (email reply from {from_addr}) {body}")

        if entries:
            Brain().append_inbox(entries)

        _save_state({"last_uid": highest_seen})
        return {"available": True, "ingested": len(entries), "reason": None}

    except Exception as e:
        return {"available": False, "ingested": 0, "reason": str(e)}
    finally:
        if conn is not None:
            try:
                conn.logout()
            except Exception:
                pass
