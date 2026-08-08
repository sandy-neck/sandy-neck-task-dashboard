"""
Second brain I/O — the agent's memory between runs.

Reading order matters. CONTEXT.md is curated by Sandy and is authoritative; LEARNED.md is the
agent's own accumulated guesswork and is not. The agent may append to LEARNED.md and write daily
logs, but never rewrites CONTEXT.md unattended — a bad inference shouldn't be able to corrupt the
file everything else is judged against.
"""
import re
from datetime import date, timedelta
from pathlib import Path

BRAIN_DIR = Path(__file__).resolve().parent.parent / "brain"

# Keeps a runaway file from crowding the model's context window.
MAX_CHARS = 14_000


def _read(path: Path, limit: int = MAX_CHARS) -> str:
    try:
        text = path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        return ""
    if len(text) > limit:
        return text[:limit] + "\n\n[...truncated...]"
    return text


class Brain:
    def __init__(self, base: Path = BRAIN_DIR):
        self.base = Path(base)
        self.daily_dir = self.base / "daily"

    # ── Reading ───────────────────────────────────────────────────────────────

    def context(self) -> str:
        return _read(self.base / "CONTEXT.md")

    def learned(self) -> str:
        return _read(self.base / "LEARNED.md", limit=8_000)

    def inbox(self) -> str:
        """Only the Unprocessed section — Processed items have already been folded in."""
        raw = _read(self.base / "INBOX.md")
        if not raw:
            return ""
        match = re.search(
            r"^##\s+Unprocessed\s*$(.*?)(?=^##\s+|\Z)", raw, re.MULTILINE | re.DOTALL
        )
        body = (match.group(1) if match else raw).strip()
        # Strip HTML comments so template hints don't read as real notes.
        body = re.sub(r"<!--.*?-->", "", body, flags=re.DOTALL)
        # Drop horizontal rules — they'd otherwise parse as bullet points and get "processed".
        body = "\n".join(l for l in body.splitlines() if l.strip() not in ("---", "***", "___"))
        return body.strip()

    def recent_logs(self, days: int = 5, before: date | None = None) -> list[tuple[str, str]]:
        """Most recent daily logs, newest first, as (date_string, content)."""
        if not self.daily_dir.is_dir():
            return []
        cutoff = (before or date.today()).isoformat()
        entries = sorted(
            (p for p in self.daily_dir.glob("*.md") if p.stem < cutoff),
            key=lambda p: p.stem,
            reverse=True,
        )
        return [(p.stem, _read(p, limit=4_000)) for p in entries[:days]]

    def open_threads(self, days: int = 7) -> list[str]:
        """
        Questions raised in recent logs that were never resolved, so a thread opened on Tuesday
        gets revisited instead of quietly dropped.
        """
        threads = []
        for day, content in self.recent_logs(days=days):
            match = re.search(
                r"^##\s+Open threads\s*$(.*?)(?=^##\s+|\Z)", content, re.MULTILINE | re.DOTALL
            )
            if not match:
                continue
            for line in match.group(1).splitlines():
                line = line.strip()
                if line.startswith(("-", "*")) and len(line) > 3:
                    threads.append(f"({day}) {line.lstrip('-* ').strip()}")
        return threads[:12]

    # ── Writing ───────────────────────────────────────────────────────────────

    def write_daily_log(self, day: str, content: str) -> Path:
        self.daily_dir.mkdir(parents=True, exist_ok=True)
        path = self.daily_dir / f"{day}.md"
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        return path

    def append_learned(self, entry: str) -> None:
        """Append a dated observation. No-op on empty input."""
        entry = (entry or "").strip()
        if not entry:
            return
        path = self.base / "LEARNED.md"
        existing = ""
        try:
            existing = path.read_text(encoding="utf-8").rstrip()
        except (FileNotFoundError, OSError):
            existing = "# Learned\n"
        path.write_text(f"{existing}\n\n---\n\n{entry}\n", encoding="utf-8")

    def mark_inbox_processed(self, note_lines: list[str], day: str) -> None:
        """
        Move handled notes from Unprocessed to Processed, stamped with where they landed.
        Left untouched if anything looks off — losing a note is worse than processing it twice.
        """
        if not note_lines:
            return
        path = self.base / "INBOX.md"
        try:
            raw = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return

        moved = []
        for note in note_lines:
            note = note.strip()
            if note and note in raw:
                raw = raw.replace(note + "\n", "", 1)
                moved.append(f"{note}  _(processed {day})_")
        if not moved:
            return

        marker = "## Processed"
        if marker not in raw:
            raw = raw.rstrip() + f"\n\n{marker}\n"
        raw = raw.replace(marker, marker + "\n\n" + "\n".join(moved), 1)
        path.write_text(raw, encoding="utf-8")
