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
from datetime import datetime, date
import pytz

from shopify_client import ShopifyClient
from social_client import SocialClient
from klaviyo_client import KlaviyoClient
from google_local_client import GoogleLocalClient
from weather_client import WeatherClient, comparable_days, score_days_with_snp500
from expectations import assess
from targets import pace, load_prior_year_curve, save_prior_year_curve
from forecast import project_week, best_opportunity
from brain import Brain
from synthesizer import ClaudeSynthesizer
from email_report import EmailReporter, build_subject

ET = pytz.timezone("America/New_York")


def _fallback_log(payload: dict, report_date: str, content: dict) -> str:
    """
    Bare-bones journal entry, written when the model didn't return one.

    Deliberately records that it's a fallback: a thin entry that looks like a considered one would
    quietly corrupt the record the agent reads back later.
    """
    sales = payload.get("shopify", {}).get("sales", {})
    snp = (payload.get("snp500") or {}).get(report_date, {})
    exp = payload.get("expectation") or {}
    pacing = payload.get("pacing") or {}

    lines = [
        f"# {report_date}",
        "",
        "> Auto-generated fallback entry — the model returned an email but no journal block, so "
        "this records the facts only. No analysis was captured for this day.",
        "",
        "## Conditions",
        f"- SNP 500: {snp.get('score', 'unknown')} ({snp.get('rating', '?')}), "
        f"confidence {snp.get('confidence', '?')}",
        f"- {snp.get('headline', 'No conditions data.')}",
        "",
        "## What happened",
        f"- Revenue ${sales.get('revenue', 0):,.2f} across {sales.get('orders', 0)} orders "
        f"(AOV ${sales.get('aov', 0):,.2f})",
    ]
    for row in payload.get("channel_split", [])[:5]:
        lines.append(f"  - {row['channel']}: ${row['revenue']:,.2f} ({row['share_pct']}%)")
    if exp.get("available"):
        lines.append(f"- Expected ~${exp['expected_revenue']:,} → {exp['pct_of_expected']}% "
                     f"of that, {exp['verdict']}")
    if pacing.get("available"):
        lines.append(f"- YTD ${pacing['ytd_revenue']:,.0f} of ${pacing['target']:,} "
                     f"({pacing['status']}), projecting ${pacing['projected_year_end']:,}")

    lines += ["", "## Open threads",
              "- No analysis captured for this day; re-read the numbers if this date matters later."]
    if payload.get("errors"):
        lines += ["", "## Data gaps"] + [f"- {e}" for e in payload["errors"]]
    if content.get("subject"):
        lines += ["", f"Email that went out: \"{content['subject']}\""]
    return "\n".join(lines)


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

        # Pace against the annual target using prior year's shape. The curve is cached because
        # last year's numbers don't change — no point re-pulling a full year every morning.
        curve = load_prior_year_curve()
        if curve is None:
            prior = shopify.get_daily_revenue_for_year(now.year - 1)
            if prior:
                curve = save_prior_year_curve(now.year - 1, prior)
                print(f"   Built {now.year - 1} seasonality curve "
                      f"(${curve['total_revenue']:,.0f} across {len(prior)} days)")
        payload["pacing"] = pace(shopify.get_ytd_revenue(), now.date(), curve=curve)

        print(f"   Reporting on: {report_date}")
        print(f"   Revenue:      ${sales.get('revenue', 0):,.2f} / {sales.get('orders', 0)} orders")
        for row in payload["channel_split"][:4]:
            print(f"     {row['channel']:<18} ${row['revenue']:>9,.2f}  ({row['share_pct']}%)")
        urgent = [s for s in payload["reorder_signals"] if s["urgency"] in ("critical", "out of stock")]
        print(f"   Reorder flags: {len(payload['reorder_signals'])} ({len(urgent)} urgent)")
        pacing = payload.get("pacing", {})
        if pacing.get("available"):
            print(f"   YTD:          ${pacing['ytd_revenue']:,.0f} of ${pacing['target']:,} "
                  f"({pacing['pct_of_target']}%) — {pacing['status']}")
            print(f"   Season:       {pacing['phase']['phase']}, "
                  f"{pacing['phase']['days_remaining']} days left | "
                  f"projecting ${pacing['projected_year_end']:,}")
            print(f"   Pace basis:   {pacing['basis']}")
        print(f"   Source:       {sales.get('source')}")
        if shopify.ql_errors:
            # Loud on purpose: a silent fallback to raw orders costs the channel split,
            # reorder signals and real pacing, and looks like everything is fine.
            print(f"   ShopifyQL FAILED {len(shopify.ql_errors)}x — falling back:", file=sys.stderr)
            for err in shopify.ql_errors[:3]:
                print(f"      {err}", file=sys.stderr)
            payload["errors"].append(f"ShopifyQL unavailable ({len(shopify.ql_errors)} queries)")
    except Exception as e:
        msg = f"Shopify: {e}"
        print(f"   ERROR: {msg}", file=sys.stderr)
        payload["errors"].append(msg)

    # ── Weather & tides ───────────────────────────────────────────────────────
    print("Weather, tides & SNP 500...")
    try:
        payload["weather"] = WeatherClient().get_context()
        days = payload["weather"].get("days", {})

        # One environmental model, two consumers: the customer-facing score is also the
        # denominator that makes "was yesterday actually good?" answerable.
        snp = score_days_with_snp500(payload["weather"],
                                     bugs=os.environ.get("BUG_LEVEL"),
                                     access=os.environ.get("BEACH_ACCESS"))
        payload["snp500"] = snp
        for day, result in snp.items():
            if day in days and result.get("score") is not None:
                days[day]["beach_score"] = result["score"]
                days[day]["beach_label"] = result["rating"]

        if report_date and report_date in snp:
            today = snp[report_date]
            print(f"   {report_date}: SNP 500 = {today['score']} ({today['rating']}), "
                  f"confidence {today['confidence']}")
            print(f"      {today['headline']}")
            payload["comparable_days"] = comparable_days(days, report_date)
            print(f"   Comparable days: {len(payload['comparable_days'])}")

            # The number that makes revenue mean something.
            revenue = payload.get("shopify", {}).get("sales", {}).get("revenue")
            payload["expectation"] = assess(revenue, today["score"],
                                            day=date.fromisoformat(report_date),
                                            curve=load_prior_year_curve())
            if payload["expectation"].get("available"):
                exp = payload["expectation"]
                print(f"   Expected ~${exp['expected_revenue']:,} → actual "
                      f"${exp['actual_revenue']:,.2f} ({exp['pct_of_expected']}%) "
                      f"— {exp['verdict']}")

        # Week ahead: what conditions should deliver vs what the target actually needs.
        pacing = payload.get("pacing", {})
        payload["forecast"] = project_week(
            snp, pacing.get("ytd_revenue"), now.date(),
            curve=load_prior_year_curve(),
        )
        fc = payload["forecast"]
        if fc.get("available"):
            print(f"   Week ahead: {len(fc['days'])} days scored, "
                  f"expecting ${fc['expected_week_total']:,}")
            if fc.get("required_available"):
                print(f"      target needs ${fc['required_week_total']:,} "
                      f"— {fc['verdict']}")
                opportunity = best_opportunity(fc)
                if opportunity:
                    print(f"      best lever: {opportunity['weekday']} {opportunity['date']} "
                          f"(SNP {opportunity['snp500']}, gap ${opportunity['gap']:,})")
        if not payload["weather"].get("tides", {}).get("available"):
            print("   Tides: not configured (set NOAA_TIDE_STATION) — SNP 500 tide factor inactive")
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
            value = payload[key]
            if isinstance(value, dict) and "stub" in value:
                stubbed = value["stub"]
            elif isinstance(value, dict):
                # Social is a dict *of* platforms, so the flag lives one level down.
                stubbed = any(v.get("stub") for v in value.values() if isinstance(v, dict))
            else:
                stubbed = False
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
            "events": brain.events(around=report_date),
        }
        print(f"   context {len(brain_context['context']):,} chars | "
              f"{len(brain_context['recent_logs'])} recent logs | "
              f"{len(brain_context['open_threads'])} open threads | "
              f"{len(brain_context['open_projects'])} open projects"
              f"{' | inbox has notes' if brain_context['inbox'] else ''}"
              f"{' | events logged' if brain_context['events'] else ''}")
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
    # A day with no entry is a permanent hole in the record — the numbers can be re-queried, but
    # what the conditions were and what was concluded cannot. If the model didn't return a log
    # block, write the facts anyway.
    if report_date and not content.get("daily_log"):
        print("   No journal returned — writing a minimal entry from the data", file=sys.stderr)
        content["daily_log"] = _fallback_log(payload, report_date, content)

    if content.get("daily_log") and report_date:
        try:
            path = brain.write_daily_log(report_date, content["daily_log"])
            print(f"   Journal: {path.relative_to(path.parent.parent.parent)}")
            if content.get("learned"):
                brain.append_learned(content["learned"])
                print("   Appended to LEARNED.md")
            if brain_context.get("inbox"):
                brain.mark_inbox_processed(report_date)
                print("   Inbox: notes marked processed")
        except Exception as e:
            msg = f"Brain write: {e}"
            print(f"   ERROR: {msg}", file=sys.stderr)
            payload["errors"].append(msg)

    # ── Send ──────────────────────────────────────────────────────────────────
    print("Sending...")
    try:
        content["subject"] = build_subject(report_date, payload, content.get("subject", ""))
        print(f"   Subject: {content['subject']}")
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
