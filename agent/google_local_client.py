"""
Google local presence analytics: Business Profile + Search Console.

Answers: How are people finding Sandy Neck Provisions online?
- What searches lead to the Maps listing (branded vs. discovery)
- Direction requests, website clicks, phone calls from Maps
- Organic search queries, impressions, CTR, position (Search Console)
- Local SEO and Google Ads keyword opportunities

Authentication: Google OAuth 2.0 service account (see AGENT_SETUP.md).
Runs in stub mode until GOOGLE_SERVICE_ACCOUNT_JSON is set.
"""
import os
import json
from datetime import datetime, timedelta, timezone

STUB_MODE = os.environ.get("GOOGLE_STUB_MODE", "true").lower() != "false"

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False


class GoogleLocalClient:
    def __init__(self):
        self.location_name = os.environ.get(
            "GOOGLE_BUSINESS_LOCATION", ""
        )  # e.g. "accounts/12345/locations/67890"
        self.site_url = os.environ.get(
            "SEARCH_CONSOLE_SITE_URL", "https://sandyneckprovisions.com/"
        )
        self._creds = None

    def get_all_metrics(self) -> dict:
        if STUB_MODE or not GOOGLE_LIBS_AVAILABLE or not os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
            return self._stub_metrics()
        try:
            self._init_credentials()
            return {
                "business_profile": self._get_business_profile_metrics(),
                "search_console": self._get_search_console_metrics(),
                "available": True,
            }
        except Exception as e:
            return {"available": False, "error": str(e)}

    # ── Google Business Profile ───────────────────────────────────────────────

    def _get_business_profile_metrics(self) -> dict:
        if not self.location_name:
            return {"error": "GOOGLE_BUSINESS_LOCATION not set"}

        service = build(
            "businessprofileperformance",
            "v1",
            credentials=self._creds,
            discoveryServiceUrl=(
                "https://businessprofileperformance.googleapis.com/$discovery/rest"
                "?version=v1"
            ),
        )
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)

        result = service.locations().getDailyMetricsTimeSeries(
            name=self.location_name,
            dailyMetric=[
                "BUSINESS_IMPRESSIONS_DESKTOP_MAPS",
                "BUSINESS_IMPRESSIONS_MOBILE_MAPS",
                "BUSINESS_IMPRESSIONS_DESKTOP_SEARCH",
                "BUSINESS_IMPRESSIONS_MOBILE_SEARCH",
                "WEBSITE_CLICKS",
                "CALL_CLICKS",
                "BUSINESS_DIRECTION_REQUESTS",
            ],
            **{
                "dailyRange.startDate.year": week_ago.year,
                "dailyRange.startDate.month": week_ago.month,
                "dailyRange.startDate.day": week_ago.day,
                "dailyRange.endDate.year": now.year,
                "dailyRange.endDate.month": now.month,
                "dailyRange.endDate.day": now.day,
            },
        ).execute()

        totals = {}
        for series in result.get("multiDailyMetricTimeSeries", []):
            metric_name = series.get("dailyMetric", "")
            total = sum(
                int(p.get("value", 0))
                for p in series.get("timeSeries", {}).get("datedValues", [])
            )
            totals[metric_name] = total

        maps_views = (
            totals.get("BUSINESS_IMPRESSIONS_DESKTOP_MAPS", 0)
            + totals.get("BUSINESS_IMPRESSIONS_MOBILE_MAPS", 0)
        )
        search_views = (
            totals.get("BUSINESS_IMPRESSIONS_DESKTOP_SEARCH", 0)
            + totals.get("BUSINESS_IMPRESSIONS_MOBILE_SEARCH", 0)
        )

        # Get search keywords that led to the listing
        search_terms = self._get_business_search_keywords(service)

        return {
            "maps_views_7d": maps_views,
            "search_views_7d": search_views,
            "website_clicks_7d": totals.get("WEBSITE_CLICKS", 0),
            "direction_requests_7d": totals.get("BUSINESS_DIRECTION_REQUESTS", 0),
            "phone_calls_7d": totals.get("CALL_CLICKS", 0),
            "top_search_keywords": search_terms,
        }

    def _get_business_search_keywords(self, service) -> list:
        now = datetime.now(timezone.utc)
        week_ago = now - timedelta(days=7)
        try:
            result = service.locations().searchkeywords().impressions().monthly().list(
                parent=self.location_name,
                **{
                    "monthlyRange.startMonth.year": week_ago.year,
                    "monthlyRange.startMonth.month": week_ago.month,
                    "monthlyRange.endMonth.year": now.year,
                    "monthlyRange.endMonth.month": now.month,
                },
            ).execute()
            return [
                {
                    "keyword": item.get("searchKeyword", ""),
                    "impressions": sum(
                        i.get("count", 0) for i in item.get("insightsValue", {}).get("value", [])
                    ),
                }
                for item in result.get("searchKeywordsCounts", [])[:10]
            ]
        except Exception:
            return []

    # ── Google Search Console ─────────────────────────────────────────────────

    def _get_search_console_metrics(self) -> dict:
        service = build("searchconsole", "v1", credentials=self._creds)
        now = datetime.now(timezone.utc)
        today = now.strftime("%Y-%m-%d")
        week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d")

        # Top queries overall
        queries_resp = service.searchanalytics().query(
            siteUrl=self.site_url,
            body={
                "startDate": week_ago,
                "endDate": today,
                "dimensions": ["query"],
                "rowLimit": 20,
                "orderBy": [{"fieldName": "impressions", "sortOrder": "DESCENDING"}],
            },
        ).execute()

        # Top queries with low CTR (high-opportunity terms for SEO/ads)
        rows = queries_resp.get("rows", [])
        top_queries = [
            {
                "query": r["keys"][0],
                "impressions": r.get("impressions", 0),
                "clicks": r.get("clicks", 0),
                "ctr": round(r.get("ctr", 0) * 100, 1),
                "position": round(r.get("position", 0), 1),
            }
            for r in rows
        ]

        # Identify low-CTR, high-impression opportunities (good for ads/SEO)
        opportunities = [
            q for q in top_queries
            if q["impressions"] > 50 and q["ctr"] < 5.0 and q["position"] > 5
        ]

        # Summary totals
        total_clicks = sum(r.get("clicks", 0) for r in rows)
        total_impressions = sum(r.get("impressions", 0) for r in rows)
        avg_ctr = total_clicks / total_impressions * 100 if total_impressions else 0

        return {
            "total_clicks_7d": total_clicks,
            "total_impressions_7d": total_impressions,
            "avg_ctr": round(avg_ctr, 1),
            "top_queries": top_queries[:10],
            "low_ctr_opportunities": opportunities[:5],
        }

    # ── Credentials ───────────────────────────────────────────────────────────

    def _init_credentials(self):
        if self._creds:
            return
        json_str = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        info = json.loads(json_str)
        scopes = [
            "https://www.googleapis.com/auth/business.manage",
            "https://www.googleapis.com/auth/webmasters.readonly",
        ]
        self._creds = service_account.Credentials.from_service_account_info(info, scopes=scopes)

    # ── Stub data ─────────────────────────────────────────────────────────────

    def _stub_metrics(self) -> dict:
        return {
            "available": True,
            "stub": True,
            "business_profile": {
                "maps_views_7d": 842,
                "search_views_7d": 1204,
                "website_clicks_7d": 183,
                "direction_requests_7d": 67,
                "phone_calls_7d": 12,
                "top_search_keywords": [
                    {"keyword": "sandy neck provisions", "impressions": 310},
                    {"keyword": "seafood east sandwich ma", "impressions": 187},
                    {"keyword": "propane barnstable county", "impressions": 142},
                    {"keyword": "cape cod lobster delivery", "impressions": 98},
                    {"keyword": "provisions store sandwich", "impressions": 74},
                    {"keyword": "local seafood cape cod", "impressions": 61},
                ],
            },
            "search_console": {
                "total_clicks_7d": 412,
                "total_impressions_7d": 6840,
                "avg_ctr": 6.0,
                "top_queries": [
                    {"query": "sandy neck provisions", "impressions": 890, "clicks": 210, "ctr": 23.6, "position": 1.2},
                    {"query": "cape cod seafood delivery", "impressions": 620, "clicks": 28, "ctr": 4.5, "position": 8.3},
                    {"query": "east sandwich provisions", "impressions": 410, "clicks": 52, "ctr": 12.7, "position": 3.1},
                    {"query": "lobster roll cape cod", "impressions": 380, "clicks": 11, "ctr": 2.9, "position": 11.4},
                    {"query": "propane delivery barnstable", "impressions": 310, "clicks": 8, "ctr": 2.6, "position": 14.2},
                    {"query": "fresh clams cape cod", "impressions": 270, "clicks": 19, "ctr": 7.0, "position": 6.7},
                    {"query": "cape cod provisions store", "impressions": 240, "clicks": 31, "ctr": 12.9, "position": 4.8},
                    {"query": "seafood east sandwich", "impressions": 180, "clicks": 24, "ctr": 13.3, "position": 2.9},
                ],
                "low_ctr_opportunities": [
                    {"query": "cape cod seafood delivery", "impressions": 620, "clicks": 28, "ctr": 4.5, "position": 8.3},
                    {"query": "lobster roll cape cod", "impressions": 380, "clicks": 11, "ctr": 2.9, "position": 11.4},
                    {"query": "propane delivery barnstable", "impressions": 310, "clicks": 8, "ctr": 2.6, "position": 14.2},
                    {"query": "fresh oysters cape cod", "impressions": 220, "clicks": 7, "ctr": 3.2, "position": 9.8},
                ],
            },
        }
