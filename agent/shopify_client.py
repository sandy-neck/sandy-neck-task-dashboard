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

    def _report_dates(self) -> dict:
        """
        The report runs in the morning, so the headline day is YESTERDAY — the last
        complete sales day. Reporting "today" at 7 AM would describe an empty store.
        """
        now_et = datetime.now(ET)
        yesterday = (now_et - timedelta(days=1)).date()
        return {
            "today": now_et.date(),
            "yesterday": yesterday,
            "prior_day": yesterday - timedelta(days=1),
            "last_week": yesterday - timedelta(days=7),
        }

    def get_sales_summary(self) -> dict:
        """Sales for the last complete day, with prior-day and same-weekday context."""
        dates = self._report_dates()
        try:
            rows = self._shopifyql(
                "FROM sales "
                "SHOW orders, gross_sales, net_sales, average_order_value "
                "TIMESERIES day SINCE -14d UNTIL today"
            )
            by_day = {str(r.get("day", ""))[:10]: r for r in rows}
            return self._assemble_summary(by_day, dates, rows, "shopifyql")
        except Exception:
            return self._sales_summary_fallback(dates)

    def _assemble_summary(self, by_day: dict, dates: dict, rows: list, source: str) -> dict:
        def field(day, name):
            return (by_day.get(str(day)) or {}).get(name)

        def revenue(day):
            return float(field(day, "gross_sales") or 0)

        def orders(day):
            return int(field(day, "orders") or 0)

        y_revenue = revenue(dates["yesterday"])
        y_orders = orders(dates["yesterday"])
        y_aov = float(field(dates["yesterday"], "average_order_value") or 0)
        if not y_aov and y_orders:
            y_aov = y_revenue / y_orders

        # Trailing complete days ending yesterday — the baseline "normal day"
        trailing = [revenue(dates["yesterday"] - timedelta(days=i)) for i in range(7)]
        trailing = [t for t in trailing if t > 0]
        week_avg = sum(trailing) / len(trailing) if trailing else 0

        return {
            "report_date": str(dates["yesterday"]),
            "revenue": y_revenue,
            "net_revenue": float(field(dates["yesterday"], "net_sales") or y_revenue),
            "orders": y_orders,
            "aov": y_aov,
            "prior_day_revenue": revenue(dates["prior_day"]),
            "prior_day_orders": orders(dates["prior_day"]),
            "last_week_revenue": revenue(dates["last_week"]),
            "last_week_orders": orders(dates["last_week"]),
            "week_avg_revenue": round(week_avg, 2),
            # Today is only hours old at send time — context, never the headline.
            "today_so_far_revenue": revenue(dates["today"]),
            "today_so_far_orders": orders(dates["today"]),
            "weekly_trend": rows,
            "source": source,
        }

    def _sales_summary_fallback(self, dates: dict) -> dict:
        """
        Raw order query for when ShopifyQL is unavailable.

        Orders are bucketed into ET calendar days by parsing createdAt, which Shopify
        returns in UTC. Comparing the raw ISO strings would misfile every evening
        order into the following day.
        """
        since = ET.localize(
            datetime.combine(dates["last_week"] - timedelta(days=1), datetime.min.time())
        )

        gql = """
        query($q: String!, $after: String) {
          orders(first: 250, query: $q, after: $after, sortKey: CREATED_AT) {
            pageInfo { hasNextPage endCursor }
            edges {
              node {
                createdAt
                totalPriceSet { shopMoney { amount } }
              }
            }
          }
        }
        """
        nodes, after = [], None
        for _ in range(12):  # cap pagination so a bad filter can't loop forever
            data = self._gql(gql, {"q": f"created_at:>={since.isoformat()}", "after": after})
            conn = data["orders"]
            nodes.extend(e["node"] for e in conn["edges"])
            if not conn["pageInfo"]["hasNextPage"]:
                break
            after = conn["pageInfo"]["endCursor"]

        by_day = {}
        for o in nodes:
            created = datetime.fromisoformat(
                o["createdAt"].replace("Z", "+00:00")
            ).astimezone(ET)
            bucket = by_day.setdefault(str(created.date()), {"orders": 0, "gross_sales": 0.0})
            bucket["orders"] += 1
            # totalPrice includes tax and shipping, so this runs slightly above the
            # gross_sales figure ShopifyQL reports.
            bucket["gross_sales"] += float(o["totalPriceSet"]["shopMoney"]["amount"])

        rows = [{"day": day, **vals} for day, vals in sorted(by_day.items())]
        return self._assemble_summary(by_day, dates, rows, "graphql_fallback")

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

    # ── Channel split ──────────────────────────────────────────────────────────

    def get_channel_split(self, since: str = "-7d") -> list:
        """
        Revenue by sales channel. This is the backbone of the whole report — in-store and online
        are different businesses and get judged separately, never as one blended number.
        """
        try:
            rows = self._shopifyql(
                f"FROM sales SHOW orders, gross_sales "
                f"GROUP BY sales_channel "
                f"SINCE {since} UNTIL today"
            )
            total = sum(float(r.get("gross_sales") or 0) for r in rows) or 1
            return [
                {
                    "channel": r.get("sales_channel") or "Unattributed",
                    "orders": int(r.get("orders") or 0),
                    "revenue": float(r.get("gross_sales") or 0),
                    "share_pct": round(float(r.get("gross_sales") or 0) / total * 100, 1),
                }
                for r in sorted(rows, key=lambda x: float(x.get("gross_sales") or 0), reverse=True)
            ]
        except Exception:
            return []

    def get_channel_day(self, day: str) -> list:
        """Per-channel revenue for one specific day."""
        try:
            rows = self._shopifyql(
                f"FROM sales SHOW orders, gross_sales "
                f"GROUP BY sales_channel "
                f"SINCE {day} UNTIL {day}"
            )
            return [
                {
                    "channel": r.get("sales_channel") or "Unattributed",
                    "orders": int(r.get("orders") or 0),
                    "revenue": float(r.get("gross_sales") or 0),
                }
                for r in rows
            ]
        except Exception:
            return []

    def get_top_products_by_channel(self, channel: str, since: str = "-7d", limit: int = 8) -> list:
        """Top sellers within a single channel — 'what moved in the store' vs. 'what moved online'."""
        safe = channel.replace("'", "")
        try:
            return self._shopifyql(
                f"FROM sales SHOW gross_sales, net_items_sold, orders "
                f"WHERE sales_channel = '{safe}' "
                f"GROUP BY product_title "
                f"ORDER BY gross_sales DESC LIMIT {limit} "
                f"SINCE {since} UNTIL today"
            )
        except Exception:
            return []

    # ── Season to date ─────────────────────────────────────────────────────────

    def get_season_trend(self) -> dict:
        """
        Where the season stands. Peak runs Memorial Day → Labor Day, so a single day only means
        something against the arc it sits on.
        """
        now = datetime.now(ET)
        season_start = f"{now.year}-05-25"
        try:
            rows = self._shopifyql(
                f"FROM sales SHOW orders, gross_sales "
                f"TIMESERIES week "
                f"SINCE {season_start} UNTIL today"
            )
            weeks = [
                {
                    "week": str(r.get("week", ""))[:10],
                    "orders": int(r.get("orders") or 0),
                    "revenue": float(r.get("gross_sales") or 0),
                }
                for r in rows
            ]
            total = sum(w["revenue"] for w in weeks)
            recent = weeks[-4:] if len(weeks) >= 4 else weeks
            peak = max(weeks, key=lambda w: w["revenue"], default=None)
            return {
                "season_start": season_start,
                "weeks": weeks,
                "season_to_date_revenue": round(total, 2),
                "recent_weeks": recent,
                "peak_week": peak,
                "weeks_elapsed": len(weeks),
            }
        except Exception:
            return {}

    # ── Reorder intelligence ───────────────────────────────────────────────────

    def get_reorder_signals(self, lookback_days: int = 14, limit: int = 25) -> list:
        """
        Products at risk of running out, with enough context to make the reorder call.

        Stock alone doesn't answer anything — 6 units is comfortable for a slow mover and an
        emergency for something selling 4 a day. Pairing stock with recent velocity gives days of
        cover, which is the number that actually matters against a vendor's lead time.
        """
        try:
            sold = self._shopifyql(
                f"FROM sales SHOW net_items_sold, gross_sales "
                f"GROUP BY product_title "
                f"SINCE -{lookback_days}d UNTIL today"
            )
        except Exception:
            return []

        velocity = {}
        for row in sold:
            title = row.get("product_title")
            if not title:
                continue
            units = float(row.get("net_items_sold") or 0)
            velocity[title] = {
                "units_sold": units,
                "revenue": float(row.get("gross_sales") or 0),
                "per_day": units / lookback_days,
            }

        try:
            stock_rows = self._shopifyql(
                "FROM inventory SHOW ending_inventory_units "
                "GROUP BY product_title "
                "ORDER BY ending_inventory_units ASC LIMIT 250"
            )
        except Exception:
            return []

        signals = []
        for row in stock_rows:
            title = row.get("product_title")
            if not title:
                continue
            on_hand = float(row.get("ending_inventory_units") or 0)
            stats = velocity.get(title)
            if not stats or stats["per_day"] <= 0:
                continue  # not selling — a low count here isn't a reorder question

            days_cover = on_hand / stats["per_day"]
            if days_cover > 45:
                continue  # comfortable

            signals.append({
                "title": title,
                "on_hand": int(on_hand),
                "units_sold_recent": round(stats["units_sold"], 1),
                "units_per_day": round(stats["per_day"], 2),
                "days_of_cover": round(days_cover, 1),
                "revenue_recent": round(stats["revenue"], 2),
                "urgency": (
                    "out of stock" if on_hand <= 0
                    else "critical" if days_cover <= 7
                    else "low" if days_cover <= 21
                    else "watch"
                ),
            })

        signals.sort(key=lambda s: s["days_of_cover"])
        return signals[:limit]

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
