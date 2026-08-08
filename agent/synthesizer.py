"""
Email synthesis: Claude reads all the data and writes the email itself.

No fixed template. Claude decides:
- How long the email should be (3 sentences on a quiet day, detailed on a big day)
- Which sections deserve attention (skips sections with nothing to say)
- Whether to include tables, bullet points, or just prose
- The appropriate level of urgency and tone

The goal: an email a smart internal colleague would actually write, not a dashboard.
"""
import os
import json
import anthropic

SYSTEM_PROMPT = """You are the analytics brain for Sandy Neck Provisions, a seasonal Cape Cod e-commerce business selling premium seafood, provisions, and local specialties. You have access to daily data from Shopify, Klaviyo email marketing, social media, and Google search/maps.

Your job: write a daily analytics email to Sandy and BJ (the owners). This email comes from you — treat yourself as a trusted internal colleague, not a reporting tool.

CRITICAL TONE RULES:
- Write like a real person, not a report generator. No "Daily Analytics Summary for [DATE]" headers.
- Use "I" naturally. "I noticed X." "Worth flagging:" "Quick one today —"
- Match length to signal: if nothing changed, 3 sentences is right. If there's a real opportunity or problem, be specific and detailed.
- Never pad. If there's nothing interesting about social media today, don't mention social media.
- Never use phrases like: "leveraging synergies", "actionable insights", "deep dive", "touch base", "robust", "key takeaways", or any corporate filler.
- A recommendation should be specific enough that Sandy knows exactly what to do next. Not "consider email marketing" but "that lobster bisque post from Tuesday hit 4x normal engagement — worth a follow-up email to the newsletter list this week while it's fresh."
- If something needs urgent attention (inventory going to zero, revenue down 40%, checkout broken), say so plainly and put it first.
- If it's a quiet day, say so. End it there. A brief email that respects their time is better than a long one they'll start skimming.

WHAT THIS REPORT COVERS:
- The email goes out early morning, so it reports on YESTERDAY — the last complete sales day.
- Write about yesterday in the past tense: "yesterday did $1,468" not "today we're at $1,468".
- Judge a day against the trailing average and the same weekday a week ago, not just the day before.
  One Saturday vs. one Tuesday is not a trend; a Saturday down 40% against last Saturday is.
- "Today so far" numbers are only a few hours old. Never headline them.

CONTEXT ABOUT THE BUSINESS:
- Seasonal peak: Memorial Day through Labor Day on Cape Cod
- ~993 products: seafood, local provisions, Cape Cod specialties
- Location: East Sandwich / Sandy Neck area, Barnstable County
- Active on Instagram, Facebook, TikTok, YouTube, and Klaviyo email
- Key targets: conversion rate 15-25%, repeat customer growth
- Shopify Basic plan
- Current date context matters — if it's a Tuesday in mid-June, that's shoulder season ramp-up

EMAIL FORMAT:
- Plain subject line, like a person would write: "quick update" or "big day yesterday" or "heads up on inventory" — not "Daily Analytics Report for June 17"
- Start with the most important thing, not pleasantries
- Use simple HTML: <p>, <b>, <br>, <ul>/<li>, maybe a simple <table> if comparing numbers makes sense. Nothing fancy.
- Sign off as: Alex (your internal analytics persona)
- Never mention "stub data", "sample data", or that any source is unavailable — just omit that source silently"""


class ClaudeSynthesizer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def generate_email(self, data: dict) -> dict:
        prompt = self._build_prompt(data)
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=3000,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text

        # Parse the JSON wrapper Claude returns
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            result = json.loads(text[start:end])
        except Exception:
            # Fallback: treat the whole response as the email body
            result = {
                "subject": "daily update",
                "body": text,
                "signal_level": "normal",
            }

        return result

    def _build_prompt(self, data: dict) -> str:
        shopify = data.get("shopify", {})
        social = data.get("social", {})
        klaviyo = data.get("klaviyo", {})
        google = data.get("google_local", {})
        sales = shopify.get("sales", {})

        # The headline is the last COMPLETE day. At 7 AM, "today" is nearly empty.
        report_date = sales.get("report_date", "yesterday")
        revenue = sales.get("revenue", 0) or 0
        n_orders = sales.get("orders", 0) or 0
        aov = sales.get("aov", 0) or 0
        prior_rev = sales.get("prior_day_revenue", 0) or 0
        last_week_rev = sales.get("last_week_revenue", 0) or 0
        week_avg = sales.get("week_avg_revenue", 0) or 0

        def compare(label, baseline):
            if not baseline:
                return f"vs. {label}: no data"
            delta = (revenue - baseline) / baseline * 100
            return f"vs. {label} (${baseline:,.2f}): {delta:+.1f}%"

        vs_prior = compare("the day before", prior_rev)
        vs_last_week = compare("same weekday last week", last_week_rev)
        vs_avg = compare("trailing 7-day average", week_avg)

        conv = shopify.get("conversion_metrics", {})
        customers = shopify.get("customer_insights", {})
        top_products = shopify.get("top_products", [])
        referrals = shopify.get("referral_sources", [])
        low_inventory = shopify.get("inventory_alerts", [])

        weekly_trend = sales.get("weekly_trend", [])
        today_rev = sales.get("today_so_far_revenue", 0) or 0
        today_orders = sales.get("today_so_far_orders", 0) or 0

        # Klaviyo
        kl_rev = klaviyo.get("revenue_7d") if klaviyo and not klaviyo.get("stub") else None
        kl_campaigns = [c for c in (klaviyo.get("campaigns", []) if klaviyo and not klaviyo.get("stub") else [])]

        # Social (only real data, skip stubs)
        real_social = {k: v for k, v in social.items() if isinstance(v, dict) and v.get("available") and not v.get("stub")}

        # Google (only real data)
        google_real = google if google and google.get("available") and not google.get("stub") else {}
        bp = google_real.get("business_profile", {})
        sc = google_real.get("search_console", {})
        opp_terms = sc.get("low_ctr_opportunities", [])

        return f"""Here's the data for Sandy Neck Provisions. You're writing on {data.get('date', 'today')}. Write the email now.

SHOPIFY STORE — {report_date} (the last complete sales day — this is the headline)
Revenue: ${revenue:,.2f}
  {vs_prior}
  {vs_last_week}
  {vs_avg}
Orders: {n_orders}  |  AOV: ${aov:,.2f}

TODAY SO FAR: {today_orders} orders, ${today_rev:,.2f} — only a few hours old at send time.
Never lead with this or treat it as a trend; mention it only if it's genuinely remarkable.

Sessions: {conv.get('sessions', 'unavailable')}
Conversion rate: {conv.get('conversion_rate', 'unavailable')}
Cart → checkout → purchased: {conv.get('cart_additions','?')} → {conv.get('reached_checkout','?')} → {conv.get('completed_checkout','?')}
New customers (7d): {customers.get('new_customers_7d','unavailable')}
Returning customers (7d): {customers.get('returning_customers_7d','unavailable')} ({customers.get('returning_rate','?')}% return rate)

Weekly trend (last 7 days, most recent last):
{json.dumps(weekly_trend[-7:], indent=2)}

Top products this week:
{json.dumps(top_products, indent=2)}

Traffic & revenue by source (7d):
{json.dumps(referrals, indent=2)}

LOW INVENTORY (≤10 units):
{json.dumps(low_inventory, indent=2) if low_inventory else "None flagged"}

KLAVIYO EMAIL{" (no data — omit from email)" if not kl_campaigns else ""}
Email-attributed revenue (7d): {f"${kl_rev:,.2f}" if kl_rev else "unavailable"}
Recent campaigns: {json.dumps(kl_campaigns[:3], indent=2)}

SOCIAL MEDIA{" (no real data available today — omit from email)" if not real_social else ""}
{json.dumps(real_social, indent=2, default=str) if real_social else ""}

GOOGLE LOCAL PRESENCE{" (no real data available today — omit from email)" if not google_real else ""}
{f"Maps views (7d): {bp.get('maps_views_7d')}" if bp else ""}
{f"Direction requests (7d): {bp.get('direction_requests_7d')}" if bp else ""}
{f"Top search keywords: {json.dumps(bp.get('top_search_keywords', [])[:5])}" if bp else ""}
{f"Organic search: {sc.get('total_clicks_7d')} clicks, {sc.get('total_impressions_7d')} impressions, {sc.get('avg_ctr')}% CTR" if sc else ""}
{f"Low-CTR keyword opportunities (good for Google Ads): {json.dumps(opp_terms)}" if opp_terms else ""}

---
Now write the email. Return ONLY a JSON object with this structure:
{{
  "subject": "subject line (lowercase, casual, specific — not 'daily analytics report')",
  "body": "the full email HTML body — use <p>, <b>, <ul>/<li>, simple <table> where helpful. Start with the most important thing. Match length to signal. Sign off as Alex.",
  "signal_level": "quiet|normal|busy"
}}

signal_level guide:
- "quiet": nothing materially changed, email is 2-4 sentences
- "normal": a few things worth noting, email is a few paragraphs
- "busy": something urgent or a real opportunity requiring attention, email is detailed with specifics"""
