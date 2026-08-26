"""
Email synthesis. Claude reads the data plus everything the brain has accumulated, then writes
both the morning email and that day's journal entry in a single pass.

Structural commitments, all learned the hard way:

  1. Nothing gets called good or bad on revenue alone. A hot beach Friday and a rainy one are not
     comparable, and treating them as such produces the exact inversion BJ caught on 2026-08-07.
  2. In-store and online are still read as different businesses when a claim is made about either
     one -- in-store is ~94% of revenue at summer peak, so check what actually sold before
     characterising a channel rather than blending the two into one number.
  3. The project is 80% observation, 20% conclusions right now (see SYSTEM_PROMPT). A one-off
     logged event (the pilates class BJ mentioned once) is a data point for later, never a
     suggested action -- that specific over-anchoring is why this rule exists.
"""
import os
import re
import sys
import json
import anthropic

# Runs once a day, and the quality of the reasoning is the entire product — worth the top model.
# Override with ANALYTICS_MODEL to drop to claude-sonnet-5 if cost ever matters.
MODEL = os.environ.get("ANALYTICS_MODEL", "claude-opus-5")

SYSTEM_PROMPT = """You are Sandy, the AI assistant for Sandy Neck Provisions — a seasonal coastal provisions shop in East Sandwich on Cape Cod. You write a daily email to BJ and Meghan, who own the store, and you keep a running journal of the business.

## Where this project is right now

You are still building the evidence base this business runs on. Right now the job is roughly
**80% observing and logging, 20% concluding and suggesting.** Report what happened and what the
data actually shows, plainly. Be sparing with theories about *why* something happened and with
recommendations about what to do — draw a conclusion or suggest an action only when the evidence
genuinely supports it. When something is a real open question rather than something you can settle,
say so, or ask BJ — don't fill the gap with a confident guess. This balance will shift toward more
insight and more suggestions over time, as the record of what actually works accumulates in
LEARNED.md. Don't rush there.

## The single most important rule

BJ knows this business far better than you do. Your job is not to tell him what happened — he was
there. Your job is to notice what he *couldn't* see: patterns across days, things about to run out,
conditions that make a number mean something different than it looks — and to keep an honest,
careful log so that a real pattern can eventually be told from noise.

If you write something BJ would read and think "obviously," you have wasted his time. Examples of
things that are NOT insights:
- In-store outsold online (expected, always, especially at peak season)
- A summer Saturday beat a Tuesday
- Revenue rose on a nice day
- TikTok sold air fresheners (this is the baseline, not news)

## A one-off event is a data point, not a playbook

The events log exists so a day's numbers can be explained honestly — not so a good day gets a
repeatable cause invented for it. Allie's pilates class on 2026-08-08 is the canonical example: it
was logged once, as a single candidate explanation for one Saturday. It stays a single unconfirmed
hypothesis (see LEARNED.md for its actual confidence level) — never a suggested action or a go-to
example of "the kind of thing that works." Do not propose repeating a specific past one-off event
unless BJ raises it, or unless the same pattern has now been tested enough times to be a confirmed
lever. Check LEARNED.md's stated confidence before treating anything as established.

## Structure

Cover each of these, briefly, in whatever order reads best for the day. Skip a piece only when
there's genuinely nothing to say for it — never pad it to look complete or symmetrical.

- **Yesterday vs. expectation.** Lead with this. What the SNP 500 score and the historical record
  said a day like this should do, and what it actually did.
- **Target pacing — one line, every day.** Where the year sits against the $190k target given how
  much revenue normally lands by this date, and the pace that implies for year-end.
- **Days ahead — SNP 500 and expected revenue.** What conditions and expected revenue look like for
  the next several days, as plain facts. The required-vs-expected target gap and a "best lever" note
  are a second, smaller layer on top of that — include them only when genuinely informative.
- **Inventory and emerging trends.** Reorder signals that need a call, and anything else building
  over several days that's worth flagging as an early, still-forming pattern.
- **Online.** Traffic and what sold, plus — when the data exists — insight into how people are
  finding the business, and one thought on building or keeping momentum. Check what actually sold
  before characterising a channel, and be honest about small numbers (4 orders is not a trend).
- **Abandoned checkouts and other next-day actions.** Anything from web or in-store activity worth
  following up on tomorrow. Concrete and small is fine — this doesn't need to be a finding, just a
  worthwhile thing to do. Online checkouts only; in-store POS sales have no abandonment step.
- **A question or two for BJ.** When there's a real open question the data can't settle on its own
  — something only he'd know, or a judgment call only he can make — ask it plainly. Skip this some
  days rather than inventing a question. His answers are exactly how the 80/20 balance above shifts
  over time.

Website traffic is the one piece that's always worth a line, even on a nothing day — up or down on
the previous week, anything odd, in one sentence. BJ wants to watch this trend accumulate. Judge it
on its own scale: a move from 95 to 110 sessions is not "up 16%" in any meaningful sense — say
"traffic's roughly flat, ~100 a day."

## Weather is not colour commentary

Every day-over-day claim must be weather-adjusted. You get a beach_score (0–100) and a list of genuinely comparable recent days. Use them.

The pattern to follow: "Friday did $1,468 — but it was a prime beach day (score 84), and against the other prime beach days this month that's toward the low end." NOT "Friday did $1,468, up 25%."

A strong number on a perfect day can be an underperformance. Say so when it is.

## Reorder calls need lead time

When something is running low, do not just flag it. Say which of these applies and why:
1. **Reorder now** — sells year-round, or enough season remains to clear the lead time
2. **Let it sell out** — seasonal, lead time exceeds remaining season. Selling out is the goal, not a failure
3. **Don't restock** — didn't earn the shelf space

Do the calendar math out loud. A 30-day lead time ordered in mid-August lands as the season ends. If you don't know a vendor's lead time, say that's what you'd need to know.

## Length — this is a hard constraint

This email lands every single morning. If it takes more than two or three minutes to read, it
becomes noise and stops getting opened, and then all of this was pointless.

**Ceiling: roughly 350 words on a normal day.** That's more room than a single-topic email because
there are more pieces to touch on now (see Structure) — it is not license to write more per piece.
Each piece is a sentence or two of plain fact, not a paragraph of theory. A quiet day where most
pieces have nothing to add is still short.

To hit that, be ruthless about what goes in:
- State facts, don't build a case for them. "Sessions were flat around 100/day" beats three
  sentences arguing about why.
- No recap of numbers BJ can see in Shopify. He has the dashboard.
- No section that exists only because the structure implies it — if a piece has nothing worth
  saying, leave it out entirely rather than writing a placeholder sentence.
- Cut every sentence that explains something he already knows.

Structural facts about the business — that midweek trails weekends, that in-store beats online,
that August is the big month — belong in the JOURNAL, not the email. He knows them. Write them
down for your own future reference and leave them out of what he reads.

## Tone

- Write like a person. "I noticed", "worth flagging", "my guess is". Never "Daily Analytics Summary".
- Be specific enough to act on. Not "consider promoting beach gear" but "the tire deflators moved $260 on 4 sales and we're 12 days from empty with a 30-day lead time — that call needed making two weeks ago."
- Lead with anything urgent.
- Never use: leverage, synergies, actionable insights, deep dive, robust, key takeaways, circle back.
- Flag uncertainty honestly, and reach for a question before a guess. "I don't have the margin
  data to know if that's worth it" or "any idea why Tuesday's checkout traffic spiked? I don't
  have a read on that" both beat inventing an explanation.
- Sign off as Sandy.

## Output format

Return exactly these five blocks, in this order, with no text outside them:

<subject>A SHORT TAG ONLY — max 5 words, lowercase, naming the single most important thing about the day ("tire deflators critical", "quiet midweek", "strong saturday", "online flat again"). NOT a sentence and NOT a headline. The full subject line is assembled in code around this tag; you are only supplying the descriptor.</subject>
<signal>quiet | normal | busy</signal>
<email>
The email body as simple HTML: <p>, <b>, <ul>/<li>, and a small <table> when comparing numbers.
Use <h3> for section headings as the Structure section calls for — only for pieces you're actually
covering that day, in whatever order reads best. Nothing fancier.
</email>
<log>
The journal entry for this day, as markdown. This is written for future-you, not for BJ — it is
how the agent gets smarter. Include:

## Conditions
Weather, beach score, tide if known, day of week, position in season.

## What happened
By channel. Numbers with context.

## What I concluded
Your reading, and how confident you are.

## Open threads
Questions you could not answer and want revisited, including any question you asked BJ in the
email. Carry forward unresolved threads from previous days that are still open, and note here when
one gets answered (from `NOTES FROM BJ` below) so it stops being carried forward.

## Structural notes
Things you worked out about how the business behaves that BJ already knows intuitively and does
NOT need explained in an email — midweek versus weekend, seasonal shape, channel mix. Write them
here so you stop rediscovering them, and keep them out of what he reads.

## Notes from BJ
Anything the inbox contained and how it changed your read. Omit the section if the inbox was empty.
</log>
<learned>
Leave completely empty unless you found something that genuinely generalises beyond today — a
pattern worth carrying forward. If you did, write it as:

### YYYY-MM-DD — one-line claim
**Confidence: low|medium|high** — why.

The evidence, and what would confirm or kill it.

Most days this should be empty. Only real patterns go here.
</learned>"""


def _response_text(message) -> str:
    """
    Pull the text out of a response.

    Thinking-capable models put a ThinkingBlock first, so indexing content[0] blindly raises
    AttributeError and loses the whole email. Concatenate every text block instead.
    """
    parts = [
        block.text for block in message.content
        if getattr(block, "type", None) == "text" and getattr(block, "text", None)
    ]
    return "\n".join(parts).strip()


class ClaudeSynthesizer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def generate(self, data: dict, brain_context: dict) -> dict:
        message = self.client.messages.create(
            model=MODEL,
            # Generous because the response carries the email *and* the journal entry, and thinking
            # tokens count against this too. Running out truncates the trailing blocks silently —
            # the email arrives fine and the journal just never appears.
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": self._build_prompt(data, brain_context)}],
        )
        result = self._parse(_response_text(message))
        result["stop_reason"] = getattr(message, "stop_reason", None)
        if result["stop_reason"] == "max_tokens":
            print("   WARNING: response hit max_tokens — trailing blocks may be truncated",
                  file=sys.stderr)
        return result

    # Retained so older callers keep working.
    def generate_email(self, data: dict) -> dict:
        return self.generate(data, {})

    @staticmethod
    def _parse(text: str) -> dict:
        def block(tag, default=""):
            match = re.search(rf"<{tag}>(.*?)</{tag}>", text, re.DOTALL)
            return match.group(1).strip() if match else default

        email = block("email")
        if not email:
            # Model ignored the format — send what it wrote rather than nothing.
            email = f"<p>{text.strip()}</p>"

        return {
            "subject": block("subject", "daily update") or "daily update",
            "signal_level": (block("signal", "normal") or "normal").lower(),
            "body": email,
            "daily_log": block("log"),
            "learned": block("learned"),
        }

    @staticmethod
    def _recent_table(data: dict, trend: dict) -> str:
        """
        Every scored day alongside its revenue, as one table.

        Previously only the report date's score reached the prompt, so the agent could see that a
        Saturday did $3,023 but had no idea what kind of day it was — which blocked both the
        weekday-effect and event-effect questions it was trying to answer. The scores were already
        being computed; they just weren't being handed over.
        """
        from datetime import date as _date

        scores = data.get("snp500") or {}
        if not scores:
            return "  (no scored days available)"

        rows = []
        for day in sorted(scores):
            entry = scores[day] or {}
            if entry.get("score") is None:
                continue
            revenue = float((trend.get(day) or {}).get("gross_sales") or 0)
            orders = int((trend.get(day) or {}).get("orders") or 0)
            try:
                weekday = _date.fromisoformat(day).strftime("%a")
            except ValueError:
                weekday = "?"
            actual = f"${revenue:>8,.0f} / {orders:>3} orders" if revenue else "        — forecast"
            rows.append(
                f"  {day}  {weekday}  SNP {entry['score']:>3} {entry.get('rating', ''):<12} {actual}"
            )
        return "\n".join(rows) if rows else "  (no scored days available)"

    def _build_prompt(self, data: dict, brain: dict) -> str:
        shopify = data.get("shopify", {})
        sales = shopify.get("sales", {})
        weather = data.get("weather", {})
        report_date = sales.get("report_date", data.get("date", "yesterday"))

        weather_days = weather.get("days", {}) if weather.get("available") else {}
        today_weather = weather_days.get(report_date, {})
        comparables = data.get("comparable_days", [])

        # Weather-matched comparison — the point is like-for-like, not calendar-adjacent.
        comparison_lines = []
        trend = {str(r.get("day", ""))[:10]: r for r in sales.get("weekly_trend", [])}
        for day in comparables:
            row = trend.get(day["date"])
            revenue = float(row.get("gross_sales") or 0) if row else None
            comparison_lines.append(
                f"  {day['date']}: {day['beach_label']} (score {day['beach_score']}), "
                f"{day['conditions']}, feels {day.get('feels_like_f')}°F"
                + (f" → ${revenue:,.2f}" if revenue else " → no sales data")
            )

        tides = weather.get("tides", {})
        tide_day = (tides.get("by_day", {}) or {}).get(report_date) if tides.get("available") else None

        sections = [
            f"""Write today's email and journal entry. You are writing on {data.get('date')}, reporting on {report_date}.

═══ BUSINESS CONTEXT (curated by BJ — authoritative, trust over your own inference) ═══
{brain.get('context') or '(none yet)'}""",
        ]

        if brain.get("inbox"):
            sections.append(
                f"═══ NOTES FROM SANDY, UNPROCESSED ═══\n"
                f"React to these. They are corrections and context from someone who was there.\n\n"
                f"{brain['inbox']}"
            )

        if brain.get("learned"):
            sections.append(
                f"═══ WHAT YOU'VE LEARNED SO FAR (your own notes — hypotheses, not truth) ═══\n"
                f"{brain['learned']}"
            )

        if brain.get("events"):
            sections.append(
                "═══ EVENTS LOG ═══\n"
                "Things that happened which the data alone can't show. If one falls on the day being\n"
                "reported, say so — an unexplained spike is worse than no spike. Be careful not to\n"
                "credit an event for something it plausibly didn't cause; say what's consistent with\n"
                "what, and what would actually settle it.\n\n"
                f"{brain['events']}"
            )

        if brain.get("open_projects"):
            projects = "\n\n".join(
                f"### {p['name']} — {p['status']}\n"
                f"Next action: {p['next_action'] or '(none recorded)'}"
                for p in brain["open_projects"]
            )
            sections.append(
                "═══ OPEN PROJECTS ═══\n"
                "Loops that are started but not finished. Surface AT MOST ONE, and only when\n"
                "today's data gives a real reason to — a project connected to something that\n"
                "actually happened. A daily nag gets ignored, which defeats the point. If nothing\n"
                "in today's numbers touches any of these, mention none.\n\n"
                f"{projects}"
            )

        if brain.get("open_threads"):
            sections.append(
                "═══ OPEN THREADS FROM PREVIOUS DAYS ═══\n"
                "Revisit these where today's data speaks to them.\n"
                + "\n".join(f"- {t}" for t in brain["open_threads"])
            )

        if brain.get("recent_logs"):
            recent = "\n\n".join(
                f"--- {day} ---\n{content}" for day, content in brain["recent_logs"][:3]
            )
            sections.append(f"═══ YOUR RECENT JOURNAL ENTRIES ═══\n{recent}")

        snp = (data.get("snp500") or {}).get(report_date, {})
        exp = data.get("expectation") or {}
        expectation_line = (
            f"Expected about ${exp['expected_revenue']:,} for a day this good. "
            f"Actual ${exp['actual_revenue']:,.2f} — {exp['pct_of_expected']}% of that, "
            f"{exp['verdict']} (gap ${exp['gap']:+,.0f})."
            if exp.get("available") else "Expectation unavailable."
        )

        sections.append(f"""═══ CONDITIONS ON {report_date} ═══

SNP 500: {snp.get('score', 'unavailable')}/500 — {snp.get('rating', '?')} (confidence {snp.get('confidence', '?')})
{snp.get('headline', '')}
  Strongest positives: {', '.join(snp.get('drivers_positive', [])) or 'none'}
  Limiting factors:    {', '.join(str(d) for d in snp.get('drivers_negative', [])) or 'none'}

**{expectation_line}**

This is the most important framing in the whole report. Revenue means nothing without the kind of
day it was: $1,468 on a 480 day is a miss, and $640 on a 150 day is a win. Lead the in-store section
with how the day did against expectation, not with the raw number.

The expectation curve is a gut baseline from BJ (rainy day ≈ $500, perfect beach day ≈ $2,000),
not a fitted model. Treat it as a rough yardstick — say "well short of what a day like that should
do", not "12.4% below forecast".

{f"Weather: {today_weather.get('conditions')}, high {today_weather.get('high_f')}°F, feels like {today_weather.get('feels_like_f')}°F" if today_weather else "Weather: unavailable"}
{f"Precipitation: {today_weather.get('precip_in')} in | Wind: {today_weather.get('wind_mph')} mph | Sun: {today_weather.get('sunshine_hours')} hrs" if today_weather else ""}
{f"Tides: {json.dumps(tide_day)}" if tide_day else "Tides: not configured"}

COMPARABLE RECENT DAYS (similar SNP 500 — compare against THESE, not against the calendar):
{chr(10).join(comparison_lines) if comparison_lines else "  none found in range"}

RECENT DAYS — CONDITIONS AND REVENUE TOGETHER
Every scored day in range, so any two days can be compared like for like. Use this rather than
asking for scores you already have.
{self._recent_table(data, trend)}""")

        sections.append(f"""═══ IN-STORE (Point of Sale) ═══
Channel split, last 7 days:
{json.dumps(data.get('channel_split', []), indent=2)}

Channel split on {report_date}:
{json.dumps(data.get('channel_day', []), indent=2)}

Top in-store sellers, last 7 days:
{json.dumps(data.get('instore_products', []), indent=2)}

Season to date:
{json.dumps(data.get('season', {}), indent=2)}

YEAR AGAINST TARGET:
{json.dumps(data.get('pacing', {}), indent=2)}

Pacing is seasonal, never a straight line — "we're 60% through the year" means nothing when August
carries a fifth of it. Talk about it as: where the year sits against the $190k target given how much
normally lands by now, and what that projects to at year end. If `basis` says the curve is estimated
rather than measured prior-year history, say so — don't present a guess as a measurement.

This is now a standing daily line, not something that only appears when it moves — but keep it to
one sentence unless the phase is genuinely turning or something about it actually needs more.

WEEK AHEAD — SNP 500 and expected revenue, plus what's required against the target:
{json.dumps(data.get('forecast', {}), indent=2)}

The primary fact for the "days ahead" piece of the email is simply `days[].snp500` and
`days[].expected` for the next several days — report that plainly, e.g. "Thu 425 (~$1,300), Fri 460
(~$1,700), Sat 480 (~$2,000)". That's the 80% observation half of this section.

`required` — what a day needs to do to stay on track for the $190k target — is the smaller, second
layer on top, and only worth including when it says something `expected` alone doesn't: a day can
clear `expected` and still miss `required`, and reporting only `expected` congratulates the business
for keeping pace with itself while the target quietly slips. Speak in rough terms either way — both
numbers rest on a gut-level expectation curve, not a fitted model: "the week ahead looks about
$1,500 light against what the target needs," never a precise-sounding forecast.

If you do have a genuine, well-supported suggestion, `best lever` names the highest-quality day
still carrying a gap — the day where a push would actually land, not the day with the biggest
shortfall (a washout isn't fixable, a busy Saturday is improvable). Only suggest a specific action
when the numbers actually support it and you can say what it's meant to close — this is the 20%
insight half of the section, so most days it's fine to have nothing here. Never suggest re-running a
specific past one-off event as if it were a proven lever (see "A one-off event is a data point, not
a playbook" above). Do not invent promotions to fill space.

Whole-store daily totals, last 14 days:
{json.dumps(sales.get('weekly_trend', [])[-14:], indent=2)}

Headline for {report_date}: ${sales.get('revenue', 0):,.2f} across {sales.get('orders', 0)} orders, AOV ${sales.get('aov', 0):,.2f}
  vs. day before: ${sales.get('prior_day_revenue', 0):,.2f}
  vs. same weekday last week: ${sales.get('last_week_revenue', 0):,.2f}
  vs. trailing 7-day average: ${sales.get('week_avg_revenue', 0):,.2f}""")

        sections.append(f"""═══ REORDER SIGNALS (stock paired with recent velocity) ═══
days_of_cover = units on hand ÷ units sold per day. Check it against vendor lead times in the
context file. Where a lead time isn't recorded, say that's what you'd need.

{json.dumps(data.get('reorder_signals', []), indent=2) if data.get('reorder_signals') else "No products under 45 days of cover, or inventory data unavailable."}""")

        online_products = data.get("online_products", [])
        tiktok_products = data.get("tiktok_products", [])
        conv = shopify.get("conversion_metrics", {})
        google = data.get("google_local", {})
        google_real = google if google.get("available") and not google.get("stub") else {}

        traffic_line = (
            f"Sessions last 7 days: {conv['sessions_7d']} vs {conv['sessions_prior_7d']} the week "
            f"before ({conv['sessions_change_pct']:+.1f}%)"
            if conv.get("sessions_change_pct") is not None
            else f"Sessions last 7 days: {conv.get('sessions_7d', 'unavailable')} "
                 f"(no prior week to compare)"
        )

        sections.append(f"""═══ ONLINE (analyse in a vacuum, on its own scale) ═══

WEBSITE TRAFFIC — always worth one line in the email, even on a nothing day
{traffic_line}
Daily sessions (oldest first): {json.dumps([d['sessions'] for d in conv.get('daily_sessions', [])])}
Sessions on {report_date}: {conv.get('sessions', 'unavailable')}
Funnel: {conv.get('cart_additions','?')} cart adds → {conv.get('reached_checkout','?')} reached checkout → {conv.get('completed_checkout','?')} completed

Top online-store sellers, last 7 days:
{json.dumps(online_products, indent=2) if online_products else "none"}

Top TikTok sellers, last 7 days (check WHAT sold before characterising the channel):
{json.dumps(tiktok_products, indent=2) if tiktok_products else "none"}

Referral sources, last 7 days:
{json.dumps(shopify.get('referral_sources', []), indent=2)}

Email marketing (Klaviyo):
{json.dumps(data.get('klaviyo', {}), indent=2) if data.get('klaviyo') and not data.get('klaviyo', {}).get('stub') else "not connected — omit from the email entirely"}

Social:
{json.dumps({k: v for k, v in data.get('social', {}).items() if isinstance(v, dict) and not v.get('stub')}, indent=2, default=str) or "not connected — omit from the email entirely"}

How people are finding the business (Google Business Profile / Search Console):
{json.dumps(google_real, indent=2) if google_real else "not connected — omit from the email entirely. Apple Maps has no public analytics API and never will be available here."}

A momentum-building thought (a post idea, a follow-up, leaning into something that's working) is
worth including when today's data actually points at one — not as a standing requirement. Most days
reporting the activity honestly is the whole job here.""")

        abandoned = data.get("abandoned_checkouts") or []
        sections.append(f"""═══ ABANDONED CHECKOUTS — contact info given, purchase not completed, last 48h ═══
Online-checkout-only; in-store POS sales have no abandonment step.

{json.dumps(abandoned, indent=2) if abandoned else "none in the last 48 hours"}

Most days this is a line in the journal, not the email — only surface it when something stands out
(a high-value cart, a repeat customer, several carts dropping at the same product or step). When you
do mention one, a specific, low-effort next step (a personal follow-up, checking if a product page
was confusing) beats a generic suggestion to 'consider email marketing'.""")

        if data.get("errors"):
            sections.append(
                "═══ DATA GAPS THIS RUN ═══\n"
                "Do not mention these in the email. Note them in the journal.\n"
                + "\n".join(f"- {e}" for e in data["errors"])
            )

        return "\n\n".join(sections)
