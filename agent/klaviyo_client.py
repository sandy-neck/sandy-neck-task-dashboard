"""
Klaviyo email marketing analytics client.

Pulls campaign performance, flow metrics, and list growth for the reporting period.
Requires KLAVIYO_PRIVATE_KEY environment variable (Settings → API Keys in Klaviyo).
"""
import os
import requests
from datetime import datetime, timedelta, timezone

STUB_MODE = os.environ.get("KLAVIYO_STUB_MODE", "true").lower() != "false"
BASE_URL = "https://a.klaviyo.com/api"
API_REVISION = "2024-10-15"


class KlaviyoClient:
    def __init__(self):
        self.key = os.environ.get("KLAVIYO_PRIVATE_KEY", "")
        self.headers = {
            "Authorization": f"Klaviyo-API-Key {self.key}",
            "revision": API_REVISION,
            "Accept": "application/json",
        }

    def get_metrics(self) -> dict:
        if STUB_MODE or not self.key:
            return self._stub_metrics()
        try:
            return {
                "campaigns": self._get_recent_campaign_stats(),
                "list_growth": self._get_list_growth(),
                "revenue_7d": self._get_attributed_revenue(),
                "available": True,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    def _get_recent_campaign_stats(self) -> list:
        resp = requests.get(
            f"{BASE_URL}/campaigns/",
            headers=self.headers,
            params={
                "filter": "equals(messages.channel,'email')",
                "sort": "-scheduled_at",
                "page[size]": 5,
            },
            timeout=15,
        )
        resp.raise_for_status()
        campaigns = resp.json().get("data", [])

        results = []
        for campaign in campaigns[:5]:
            cid = campaign["id"]
            attrs = campaign.get("attributes", {})

            # Get send job metrics for this campaign
            metrics_resp = requests.get(
                f"{BASE_URL}/campaign-send-jobs/{cid}/",
                headers=self.headers,
                timeout=15,
            )
            send_attrs = {}
            if metrics_resp.ok:
                send_attrs = metrics_resp.json().get("data", {}).get("attributes", {})

            results.append({
                "name": attrs.get("name", ""),
                "subject": attrs.get("audiences", {}).get("included", [""])[0] if attrs.get("audiences") else "",
                "sent_at": attrs.get("scheduled_at", ""),
                "status": attrs.get("status", ""),
                "open_rate": send_attrs.get("open_rate"),
                "click_rate": send_attrs.get("click_rate"),
                "revenue": send_attrs.get("attributed_revenue"),
            })
        return results

    def _get_list_growth(self) -> dict:
        resp = requests.get(
            f"{BASE_URL}/lists/",
            headers=self.headers,
            params={"page[size]": 5},
            timeout=15,
        )
        resp.raise_for_status()
        lists = resp.json().get("data", [])

        week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")
        growth = {}
        for lst in lists[:3]:
            lid = lst["id"]
            name = lst.get("attributes", {}).get("name", lid)
            count_resp = requests.get(
                f"{BASE_URL}/lists/{lid}/",
                headers=self.headers,
                timeout=15,
            )
            if count_resp.ok:
                profile_count = count_resp.json().get("data", {}).get("attributes", {}).get("profile_count", 0)
                growth[name] = profile_count
        return growth

    def _get_attributed_revenue(self) -> float:
        # Fetch attributed revenue metric for last 7 days via Klaviyo metrics API
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        # First get the "Placed Order" metric ID
        metrics_resp = requests.get(
            f"{BASE_URL}/metrics/",
            headers=self.headers,
            timeout=15,
        )
        if not metrics_resp.ok:
            return None

        metrics = metrics_resp.json().get("data", [])
        placed_order = next(
            (m for m in metrics if "Placed Order" in m.get("attributes", {}).get("name", "")),
            None,
        )
        if not placed_order:
            return None

        agg_resp = requests.post(
            f"{BASE_URL}/metric-aggregates/",
            headers={**self.headers, "Content-Type": "application/json"},
            json={
                "data": {
                    "type": "metric-aggregate",
                    "attributes": {
                        "metric_id": placed_order["id"],
                        "interval": "day",
                        "page_size": 7,
                        "measurements": ["sum_value"],
                        "filter": [
                            f"greater-or-equal(datetime,{week_ago.strftime('%Y-%m-%dT00:00:00')})",
                            f"less-than(datetime,{now.strftime('%Y-%m-%dT00:00:00')})",
                        ],
                    },
                }
            },
            timeout=15,
        )
        if not agg_resp.ok:
            return None

        results = agg_resp.json().get("data", {}).get("attributes", {}).get("results", [])
        return sum(r.get("measurements", {}).get("sum_value", [0])[0] or 0 for r in results)

    def _stub_metrics(self) -> dict:
        return {
            "available": True,
            "stub": True,
            "campaigns": [
                {
                    "name": "June Newsletter — Summer Seafood Preview",
                    "sent_at": "2026-06-16",
                    "status": "sent",
                    "open_rate": 0.42,
                    "click_rate": 0.08,
                    "revenue": 1240.50,
                },
                {
                    "name": "Flash Sale: Lobster Rolls",
                    "sent_at": "2026-06-10",
                    "status": "sent",
                    "open_rate": 0.51,
                    "click_rate": 0.14,
                    "revenue": 3820.00,
                },
                {
                    "name": "Welcome Series — New Subscriber",
                    "sent_at": None,
                    "status": "flow",
                    "open_rate": 0.67,
                    "click_rate": 0.22,
                    "revenue": 890.00,
                },
            ],
            "list_growth": {
                "Newsletter Subscribers": 2847,
                "VIP Customers": 412,
                "Summer 2026 Interest": 189,
            },
            "revenue_7d": 5950.50,
            "open_rate_avg": 0.45,
            "click_rate_avg": 0.11,
        }
