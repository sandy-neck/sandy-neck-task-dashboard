import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pytz

ET = pytz.timezone("America/New_York")

CAT_COLORS = {
    "marketing": "#2d7dd2", "revenue": "#2d8a4e", "conversion": "#6f42c1",
    "email": "#e83e8c", "seo": "#fd7e14", "operations": "#6c757d",
}
EFFORT_LABELS = {
    "quick-win": "⚡ Quick Win", "this-week": "📅 This Week", "strategic": "🎯 Strategic",
}
IMPACT_ICONS = {"high": "🔴", "medium": "🟡", "low": "🟢"}
ALERT_STYLES = {
    "warning":     ("#fff3cd", "#ffc107", "#856404", "⚠️"),
    "opportunity": ("#d1e7dd", "#198754", "#0f5132", "✨"),
    "info":        ("#cff4fc", "#0dcaf0", "#055160", "ℹ️"),
}


class EmailReporter:
    def __init__(self):
        self.smtp_host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_user = os.environ["SMTP_USERNAME"]
        self.smtp_pass = os.environ["SMTP_PASSWORD"]
        self.recipient = os.environ.get("REPORT_RECIPIENT", "sandy@sandyneckprovisions.com")
        self.sender_name = os.environ.get("REPORT_SENDER_NAME", "Sandy Neck Analytics")

    def send(self, data: dict):
        html = self._render(data)
        now_et = datetime.now(ET)
        subject = f"Sandy Neck Daily Report — {data.get('date', now_et.strftime('%B %-d'))}"
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.sender_name} <{self.smtp_user}>"
        msg["To"] = self.recipient
        msg.attach(MIMEText(html, "html"))
        ctx = ssl.create_default_context()
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.ehlo()
            server.starttls(context=ctx)
            server.login(self.smtp_user, self.smtp_pass)
            server.sendmail(self.smtp_user, self.recipient, msg.as_string())

    def _render(self, data: dict) -> str:
        shopify = data.get("shopify", {})
        social = data.get("social", {})
        klaviyo = data.get("klaviyo", {})
        google = data.get("google_local", {})
        analysis = data.get("analysis", {})
        sales = shopify.get("sales", {})
        errors = data.get("errors", [])

        today_rev = sales.get("today_revenue", 0) or 0
        yesterday_rev = sales.get("yesterday_revenue", 0) or 0
        today_orders = sales.get("today_orders", 0) or 0
        yesterday_orders = sales.get("yesterday_orders", 0) or 0
        today_aov = sales.get("today_aov", 0) or 0
        rev_pct = ((today_rev - yesterday_rev) / yesterday_rev * 100) if yesterday_rev > 0 else 0
        conv = shopify.get("conversion_metrics", {})
        conv_rate = conv.get("conversion_rate")

        summary = analysis.get("summary", "Analytics report compiled.")
        headline = analysis.get("headline_metric", "")

        errors_block = ""
        if errors:
            errors_block = f'<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:12px 16px;margin:0 0 20px;font-size:13px;color:#856404;">⚠️ <strong>Data note:</strong> {"; ".join(errors)}</div>'

        return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"></head>
<body style="margin:0;padding:20px 0;background:#eef2f7;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;color:#1a1a2e;">
<div style="max-width:680px;margin:0 auto;">

  <div style="background:linear-gradient(135deg,#1a3a5c 0%,#2563a8 100%);border-radius:12px 12px 0 0;padding:36px 40px 28px;text-align:center;">
    <div style="font-size:10px;letter-spacing:4px;color:rgba(255,255,255,0.6);text-transform:uppercase;margin-bottom:10px;">Sandy Neck Provisions</div>
    <h1 style="color:#fff;margin:0 0 6px;font-size:24px;font-weight:700;">Daily Analytics Report</h1>
    <div style="color:rgba(255,255,255,0.8);font-size:14px;">{data.get("date","")}</div>
    {f'<div style="margin-top:18px;background:rgba(255,255,255,0.12);border-radius:20px;padding:8px 22px;display:inline-block;color:#fff;font-size:13px;">📌 {headline}</div>' if headline else ""}
  </div>

  <div style="background:#fff;padding:32px 40px;border-radius:0 0 12px 12px;box-shadow:0 4px 20px rgba(0,0,0,0.06);">
    {errors_block}

    <div style="background:#f0f6ff;border-left:4px solid #2563a8;border-radius:0 8px 8px 0;padding:16px 20px;margin-bottom:28px;">
      <p style="margin:0;color:#1a2e4a;font-size:15px;line-height:1.65;">{summary}</p>
    </div>

    <h2 style="{sh()}">Today's Numbers</h2>
    <table style="width:100%;border-collapse:separate;border-spacing:8px;margin:-8px -8px 24px;">
      <tr>
        <td style="{kc()}">{kb("Revenue", f"${today_rev:,.2f}", f"{'+' if rev_pct>=0 else ''}{rev_pct:.1f}% vs yesterday", "#2d8a4e" if rev_pct>=0 else "#c0392b")}</td>
        <td style="{kc()}">{kb("Orders", str(today_orders), f"{today_orders-yesterday_orders:+d} vs yesterday", "#2563a8")}</td>
        <td style="{kc()}">{kb("Avg Order", f"${today_aov:,.2f}" if today_orders else "—", "per order today", "#6f42c1")}</td>
        <td style="{kc()}">{kb("Conv. Rate", f"{float(conv_rate):.1f}%" if conv_rate else "—", "store sessions", "#fd7e14")}</td>
      </tr>
    </table>

    {self._alerts_block(analysis.get("alerts", []))}
    {self._insights_block(analysis.get("insights", []))}
    {self._recommendations_block(analysis.get("recommendations", []))}
    {self._klaviyo_block(klaviyo)}
    {self._top_products_block(shopify.get("top_products", []))}
    {self._referral_block(shopify.get("referral_sources", []))}
    {self._social_block(social)}
    {self._google_block(google)}
    {self._inventory_block(shopify.get("inventory_alerts", []))}
  </div>

  <div style="text-align:center;padding:20px;font-size:11px;color:#9aa5b4;">
    Sandy Neck Analytics Agent · {data.get("date","")} · Data current as of report time
  </div>
</div>
</body>
</html>"""

    def _alerts_block(self, alerts: list) -> str:
        if not alerts:
            return ""
        items = "".join(
            f'<div style="background:{bg};border:1px solid {brd};border-radius:6px;padding:10px 14px;margin-bottom:8px;font-size:13px;color:{txt};">{ico} {a.get("message","")}</div>'
            for a in alerts
            for bg, brd, txt, ico in [ALERT_STYLES.get(a.get("type","info"), ALERT_STYLES["info"])]
        )
        return f'<div style="margin-bottom:24px;">{items}</div>'

    def _insights_block(self, insights: list) -> str:
        if not insights:
            return ""
        items = "".join(
            f'<div style="border:1px solid #e9ecef;border-radius:8px;padding:14px 16px;margin-bottom:10px;"><div style="font-weight:600;margin-bottom:4px;">{IMPACT_ICONS.get(i.get("impact","medium"),"🔵")} {i.get("title","")}</div><div style="font-size:13px;color:#495057;line-height:1.55;">{i.get("detail","")}</div></div>'
            for i in insights
        )
        return f'<h2 style="{sh()}">Key Insights</h2>{items}'

    def _recommendations_block(self, recs: list) -> str:
        if not recs:
            return ""
        items = "".join(
            f'<div style="border-left:4px solid {CAT_COLORS.get(r.get("category","operations"),"#6c757d")};border-radius:0 8px 8px 0;background:#f8f9fa;padding:14px 18px;margin-bottom:10px;"><div style="font-size:15px;font-weight:700;margin-bottom:5px;">#{r.get("priority","")} {r.get("action","")}</div><div style="font-size:13px;color:#495057;margin-bottom:6px;">{r.get("rationale","")}</div><span style="font-size:11px;background:{CAT_COLORS.get(r.get("category","operations"),"#6c757d")}22;color:{CAT_COLORS.get(r.get("category","operations"),"#6c757d")};padding:2px 8px;border-radius:10px;margin-right:6px;">{r.get("category","")}</span><span style="font-size:11px;color:#6c757d;">{EFFORT_LABELS.get(r.get("effort","this-week"),"")}</span></div>'
            for r in sorted(recs, key=lambda x: x.get("priority", 99))
        )
        return f'<h2 style="{sh()}">Recommendations</h2>{items}'

    def _klaviyo_block(self, klaviyo: dict) -> str:
        if not klaviyo or not klaviyo.get("available"):
            return ""
        stub_badge = ' <span style="font-size:10px;background:#fff3cd;color:#856404;padding:1px 6px;border-radius:10px;">sample</span>' if klaviyo.get("stub") else ""
        revenue = klaviyo.get("revenue_7d")
        lists = klaviyo.get("list_growth", {})
        campaigns = klaviyo.get("campaigns", [])[:3]
        rows_html = "".join(
            f'<tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:9px 0;font-size:13px;">{c.get("name","")[:38]}</td><td style="padding:9px 0;font-size:13px;text-align:center;color:#e83e8c;">{f"{c["open_rate"]:.0%}" if c.get("open_rate") else "—"}</td><td style="padding:9px 0;font-size:13px;text-align:center;">{f"{c["click_rate"]:.0%}" if c.get("click_rate") else "—"}</td><td style="padding:9px 0;font-size:13px;text-align:right;color:#2d8a4e;">{f"${c["revenue"]:,.0f}" if c.get("revenue") else "—"}</td></tr>'
            for c in campaigns
        )
        lists_html = " &nbsp;·&nbsp; ".join(f"<b>{k}</b>: {v:,}" for k, v in lists.items())
        return f'<h2 style="{sh()}">Klaviyo Email Marketing{stub_badge}</h2><div style="background:#fef0f7;border-radius:8px;padding:14px 18px;margin-bottom:14px;"><span style="font-size:13px;color:#6c757d;">Email-attributed revenue (7d)</span><span style="font-size:22px;font-weight:700;color:#e83e8c;margin-left:12px;">{f"${revenue:,.2f}" if revenue else "—"}</span></div><table style="width:100%;border-collapse:collapse;margin-bottom:12px;"><tr style="border-bottom:2px solid #e9ecef;"><th style="{th()}">Campaign</th><th style="{th()} text-align:center;">Open</th><th style="{th()} text-align:center;">Click</th><th style="{th()} text-align:right;">Revenue</th></tr>{rows_html}</table><div style="font-size:12px;color:#6c757d;margin-bottom:24px;">{lists_html}</div>'

    def _top_products_block(self, products: list) -> str:
        if not products:
            return ""
        rows = "".join(
            f'<tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:9px 0;font-size:13px;">{i+1}. {p.get("product_title", p.get("title","—"))}</td><td style="padding:9px 0;font-size:13px;text-align:right;color:#2d8a4e;">{f"${float(p["gross_sales"]):,.2f}" if p.get("gross_sales") else "—"}</td><td style="padding:9px 0;font-size:13px;text-align:right;color:#6c757d;">{p.get("orders","—")} orders</td></tr>'
            for i, p in enumerate(products[:5])
        )
        return f'<h2 style="{sh()}">Top Products — Last 7 Days</h2><table style="width:100%;border-collapse:collapse;margin-bottom:24px;"><tr style="border-bottom:2px solid #e9ecef;"><th style="{th()}">Product</th><th style="{th()} text-align:right;">Revenue</th><th style="{th()} text-align:right;">Orders</th></tr>{rows}</table>'

    def _referral_block(self, referrals: list) -> str:
        if not referrals:
            return ""
        top = sorted(referrals, key=lambda r: float(r.get("total_sales") or 0), reverse=True)[:6]
        rows = "".join(
            f'<tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:8px 0;font-size:13px;">{r.get("order_referrer_source","—")} / {r.get("order_referrer_name","direct")}</td><td style="padding:8px 0;font-size:13px;text-align:right;color:#2d8a4e;">{f"${float(r["total_sales"]):,.2f}" if r.get("total_sales") else "—"}</td><td style="padding:8px 0;font-size:13px;text-align:right;color:#6c757d;">{r.get("orders","—")}</td></tr>'
            for r in top
        )
        return f'<h2 style="{sh()}">Traffic Attribution — Last 7 Days</h2><table style="width:100%;border-collapse:collapse;margin-bottom:24px;"><tr style="border-bottom:2px solid #e9ecef;"><th style="{th()}">Source / Channel</th><th style="{th()} text-align:right;">Revenue</th><th style="{th()} text-align:right;">Orders</th></tr>{rows}</table>'

    def _social_block(self, social: dict) -> str:
        platform_order = ["instagram", "tiktok", "facebook", "youtube"]
        available = [
            (k, social[k]) for k in platform_order
            if k in social and isinstance(social[k], dict) and social[k].get("available") is not False
        ]
        if not available:
            return ""
        cards = "".join(
            f'<div style="display:inline-block;width:calc(50% - 14px);margin:0 4px 12px;vertical-align:top;background:#f8f9fa;border:1px solid #e9ecef;border-radius:8px;padding:13px;"><div style="font-weight:600;font-size:14px;margin-bottom:7px;">{m.get("icon","📱")} {m.get("platform",k.title())}{" <span style='font-size:9px;background:#fff3cd;color:#856404;padding:1px 5px;border-radius:8px;'>sample</span>" if m.get("stub") else ""}</div><div style="font-size:12px;color:#495057;line-height:1.9;">👥 {f"{m["followers"]:,}" if m.get("followers") else "—"} followers {f"({m["follower_change_7d"]} this wk)" if m.get("follower_change_7d") else ""}<br>📈 Reach: {f"{m["reach_7d"]:,}" if m.get("reach_7d") else "—"}<br>💬 {m.get("engagement_rate","—")} engagement<br>🏆 {(m.get("top_post_7d") or "—")[:48]}</div></div>'
            for k, m in available
        )
        return f'<h2 style="{sh()}">Social Media — Last 7 Days</h2><div style="margin:0 -4px 24px;">{cards}</div>'

    def _google_block(self, google: dict) -> str:
        if not google or not google.get("available"):
            return ""
        stub_badge = ' <span style="font-size:10px;background:#fff3cd;color:#856404;padding:1px 6px;border-radius:10px;">sample</span>' if google.get("stub") else ""
        bp = google.get("business_profile", {})
        sc = google.get("search_console", {})
        keywords = bp.get("top_search_keywords", [])[:6]
        opportunities = sc.get("low_ctr_opportunities", [])[:4]

        kw_html = "".join(
            f'<span style="display:inline-block;background:#e8f0fe;border-radius:14px;padding:4px 10px;margin:3px;font-size:12px;color:#1a3a5c;">🔍 {k.get("keyword","")} <span style="color:#6c757d;">({k.get("impressions","")})</span></span>'
            for k in keywords
        )
        opp_rows = "".join(
            f'<tr style="border-bottom:1px solid #f0f0f0;"><td style="padding:8px 0;font-size:13px;">{o.get("query","")}</td><td style="padding:8px 0;font-size:13px;text-align:center;">{o.get("impressions","—")}</td><td style="padding:8px 0;font-size:13px;text-align:center;color:#fd7e14;">{o.get("ctr","—")}%</td><td style="padding:8px 0;font-size:13px;text-align:right;color:#6c757d;">#{o.get("position","—")}</td></tr>'
            for o in opportunities
        )
        opp_table = f'<p style="font-size:12px;color:#fd7e14;font-weight:600;margin:14px 0 6px;">⚡ Google Ads / SEO Opportunities (high impressions, low CTR)</p><table style="width:100%;border-collapse:collapse;"><tr style="border-bottom:2px solid #e9ecef;"><th style="{th()}">Query</th><th style="{th()} text-align:center;">Impressions</th><th style="{th()} text-align:center;">CTR</th><th style="{th()} text-align:right;">Position</th></tr>{opp_rows}</table>' if opp_rows else ""

        return f"""<h2 style="{sh()}">Google Local Presence{stub_badge}</h2>
        <table style="width:100%;border-collapse:separate;border-spacing:8px;margin:-8px -8px 16px;">
          <tr>
            <td style="{kc()}">{kb("Maps Views", f"{bp.get('maps_views_7d','—'):,}" if isinstance(bp.get('maps_views_7d'),int) else "—", "7-day total", "#4285f4")}</td>
            <td style="{kc()}">{kb("Directions", str(bp.get('direction_requests_7d','—')), "requested", "#34a853")}</td>
            <td style="{kc()}">{kb("Web Clicks", str(bp.get('website_clicks_7d','—')), "from Maps/Search", "#ea4335")}</td>
            <td style="{kc()}">{kb("Organic Clicks", str(sc.get('total_clicks_7d','—')), f"{sc.get('avg_ctr','—')}% avg CTR", "#fbbc04")}</td>
          </tr>
        </table>
        <div style="margin-bottom:12px;"><p style="font-size:12px;color:#6c757d;margin:0 0 8px;font-weight:600;">How people found the business (Google Maps searches)</p>{kw_html}</div>
        {opp_table}
        <div style="margin-bottom:24px;"></div>"""

    def _inventory_block(self, alerts: list) -> str:
        if not alerts:
            return ""
        badges = "".join(
            f'<span style="display:inline-block;background:#fff3cd;border:1px solid #ffc107;border-radius:6px;padding:4px 10px;margin:3px 4px;font-size:12px;">⚠️ {a.get("title","")}{" / " + a["variant"] if a.get("variant") else ""} ({a.get("inventory","?")} left)</span>'
            for a in alerts
        )
        return f'<h2 style="{sh()}">Low Inventory</h2><div style="margin-bottom:24px;">{badges}</div>'


def sh() -> str:
    return "font-size:11px;text-transform:uppercase;letter-spacing:2px;color:#6c757d;margin:28px 0 14px;font-weight:600;"

def kc() -> str:
    return "background:#f8f9fa;border:1px solid #e9ecef;border-radius:8px;padding:14px 10px;text-align:center;vertical-align:top;"

def kb(label: str, value: str, sub: str, color: str) -> str:
    return f'<div style="font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6c757d;margin-bottom:4px;">{label}</div><div style="font-size:20px;font-weight:700;">{value}</div><div style="font-size:11px;color:{color};margin-top:3px;">{sub}</div>'

def th() -> str:
    return "text-align:left;font-size:10px;text-transform:uppercase;letter-spacing:1px;color:#6c757d;padding-bottom:8px;"
