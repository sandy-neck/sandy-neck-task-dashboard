# The Second Brain

A running memory for the store. The point is that the daily email stops being a series of
disconnected one-off observations and starts accumulating into something that understands the
business roughly as well as Sandy does.

## The four files

| File | Owned by | What it's for |
|---|---|---|
| `CONTEXT.md` | **You** | Curated truth. The agent reads this first and treats it as authoritative. |
| `INBOX.md` | **You** | Scratch pad. Drop a thought any time; the agent picks it up on the next run. |
| `LEARNED.md` | **The agent** | Append-only observations the agent accumulates on its own. |
| `daily/YYYY-MM-DD.md` | The agent | One entry per day: what happened, what it concluded, what it wasn't sure about. |

The split matters. The agent never rewrites `CONTEXT.md` unattended — a bad inference shouldn't be
able to quietly corrupt the file everything else is judged against. It appends to `LEARNED.md`
instead, and you promote anything worth keeping.

## The loop

```
   You add a note ─────────► INBOX.md
                                │
                                ▼
   Agent runs (7 AM) ──► reads CONTEXT + INBOX + LEARNED + recent daily logs
                                │
                    ┌───────────┼────────────┐
                    ▼           ▼            ▼
              daily log     the email    LEARNED.md
                                              │
                          you promote what's real
                                              ▼
                                        CONTEXT.md
```

## How to give feedback

Three ways, in increasing order of effort:

**1. Jot it in `INBOX.md`.** One line is fine. The next run reads it and folds it into the analysis.

```markdown
- 2026-08-08 — Customer said she found us googling "swim suits near me". Ask more people this.
- 2026-08-08 — Yesterday's "strong day" call was wrong. Hot beach day, should've done better.
```

**2. Correct `CONTEXT.md` directly.** If the agent keeps making the same wrong assumption, this is
where you fix it permanently.

**3. Tell Claude in a session.** Say what was wrong and it'll write the correction into the right
file. Usually the fastest option.

## What makes a daily entry good

Each entry records the reasoning, not just the numbers — so that a month from now it's possible to
see *why* a call was made and whether it held up.

- What the conditions were (weather, tide, day of week, season position)
- What actually moved, by channel
- What the agent concluded, and with what confidence
- What it flagged as uncertain
- Anything from `INBOX.md` that changed the read

Entries also carry forward open threads, so a question raised on Tuesday gets revisited rather than
forgotten.

## Why it's in git

Every change is diffable and revertable. If the agent writes something wrong into `LEARNED.md`, or
a context edit turns out to be a mistake, the history is right there.
