# Projects / Open Loops

One file per open loop. Things that are started, half-built, or decided-but-not-done — the stuff
that quietly falls off when it lives in your head or in a chat thread somewhere.

The daily agent reads every project with a status other than `Done` and will surface one when the
data gives it a reason to. Not every day, and not all of them at once — a nag every morning gets
ignored, which defeats the point. A project comes up when something in the numbers makes it
relevant, or when it's been sitting long enough to be worth a nudge.

## Format

Keep it loose. The parts that matter:

```markdown
# Project name

**Status:** Not started | In progress | Blocked | Done
**Owner:** who
**Opened:** YYYY-MM-DD

## What this is
## Why it matters
## Next action        ← the single most important line
## Log                ← dated entries, newest at the bottom
```

`Next action` should be concrete enough to do without re-thinking it. "Decide on Q4 buy" is not a
next action; "pull last October's top 20 and mark which have >30 day lead times" is.

## Status meanings

| Status | Means |
|---|---|
| `Not started` | Agreed it matters, nothing done |
| `In progress` | Actively moving |
| `Blocked` | Waiting on something external — say what in the log |
| `Done` | Finished. Leave the file; the history is worth keeping |

## Why not a task app

Because the analysis and the follow-through belong in the same place. When the agent notices the
tire deflators are 15 days from empty, it should be able to see there's an open reorder-process
project and connect the two. A separate to-do list can't do that.
