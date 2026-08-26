"""
Second brain I/O — the agent's memory between runs.

Reading order matters. CONTEXT.md is curated by BJ and is authoritative; LEARNED.md is the
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

# CONTEXT.md is the authoritative file and gets a much larger budget. It grew past the old 14k
# ceiling unnoticed, which silently cut the Standing Instructions off the bottom — the agent was
# running for days without ever seeing its own operating rules.
CONTEXT_MAX_CHARS = 60_000


def _read(path: Path, limit: int = MAX_CHARS) -> str:
    """
    Read a brain file, truncating from the MIDDLE if it's too long.

    Head-only truncation is the wrong shape for these documents: the most operationally important
    content — standing instructions, next actions, recent log entries — sits at the BOTTOM. Cutting
    the tail silently discards exactly what matters most, and does it without any visible symptom.
    """
    try:
        text = path.read_text(encoding="utf-8").strip()
    except (FileNotFoundError, OSError):
        return ""
    if len(text) <= limit:
        return text

    # Keep twice as much head as tail — narrative sets up the file, but the tail must survive.
    head = int(limit * 0.65)
    tail = limit - head
    return (
        text[:head]
        + f"\n\n[...{len(text) - limit:,} characters omitted from the middle of this file...]\n\n"
        + text[-tail:]
    )


class Brain:
    def __init__(self, base: Path = BRAIN_DIR):
        self.base = Path(base)
        self.daily_dir = self.base / "daily"

    # ── Reading ───────────────────────────────────────────────────────────────

    def context(self) -> str:
        return _read(self.base / "CONTEXT.md", limit=CONTEXT_MAX_CHARS)

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

    def events(self, around: str = None, window: int = 21) -> str:
        """
        Recent entries from the events log.

        The agent can see weather and sales but not that someone ran a class on the sand at 8am.
        Without that line, an unusual morning either reads as noise or gets pinned on the wrong
        cause — so these are pulled in before anything gets explained.
        """
        raw = _read(self.base / "events.md", limit=6_000)
        if not raw:
            return ""
        match = re.search(r"^##\s+Log\s*$(.*)", raw, re.MULTILINE | re.DOTALL)
        body = (match.group(1) if match else raw).strip()

        if not around:
            return body
        try:
            cutoff = (date.fromisoformat(around) - timedelta(days=window)).isoformat()
        except ValueError:
            return body
        # Keep undated lines: continuation text belongs with the entry above it.
        kept, keeping = [], False
        for line in body.splitlines():
            stamp = re.match(r"^\s*[-*]\s*(\d{4}-\d{2}-\d{2})", line)
            if stamp:
                keeping = stamp.group(1) >= cutoff
            if keeping:
                kept.append(line)
        return "\n".join(kept).strip()

    def open_projects(self) -> list[dict]:
        """
        Projects still in flight. These are the loops that fall through the cracks when they live
        in someone's head — the agent surfaces one when the data gives it a reason to.
        """
        projects_dir = self.base / "projects"
        if not projects_dir.is_dir():
            return []

        found = []
        for path in sorted(projects_dir.glob("*.md")):
            if path.stem.lower() == "readme":
                continue
            content = _read(path, limit=5_000)
            if not content:
                continue
            status = "Unknown"
            if match := re.search(r"^\*\*Status:\*\*\s*(.+)$", content, re.MULTILINE):
                status = match.group(1).strip()
            if status.lower().startswith("done"):
                continue
            next_action = ""
            if match := re.search(
                r"^##\s+Next action\s*$(.*?)(?=^##\s+|\Z)", content, re.MULTILINE | re.DOTALL
            ):
                next_action = re.sub(r"<!--.*?-->", "", match.group(1), flags=re.DOTALL).strip()
            found.append({
                "name": path.stem,
                "status": status,
                "next_action": next_action,
                "content": content,
            })
        return found

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

    def append_inbox(self, entries: list[str]) -> None:
        """
        Add new dated notes to Unprocessed -- the same section inbox() reads and
        mark_inbox_processed() clears once a run has folded them in. Written for reply_ingest.py
        (email replies to the daily report land here), but usable by anything that wants to feed
        INBOX.md a note programmatically rather than BJ typing it in by hand.

        Mirrors mark_inbox_processed()'s own section-matching regex on purpose -- same shape of
        edit, same file, so both stay easy to reason about together.
        """
        entries = [e.strip() for e in entries if e and e.strip()]
        if not entries:
            return

        path = self.base / "INBOX.md"
        try:
            raw = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            raw = "# Inbox\n\n---\n\n## Unprocessed\n\n---\n\n## Processed\n"

        addition = "\n".join(entries)
        section = re.search(
            r"(^##\s+Unprocessed\s*$)(.*?)(?=^##\s+|\Z)", raw, re.MULTILINE | re.DOTALL
        )
        if section:
            # group(1)'s trailing `\s*$` greedily swallows the heading's own newline, so rstrip it
            # back to the bare heading and rebuild spacing explicitly rather than doubling it up.
            heading = section.group(1).rstrip()
            existing = "\n".join(
                line for line in section.group(2).splitlines()
                if line.strip() not in ("---", "***", "___")
            ).strip()
            body = f"{existing}\n\n{addition}" if existing else addition
            raw = (
                raw[:section.start(1)] + heading + "\n\n" + body + "\n\n"
                + raw[section.end(2):]
            )
        else:
            raw = raw.rstrip() + "\n\n## Unprocessed\n\n" + addition + "\n"
        path.write_text(raw, encoding="utf-8")

    def mark_inbox_processed(self, day: str) -> None:
        """
        Move everything in Unprocessed to Processed, stamped with the date it was read.

        Works on whole entries, not lines. Notes wrap across several lines, and moving only the
        bullet leaves its continuation stranded under the wrong heading — which shreds the note into
        fragments that read like separate half-thoughts.

        Left untouched if the file isn't in the expected shape; processing twice is recoverable,
        mangling someone's notes is not.
        """
        path = self.base / "INBOX.md"
        try:
            raw = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return

        section = re.search(
            r"(^##\s+Unprocessed\s*$)(.*?)(?=^##\s+|\Z)", raw, re.MULTILINE | re.DOTALL
        )
        if not section:
            return

        body = section.group(2)
        entries, current = [], []
        for line in body.splitlines():
            if re.match(r"^\s*[-*]\s+\S", line):       # new bullet starts a new entry
                if current:
                    entries.append("\n".join(current))
                current = [line.rstrip()]
            elif current and line.strip() and not line.startswith("#"):
                current.append(line.rstrip())          # continuation of the current entry
            elif current and not line.strip():
                entries.append("\n".join(current))
                current = []
        if current:
            entries.append("\n".join(current))

        entries = [e for e in entries if e.strip() and e.strip() not in ("---", "***", "___")]
        if not entries:
            return

        stamped = [f"{e}\n  _(processed {day})_" for e in entries]
        raw = raw[:section.start(2)] + "\n\n" + raw[section.end(2):]

        marker = "## Processed"
        if marker not in raw:
            raw = raw.rstrip() + f"\n\n{marker}\n"
        raw = raw.replace(marker, marker + "\n\n" + "\n".join(stamped), 1)
        path.write_text(raw, encoding="utf-8")
