"""
Shopify data client for the daily analytics agent.

Uses ShopifyQL (primary) with Admin GraphQL fallback for each metric.
ShopifyQL syntax confirmed against live store: TIMESERIES / GROUP BY / SINCE / UNTIL.
"""
import os
import requests
from datetime import datetime, timedelta
import pytz

API_VERSION = "2025-04"
ET = pytz.timezone("America/New_York")


class ShopifyClient:
    def __init__(self):
        self.shop = os.environ["SHOPIFY_SHOP_DOMAIN"]
        self.token = os.environ["SHOPIFY_ACCESS_TOKEN"]
        self.endpoint = f"https://{self.shop}/admin/api/{API_VERSION}/graphql.json"
        self.session = requests.Session()
        self.session.headers.update({
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
        })

    # ── Low-level helpers ──────────────────────────────────────────────────────

    def _gql(self, query: str, variables: dict = None) -> dict:
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        resp = self.session.post(self.endpoint, json=payload, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        if "errors" in result:
            raise ValueError(f"GraphQL error: {result['errors'][0]['message']}")
        return result["data"]

    def _shopifyql(self, query: str) -> list:
        """Run a ShopifyQL query and return list of dicts (one per row)."""
        gql = """
        query RunShopifyQL($q: String!) {
          shopifyqlQuery(query: $q) {
            parseErrors { code message }
            tableData {
              unformattedData
              columns { name dataType }
            }
          }
        }
        """
        data = self._gql(gql, {"q": query})
        result = data["shopifyqlQuery"]
        if result.get("parseErrors"):
            raise ValueError(f"ShopifyQL: {result['parseErrors'][0]['message']}")
        table = result.get("tableData")
        if not table or not table.get("unformattedData"):
            return []
        cols = [c["name"] for c in table["columns"]]
        return [dict(zip(cols, row)) for row in table["unformattedData"]]

    # ── Sales & revenue ────────────────────────────────────────────────────────

    def get_sales_summary(self) -> dict:
        """Daily revenue and order counts for last 7 days, with today highlighted."""
        now_et = datetime.now(ET)
        today_str = now_et.strftime("%Y-%m-%d")
        yesterday_str = (now_et - timedelta(days=1)).strftime("%Y-%m-%d")

        try:
            rows = self._shopifyql(
                "FROM sales "
                "SHOW orders, gross_sales, net_sales, average_order_value "
                "TIMESERIES day SINCE -7d UNTIL today"
            )
            today_row = next((r for r in rows if r.get("day", "").startswith(today_str)), {})
            yesterday_row = next((r for r in rows if r.get("day", "").startswith(yesterday_str)), {})
            return {
                "today_revenue": float(today_row.get("gross_sales") or 0),
                "today_net_revenue": float(today_row.get("net_sales") or 0),
                "today_orders": int(today_row.get("orders") or 0),
                "today_aov": float(today_row.get("average_order_value") or 0),
                "yesterday_revenue": float(yesterday_row.get("gross_sales") or 0),
                "yesterday_orders": int(yesterday_row.get("orders") or 0),
                "weekly_trend": rows,
                "source": "shopifyql",
            }
        except Exception:
            return self._sales_summary_fallback()

    def _sales_summary_fallback(self) -> dict:
        now_et = datetime.now(ET)
        today_start = now_et.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)

        gql = """
        query($q: String!) {
          orders(first: 250, query: $q, sortKey: CREATED_AT, reverse: true) {
            edges {
              node {
                createdAt
                totalPriceSet { shopMoney { amount } }
              }
            }
          }
        }
        """
        q = f"created_at:>={yesterday_start.isoformat()}"
        data = self._gql(gql, {"q": q})
        orders = [e["node"] for e in data["orders"]["edges"]]

        today_orders = [o for o in orders if o["createdAt"] >= today_start.isoformat()]
        yesterday_orders = [
            o for o in orders
            if yesterday_start.isoformat() <= o["createdAt"] < today_start.isoformat()
        ]

        def revenue(ol):
            return sum(float(o["totalPriceSet"]["shopMoney"]["amount"]) for o in ol)

        return {
            "today_revenue": revenue(today_orders),
            "today_net_revenue": revenue(today_orders),
            "today_orders": len(today_orders),
            "today_aov": revenue(today_orders) / len(today_orders) if today_orders else 0,
            "yesterday_revenue": revenue(yesterday_orders),
            "yesterday_orders": len(yesterday_orders),
            "weekly_trend": [],
            "source": "graphql_fallback",
        }

    # ── Conversion funnel ──────────────────────────────────────────────────────

    def get_conversion_metrics(self) -> dict:
        """Full conversion funnel: sessions → cart → checkout → purchased."""
        try:
            rows = self._shopifyql(
                "FROM sessions "
                "SHOW sessions, sessions_with_cart_additions, "
                "sessions_that_reached_checkout, sessions_that_completed_checkout, "
                "conversion_rate "
                "TIMESERIES day SINCE -7d UNTIL today"
            )
            now_str = datetime.now(ET).strftime("%Y-%m-%d")
            today_row = next((r for r in rows if r.get("day", "").startswith(now_str)), rows[-1] if rows else {})
            return {
                "sessions": today_row.get("sessions"),
                "cart_additions": today_row.get("sessions_with_cart_additions"),
                "reached_checkout": today_row.get("sessions_that_reached_checkout"),
                "completed_checkout": today_row.get("sessions_that_completed_checkout"),
                "conversion_rate": today_row.get("conversion_rate"),
                "weekly_trend": rows,
            }
        except Exception:
            return {k: None for k in ["sessions", "cart_additions", "reached_checkout",
                                       "completed_checkout", "conversion_rate"]}

    # ── Top products ───────────────────────────────────────────────────────────

    def get_top_products(self, limit: int = 5) -> list:
        try:
            return self._shopifyql(
                f"FROM sales "
                f"SHOW gross_sales, net_sales, orders "
                f"GROUP BY product_title "
                f"ORDER BY gross_sales DESC "
                f"LIMIT {limit} "
                f"SINCE -7d UNTIL today"
            )
        except Exception:
            gql = """
            {
              products(first: 20, sortKey: UPDATED_AT, reverse: true, query: "status:ACTIVE") {
                edges {
                  node { title totalInventory }
                }
              }
            }
            """
            data = self._gql(gql)
            return [
                {"product_title": e["node"]["title"], "gross_sales": None, "orders": None}
                for e in data["products"]["edges"][:limit]
            ]

    # ── Referral attribution ───────────────────────────────────────────────────

    def get_referral_sources(self) -> list:
        """Traffic and revenue by referral source — ties social media to sales."""
        try:
            return self._shopifyql(
                "FROM sales "
                "SHOW orders, total_sales "
                "GROUP BY order_referrer_source, order_referrer_name "
                "SINCE -7d UNTIL today"
            )
        except Exception:
            return []

    # ── Customer metrics ───────────────────────────────────────────────────────

    def get_customer_insights(self) -> dict:
        try:
            rows = self._shopifyql(
                "FROM customers "
                "SHOW new_customers, returning_customers "
                "TIMESERIES day SINCE -7d UNTIL today"
            )
            total_new = sum(int(r.get("new_customers") or 0) for r in rows)
            total_returning = sum(int(r.get("returning_customers") or 0) for r in rows)
            return {
                "new_customers_7d": total_new,
                "returning_customers_7d": total_returning,
                "returning_rate": (
                    round(total_returning / (total_new + total_returning) * 100, 1)
                    if (total_new + total_returning) > 0 else 0
                ),
                "weekly_trend": rows,
            }
        except Exception:
            week_ago = (datetime.now(ET) - timedelta(days=7)).strftime("%Y-%m-%d")
            try:
                gql = f"""
                {{
                  new: customers(first: 250, query: "created_at:>={week_ago} orders_count:1") {{
                    edges {{ node {{ id }} }}
                  }}
                  returning: customers(first: 250, query: "orders_count:>1 created_at:>={week_ago}") {{
                    edges {{ node {{ id }} }}
                  }}
                }}
                """
                data = self._gql(gql)
                n = len(data["new"]["edges"])
                r = len(data["returning"]["edges"])
                return {
                    "new_customers_7d": n,
                    "returning_customers_7d": r,
                    "returning_rate": round(r / (n + r) * 100, 1) if (n + r) > 0 else 0,
                }
            except Exception:
                return {"new_customers_7d": None, "returning_customers_7d": None, "returning_rate": None}

    # ── Inventory alerts ───────────────────────────────────────────────────────

    def get_low_inventory(self, threshold: int = 10) -> list:
        try:
            rows = self._shopifyql(
                f"FROM inventory "
                f"SHOW ending_inventory_units, sell_through_rate "
                f"GROUP BY product_title, product_variant_title "
                f"HAVING ending_inventory_units < {threshold} "
                f"ORDER BY ending_inventory_units ASC "
                f"LIMIT 20"
            )
            return [
                {
                    "title": r.get("product_title", ""),
                    "variant": r.get("product_variant_title", ""),
                    "inventory": r.get("ending_inventory_units"),
                    "sell_through_rate": r.get("sell_through_rate"),
                }
                for r in rows
            ]
        except Exception:
            try:
                gql = f"""
                {{
                  products(first: 30, query: "status:ACTIVE inventory_total:<{threshold}",
                           sortKey: INVENTORY_TOTAL) {{
                    edges {{ node {{ title totalInventory }} }}
                  }}
                }}
                """
                data = self._gql(gql)
                return [
                    {"title": e["node"]["title"], "variant": None,
                     "inventory": e["node"]["totalInventory"], "sell_through_rate": None}
                    for e in data["products"]["edges"]
                ]
            except Exception:
                return []
