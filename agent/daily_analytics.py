#!/usr/bin/env python3
"""
Sandy Neck Provisions — Daily Analytics Agent
Runs via GitHub Actions cron at 7 AM ET.

Reports on the last complete sales day, analysing in-store and online separately, weather-adjusting
every comparison, and keeping a running journal in brain/ so each run starts from what the previous
ones learned.
"""
import os
import sys
from datetime import datetime
import pytz

from shopify_client import ShopifyClient
from social_client import SocialClient
from klaviyo_client import KlaviyoClient
from google_local_client import GoogleLocalClient
from weather_client import WeatherClient, comparable_days
from brain import Brain
from synthesizer import ClaudeSynthesizer
from email_report import EmailReporter

ET = pytz.timezone("America/New_York")


def main():
    now = datetime.now(ET)
    run_date = now.strftime("%A, %B %-d, %Y")
    print(f"[{now.strftime('%I:%M %p ET')}] Sandy Neck Analytics — {run_date}")
    print("-" * 60)

    payload = {"date": run_date, "shopify": {}, "social": {}, "klaviyo": {},
               "google_local": {}, "weather": {}, "errors": []}
    report_date = None

    # ── Shopify ───────────────────────────────────────────────────────────────
    print("Shopify...")
    try:
        shopify = ShopifyClient()
        sales = shopify.get_sales_summary()
        report_date = sales.get("report_date")

        payload["shopify"] = {
            "sales": sales,
            "referral_sources": shopify.get_referral_sources(),
            "customer_insights": shopify.get_customer_insights(),
            "conversion_metrics": shopify.get_conversion_metrics(),
        }
        payload["channel_split"] = shopify.get_channel_split()
        payload["channel_day"] = shopify.get_channel_day(report_date) if report_date else []
        payload["instore_products"] = shopify.get_top_products_by_channel("Point of Sale")
        payload["online_products"] = shopify.get_top_products_by_channel("Online Store")
        payload["tiktok_products"] = shopify.get_top_products_by_channel("TikTok")
        payload["season"] = shopify.get_season_trend()
        payload["reorder_signals"] = shopify.get_reorder_signals()

        print(f"   Reporting on: {report_date}")
        print(f"   Revenue:      ${sales.get('revenue', 0):,.2f} / {sales.get('orders', 0)} orders")
        for row in payload["channel_split"][:4]:
            print(f"     {row['channel']:<18} ${row['revenue']:>9,.2f}  ({row['share_pct']}%)")
        urgent = [s for s in payload["reorder_signals"] if s["urgency"] in ("critical", "out of stock")]
        print(f"   Reorder flags: {len(payload['reorder_signals'])} ({len(urgent)} urgent)")
        print(f"   Source:       {sales.get('source')}")
    except Exception as e:
        msg = f"Shopify: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Weather & tides ───────────────────────────────────────────────────────
    print("Weather & tides...")
    try:
        payload["weather"] = WeatherClient().get_context()
        days = payload["weather"].get("days", {})
        if report_date and report_date in days:
            day = days[report_date]
            print(f"   {report_date}: {day['conditions']}, feels {day['feels_like_f']}°F "
                  f"— {day['beach_label']} ({day['beach_score']}/100)")
            payload["comparable_days"] = comparable_days(days, report_date)
            print(f"   Comparable days found: {len(payload['comparable_days'])}")
        if not payload["weather"].get("tides", {}).get("available"):
            print("   Tides: not configured (set NOAA_TIDE_STATION)")
    except Exception as e:
        msg = f"Weather: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Optional sources ──────────────────────────────────────────────────────
    for label, key, fetch in [
        ("Social", "social", lambda: SocialClient().get_all_metrics()),
        ("Klaviyo", "klaviyo", lambda: KlaviyoClient().get_metrics()),
        ("Google local", "google_local", lambda: GoogleLocalClient().get_all_metrics()),
    ]:
        print(f"{label}...")
        try:
            payload[key] = fetch()
            stubbed = (
                payload[key].get("stub")
                if isinstance(payload[key], dict)
                else any(v.get("stub") for v in payload[key].values() if isinstance(v, dict))
            )
            print(f"   {'sample data (not connected)' if stubbed else 'live'}")
        except Exception as e:
            msg = f"{label}: {e}"
            print(f"   ERROR: {msg}", file=sys.stderr)
            payload["errors"].append(msg)

    # ── Brain ─────────────────────────────────────────────────────────────────
    print("Reading brain...")
    brain = Brain()
    brain_context = {}
    try:
        brain_context = {
            "context": brain.context(),
            "inbox": brain.inbox(),
            "learned": brain.learned(),
            "recent_logs": brain.recent_logs(days=5),
            "open_threads": brain.open_threads(),
            "open_projects": brain.open_projects(),
        }
        print(f"   context {len(brain_context['context']):,} chars | "
              f"{len(brain_context['recent_logs'])} recent logs | "
              f"{len(brain_context['open_threads'])} open threads | "
              f"{len(brain_context['open_projects'])} open projects"
              f"{' | inbox has notes' if brain_context['inbox'] else ''}")
        for project in brain_context["open_projects"]:
            print(f"     - {project['name']}: {project['status']}")
    except Exception as e:
        msg = f"Brain read: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Write ─────────────────────────────────────────────────────────────────
    print("Writing...")
    content = {"subject": "daily update", "signal_level": "quiet",
               "body": "<p>Data collected — synthesis unavailable today.</p>",
               "daily_log": "", "learned": ""}
    try:
        content = ClaudeSynthesizer().generate(payload, brain_context)
        print(f"   Subject: {content.get('subject')}")
        print(f"   Signal:  {content.get('signal_level')}")
    except Exception as e:
        msg = f"Synthesis: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Persist to brain ──────────────────────────────────────────────────────
    if content.get("daily_log") and report_date:
        try:
            path = brain.write_daily_log(report_date, content["daily_log"])
            print(f"   Journal: {path.relative_to(path.parent.parent.parent)}")
            if content.get("learned"):
                brain.append_learned(content["learned"])
                print("   Appended to LEARNED.md")
            if brain_context.get("inbox"):
                notes = [l for l in brain_context["inbox"].splitlines() if l.strip().startswith("-")]
                brain.mark_inbox_processed(notes, report_date)
                print(f"   Inbox: {len(notes)} note(s) marked processed")
        except Exception as e:
            msg = f"Brain write: {e}"
            print(f"   ERROR: {msg}", file=sys.stderr)
            payload["errors"].append(msg)

    # ── Send ──────────────────────────────────────────────────────────────────
    print("Sending...")
    try:
        EmailReporter().send(content)
        print(f"   Sent to: {os.environ.get('REPORT_RECIPIENT') or 'goodvibes@sandyneckprovisions.com'}")
    except Exception as e:
        msg = f"Email: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    print("-" * 60)
    if payload["errors"]:
        print(f"Completed with {len(payload['errors'])} issue(s):")
        for err in payload["errors"]:
            print(f"   - {err}")
        if any(e.startswith(("Shopify:", "Email:")) for e in payload["errors"]):
            sys.exit(1)
    else:
        print("Delivered.")


if __name__ == "__main__":
    main()
