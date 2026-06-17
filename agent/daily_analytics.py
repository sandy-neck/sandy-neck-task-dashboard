#!/usr/bin/env python3
"""
Sandy Neck Provisions — Daily Analytics Agent
Runs via GitHub Actions cron at 7 AM ET every day.
"""
import os
import sys
from datetime import datetime
import pytz

from shopify_client import ShopifyClient
from social_client import SocialClient
from klaviyo_client import KlaviyoClient
from google_local_client import GoogleLocalClient
from synthesizer import ClaudeSynthesizer
from email_report import EmailReporter

ET = pytz.timezone("America/New_York")


def main():
    now = datetime.now(ET)
    run_date = now.strftime("%A, %B %-d, %Y")
    print(f"[{now.strftime('%I:%M %p ET')}] Sandy Neck Analytics — {run_date}")
    print("-" * 55)

    payload = {
        "date": run_date,
        "shopify": {},
        "social": {},
        "klaviyo": {},
        "google_local": {},
        "errors": [],
    }

    # ── Shopify ────────────────────────────────────────────────────────────────
    print("📦 Fetching Shopify data...")
    try:
        shopify = ShopifyClient()
        sales = shopify.get_sales_summary()
        payload["shopify"] = {
            "sales": sales,
            "top_products": shopify.get_top_products(),
            "referral_sources": shopify.get_referral_sources(),
            "customer_insights": shopify.get_customer_insights(),
            "inventory_alerts": shopify.get_low_inventory(),
            "conversion_metrics": shopify.get_conversion_metrics(),
        }
        print(f"   Revenue today:  ${sales.get('today_revenue', 0):,.2f}")
        print(f"   Orders today:   {sales.get('today_orders', 0)}")
        print(f"   Data source:    {sales.get('source', 'unknown')}")
    except Exception as e:
        msg = f"Shopify: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Social ─────────────────────────────────────────────────────────────────
    print("📱 Fetching social media data...")
    try:
        social = SocialClient()
        payload["social"] = social.get_all_metrics()
        active = [k for k, v in payload["social"].items() if isinstance(v, dict) and v.get("available")]
        stubs = [k for k, v in payload["social"].items() if isinstance(v, dict) and v.get("stub")]
        print(f"   Active platforms: {', '.join(active) or 'none'}")
        if stubs:
            print(f"   Stub mode (sample data): {', '.join(stubs)}")
    except Exception as e:
        msg = f"Social: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Klaviyo ────────────────────────────────────────────────────────────────
    print("✉️  Fetching Klaviyo data...")
    try:
        klaviyo = KlaviyoClient()
        payload["klaviyo"] = klaviyo.get_metrics()
        rev = payload["klaviyo"].get("revenue_7d")
        print(f"   Email revenue (7d): {f'${rev:,.2f}' if rev else 'unavailable'}")
        if payload["klaviyo"].get("stub"):
            print("   Stub mode: klaviyo")
    except Exception as e:
        msg = f"Klaviyo: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Google Local ───────────────────────────────────────────────────────────
    print("🗺️  Fetching Google local presence data...")
    try:
        google = GoogleLocalClient()
        payload["google_local"] = google.get_all_metrics()
        bp = payload["google_local"].get("business_profile", {})
        sc = payload["google_local"].get("search_console", {})
        print(f"   Maps views (7d):    {bp.get('maps_views_7d', 'unavailable')}")
        print(f"   Search clicks (7d): {sc.get('total_clicks_7d', 'unavailable')}")
        if payload["google_local"].get("stub"):
            print("   Stub mode: google")
    except Exception as e:
        msg = f"Google Local: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Write + send email ─────────────────────────────────────────────────────
    print("🧠 Writing email with Claude...")
    email_content = {"subject": "daily update", "body": "<p>Data collected — synthesis unavailable today.</p>", "signal_level": "quiet"}
    try:
        synth = ClaudeSynthesizer()
        email_content = synth.generate_email(payload)
        print(f"   Subject: {email_content.get('subject','')}")
        print(f"   Signal:  {email_content.get('signal_level','')}")
    except Exception as e:
        msg = f"Synthesis: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    print("📧 Sending email...")
    try:
        reporter = EmailReporter()
        reporter.send(email_content)
        recipient = os.environ.get("REPORT_RECIPIENT", "goodvibes@sandyneckprovisions.com")
        print(f"   Sent to: {recipient}")
    except Exception as e:
        msg = f"Email: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Done ───────────────────────────────────────────────────────────────────
    print("-" * 55)
    if payload["errors"]:
        print(f"⚠️  Completed with {len(payload['errors'])} issue(s):")
        for err in payload["errors"]:
            print(f"   • {err}")
        if any(e.startswith(("Shopify:", "Email:")) for e in payload["errors"]):
            sys.exit(1)
    else:
        print("✅ Daily analytics report delivered successfully.")


if __name__ == "__main__":
    main()
