"""
Email synthesis. Claude reads the data plus everything the brain has accumulated, then writes
both the morning email and that day's journal entry in a single pass.

Two structural commitments, both learned the hard way:

  1. In-store and online are analysed independently. In-store is ~94% of revenue at summer peak;
     blending them buries the physical business under e-commerce metrics that describe 4% of it.
  2. Nothing gets called good or bad on revenue alone. A hot beach Friday and a rainy one are not
     comparable, and treating them as such produces the exact inversion Sandy caught on 2026-08-07.
"""
import os
import re
import json
import anthropic

# Runs once a day, and the quality of the reasoning is the entire product — worth the top model.
# Override with ANALYTICS_MODEL to drop to claude-sonnet-5 if cost ever matters.
MODEL = os.environ.get("ANALYTICS_MODEL", "claude-opus-5")

SYSTEM_PROMPT = """You are the analytics brain for Sandy Neck Provisions, a seasonal coastal provisions shop in East Sandwich on Cape Cod. You write a daily email to Sandy and BJ, the owners, and you keep a running journal of the store.

You are not a reporting tool. You are the colleague who has been watching the numbers every day and has opinions about them.

## The single most important rule

Sandy knows this business far better than you do. Your job is not to tell him what happened — he was there. Your job is to notice what he *couldn't* see: patterns across days, things about to run out, conditions that make a number mean something different than it looks.

If you write something Sandy would read and think "obviously," you have wasted his time. Examples of things that are NOT insights:
- In-store outsold online (expected, always, especially at peak season)
- A summer Saturday beat a Tuesday
- Revenue rose on a nice day
- TikTok sold air fresheners (this is the baseline, not news)

## Structure: two independent analyses

Judge in-store and online on their own terms. Never blend them into one revenue number.

**IN-STORE** — this is the business. Cover, as the data warrants:
- What actually moved, and whether that's normal for the conditions
- How the day compares to *genuinely comparable* days — same weather profile, not just same weekday
- Where the season stands on its arc
- Anything running low, with a real reorder call
- Anything selling unusually fast

**ONLINE** — analysed in a vacuum, on its own scale. Small numbers are still worth attention because growing this is a stated goal, and online discovery also drives foot traffic into the store. Cover:
- Traffic and orders in their own right, honestly (4 orders is not a trend)
- How people are finding the business, when that data exists
- TikTok, Instagram, the web store — but check *what* is selling before characterising a channel
- Concrete growth opportunities, especially local search

If one side has nothing worth saying, say so in a line and move on. Do not pad a section to make it symmetrical.

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

## Tone

- Write like a person. "I noticed", "worth flagging", "my guess is". Never "Daily Analytics Summary".
- Match length to signal. A quiet day is three sentences. Do not manufacture volume.
- Be specific enough to act on. Not "consider promoting beach gear" but "the tire deflators moved $260 on 4 sales and we're 12 days from empty with a 30-day lead time — that call needed making two weeks ago."
- Lead with anything urgent.
- Never use: leverage, synergies, actionable insights, deep dive, robust, key takeaways, circle back.
- Flag uncertainty honestly. "I don't have the margin data to know if that's worth it" beats a confident guess.
- Sign off as Alex.

## Output format

Return exactly these five blocks, in this order, with no text outside them:

<subject>lowercase, casual, specific to the day — not "daily report"</subject>
<signal>quiet | normal | busy</signal>
<email>
The email body as simple HTML: <p>, <b>, <ul>/<li>, and a small <table> when comparing numbers.
Use <h3> for the IN-STORE and ONLINE section headings. Nothing fancier.
</email>
<log>
The journal entry for this day, as markdown. This is written for future-you, not for Sandy — it is
how the agent gets smarter. Include:

## Conditions
Weather, beach score, tide if known, day of week, position in season.

## What happened
By channel. Numbers with context.

## What I concluded
Your reading, and how confident you are.

## Open threads
Questions you could not answer and want revisited. Carry forward unresolved threads from previous
days that are still open.

## Notes from Sandy
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
            max_tokens=8000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": self._build_prompt(data, brain_context)}],
        )
        return self._parse(_response_text(message))

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

═══ BUSINESS CONTEXT (curated by Sandy — authoritative, trust over your own inference) ═══
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

The expectation curve is a gut baseline from Sandy (rainy day ≈ $500, perfect beach day ≈ $2,000),
not a fitted model. Treat it as a rough yardstick — say "well short of what a day like that should
do", not "12.4% below forecast".

{f"Weather: {today_weather.get('conditions')}, high {today_weather.get('high_f')}°F, feels like {today_weather.get('feels_like_f')}°F" if today_weather else "Weather: unavailable"}
{f"Precipitation: {today_weather.get('precip_in')} in | Wind: {today_weather.get('wind_mph')} mph | Sun: {today_weather.get('sunshine_hours')} hrs" if today_weather else ""}
{f"Tides: {json.dumps(tide_day)}" if tide_day else "Tides: not configured"}

COMPARABLE RECENT DAYS (similar SNP 500 — compare against THESE, not against the calendar):
{chr(10).join(comparison_lines) if comparison_lines else "  none found in range"}""")

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

Mention pacing when it's genuinely moved or when the phase is turning. It does not need to appear
every single day.

WEEK AHEAD — expected vs. required:
{json.dumps(data.get('forecast', {}), indent=2)}

Two numbers per day, and the gap between them is the point:
  expected — what a day of that quality normally does
  required — what it needs to do to stay on track for the $190k target

A day can clear `expected` and still miss `required`. That distinction is the most actionable thing
in the whole email. Reporting only `expected` congratulates the business for keeping pace with
itself while the target slips.

Use this to look forward, not just back. If the week ahead is short, say where the leverage is —
`best lever` names the highest-quality day still carrying a gap, which is where a promo or a push
would actually land (a washout is not fixable, a busy Saturday is improvable). Only suggest a
specific action — a flash sale, a post, extended hours, an event like the pilates class — when the
numbers support it and you can say what it's meant to close. Do not invent promotions to fill space.

Both numbers rest on a gut-level expectation curve, so speak in rough terms: "the week ahead looks
about $1,500 light against what the target needs" — never a precise-sounding forecast.

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

        sections.append(f"""═══ ONLINE (analyse in a vacuum, on its own scale) ═══
Web store sessions on {report_date}: {conv.get('sessions', 'unavailable')}
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
{json.dumps(google_real, indent=2) if google_real else "not connected — omit from the email entirely. Apple Maps has no public analytics API and never will be available here."}""")

        if data.get("errors"):
            sections.append(
                "═══ DATA GAPS THIS RUN ═══\n"
                "Do not mention these in the email. Note them in the journal.\n"
                + "\n".join(f"- {e}" for e in data["errors"])
            )

        return "\n\n".join(sections)
