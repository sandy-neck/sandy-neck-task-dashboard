# Events log

Anything unusual that happened on a given day and might explain the numbers. Classes, markets,
a vendor pop-up, a holiday, a road closure, a power cut, a viral post, a nor'easter.

**Why this file exists:** the agent can see weather and it can see sales, but it cannot see that
Allie ran a pilates class at 8am. Without that, a strong morning looks like noise — or worse, gets
attributed to something that didn't cause it. One line here is the difference between a real
explanation and a confident wrong one.

The agent reads this every run, calls out outlier days in the journal entry, and over time can
start telling you whether a given kind of event actually moves anything.

## Format

One line per event. Date first, then time if it matters, then what happened. Everything else is
optional — a half-remembered note beats no note.

```
- 2026-08-08 08:00 — Allie led a pilates class in the sand area. ~15 people.
- 2026-08-15 — Labor Day weekend traffic starts; town parking lot repaving all week.
- 2026-09-02 — TikTok video on the salty gem rings took off overnight.
```

Add anything you'd want to remember when looking back at a strange-looking day. Bad days matter as
much as good ones: a washout, a staffing gap, or a closed road explains a dip that would otherwise
sit in the data looking like a trend.

---

## Log

- 2026-08-08 08:00 — Allie led a pilates class in the sand area. Direct sales from the class itself
  were small, but Sandy's read was that it set the tone for the day. Store went on to a very strong
  Saturday. See `LEARNED.md` for the hourly comparison — the 8–10am window ran roughly double the
  previous Saturday's orders.
