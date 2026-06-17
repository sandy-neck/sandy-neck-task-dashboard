import os
import json
import anthropic

SYSTEM_PROMPT = """You are the analytics advisor for Sandy Neck Provisions, a seasonal e-commerce business on Cape Cod (East Sandwich / Barnstable area) selling premium seafood, local provisions, and Cape Cod specialties.

Business context:
- Owners: Sandy (Operations & Analytics) and BJ (Owner / Strategy)
- Location: East Sandwich / Sandy Neck area, Cape Cod, MA
- Seasonal peak: Memorial Day through Labor Day (summer)
- ~993 active products across seafood, provisions, local specialties
- Shopify plan: Basic
- Key goals: conversion rate 15-25%, repeat customer growth, email list monetization
- Active channels: Instagram, Facebook, TikTok, YouTube, Klaviyo email
- Local context: customers find the store via Maps searches, Cape Cod tourism, summer residents

Your job: analyze today's data from Shopify, Klaviyo email, social media, and Google local presence, then produce sharp, specific insights and prioritized recommendations.

Recommendation focus areas: marketing/content opportunities, cash flow/revenue signals, conversion optimization, email marketing leverage, and local SEO / Google Ads opportunities.

Tone: direct, practical, numbers-first. No filler. Sandy and BJ are smart operators who want concrete next actions."""


class ClaudeSynthesizer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def analyze(self, data: dict) -> dict:
        prompt = self._build_prompt(data)
        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        text = message.content[0].text
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return {
                "summary": text[:500],
                "headline_metric": "",
                "insights": [],
                "recommendations": [],
                "alerts": [],
            }

    def _build_prompt(self, data: dict) -> str:
        shopify = data.get("shopify", {})
        social = data.get("social", {})
        klaviyo = data.get("klaviyo", {})
        google = data.get("google_local", {})
        sales = shopify.get("sales", {})

        today_rev = sales.get("today_revenue", 0) or 0
        yesterday_rev = sales.get("yesterday_revenue", 0) or 0
        rev_pct = ((today_rev - yesterday_rev) / yesterday_rev * 100) if yesterday_rev > 0 else 0
        today_orders = sales.get("today_orders", 0) or 0
        today_aov = sales.get("today_aov", 0) or 0

        conv = shopify.get("conversion_metrics", {})
        customers = shopify.get("customer_insights", {})
        top_products = shopify.get("top_products", [])
        referrals = shopify.get("referral_sources", [])
        low_inventory = shopify.get("inventory_alerts", [])

        # Klaviyo summary
        kl_rev = klaviyo.get("revenue_7d") if klaviyo else None
        kl_campaigns = klaviyo.get("campaigns", []) if klaviyo else []
        best_campaign = max(
            (c for c in kl_campaigns if c.get("revenue")),
            key=lambda c: c.get("revenue", 0), default=None
        )

        # Google local
        bp = google.get("business_profile", {}) if google else {}
        sc = google.get("search_console", {}) if google else {}
        opp_terms = sc.get("low_ctr_opportunities", [])

        stub_note = ""
        stubs = [k for k, v in social.items() if isinstance(v, dict) and v.get("stub")]
        if stubs or klaviyo.get("stub") or google.get("stub"):
            items = stubs + (["klaviyo"] if klaviyo.get("stub") else []) + (["google"] if google.get("stub") else [])
            stub_note = f"\n⚠️ Sample/stub data for: {', '.join(items)} — treat as directional."

        return f"""Today's full data for Sandy Neck Provisions ({data.get('date', 'today')}):
{stub_note}

## SHOPIFY STORE PERFORMANCE
Revenue today: ${today_rev:,.2f} ({rev_pct:+.1f}% vs yesterday's ${yesterday_rev:,.2f})
Orders today: {today_orders}  |  AOV: ${today_aov:,.2f}
Sessions: {conv.get('sessions', '—')}  |  Conversion rate: {conv.get('conversion_rate', '—')}
Cart abandonment: {conv.get('cart_additions', '—')} added to cart → {conv.get('reached_checkout', '—')} reached checkout → {conv.get('completed_checkout', '—')} purchased

New customers (7d): {customers.get('new_customers_7d', '—')}
Returning customers (7d): {customers.get('returning_customers_7d', '—')}
Return rate: {customers.get('returning_rate', '—')}%

Top products (7d):
{json.dumps(top_products, indent=2)}

Traffic & revenue by referral source (7d):
{json.dumps(referrals, indent=2)}

Low inventory alerts:
{json.dumps(low_inventory, indent=2)}

## KLAVIYO EMAIL MARKETING
Email-attributed revenue (7d): {f"${kl_rev:,.2f}" if kl_rev else "—"}
Best campaign: {f"{best_campaign['name']} — {best_campaign['open_rate']:.0%} open, {best_campaign['click_rate']:.0%} click, ${best_campaign['revenue']:,.0f} revenue" if best_campaign else "—"}
Recent campaigns: {json.dumps(kl_campaigns[:3], indent=2)}
List sizes: {json.dumps(klaviyo.get('list_growth', {}), indent=2)}

## GOOGLE LOCAL PRESENCE (last 7 days)
Google Maps views: {bp.get('maps_views_7d', '—')}
Google Search listing views: {bp.get('search_views_7d', '—')}
Direction requests: {bp.get('direction_requests_7d', '—')}
Website clicks from Maps/Search: {bp.get('website_clicks_7d', '—')}
Phone calls: {bp.get('phone_calls_7d', '—')}
Top search terms that found the business: {json.dumps(bp.get('top_search_keywords', [])[:6], indent=2)}

Google Search Console (organic search):
Total clicks: {sc.get('total_clicks_7d', '—')}  |  Impressions: {sc.get('total_impressions_7d', '—')}  |  Avg CTR: {sc.get('avg_ctr', '—')}%
Top queries: {json.dumps(sc.get('top_queries', [])[:5], indent=2)}
High-impression, low-CTR opportunities (for SEO + Google Ads): {json.dumps(opp_terms, indent=2)}

## SOCIAL MEDIA (last 7 days)
{json.dumps(social, indent=2, default=str)}

---
Respond with ONLY a valid JSON object (no markdown wrapper, no code fences), exactly this structure:
{{
  "summary": "2-3 sentence executive summary. Lead with the most important number or trend.",
  "headline_metric": "Single most actionable number or trend today — max 12 words",
  "insights": [
    {{"title": "Short title", "detail": "Specific observation with numbers from the data", "impact": "high|medium|low"}}
  ],
  "recommendations": [
    {{
      "priority": 1,
      "action": "Specific action verb + what to do",
      "rationale": "Why this matters for Sandy Neck right now — be specific, reference the data",
      "category": "marketing|revenue|conversion|email|seo",
      "effort": "quick-win|this-week|strategic"
    }}
  ],
  "alerts": [
    {{"type": "warning|opportunity|info", "message": "Brief, specific message"}}
  ]
}}

Provide 3-4 insights and 4-6 recommendations covering: revenue/cash flow signals, marketing/content opportunities, conversion optimization, email leverage, and local SEO / Google Ads keywords (e.g. if "cape cod seafood delivery" has 620 impressions but only 4.5% CTR at position 8, that's a clear Google Ads opportunity with clear rationale)."""
