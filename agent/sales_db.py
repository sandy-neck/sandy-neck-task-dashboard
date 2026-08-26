"""
Local cache of daily Shopify sales, by POS location and by sales channel.

Backed by two CSVs in brain/reference/, backfilled once from full Shopify history (2023-06-01
onward -- as far back as real data goes) and kept current by one upsert_day() call per day from
the daily agent. Exists so repeat analysis -- this session or a future one -- reads a local file
instead of re-running the same ShopifyQL historical query every time. See brain/CONTEXT.md for the
exclusion rules (Snack Shack, 2024 Square caveat) that apply when *using* this data; the cache
itself is intentionally unfiltered/complete, so those rules stay in one place rather than being
silently baked into the stored numbers.

Both files are two different splits of the same underlying sales and their totals always match:
location tells you store vs. Snack Shack vs. non-POS; channel breaks non-POS out further into
Online Store, TikTok, Shop, etc.

Shopify's own totals for a day aren't fixed once it's over -- a late refund, a chargeback, or a
test/draft order that gets cleaned up afterward all change what a past day adds up to. upsert_day()
alone would never notice: it writes a day once and never looks at it again, so the cache would
quietly drift from Shopify's live numbers. reconcile() is the fix -- re-pull a trailing window and
self-heal the cache to match, logging anything that changed rather than silently rewriting history.
"""
import os
from datetime import datetime, timezone

from csv_cache import read_rows, write_rows

REFERENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "brain", "reference")
LOCATION_CSV = os.path.join(REFERENCE_DIR, "daily_sales_by_location.csv")
CHANNEL_CSV = os.path.join(REFERENCE_DIR, "daily_sales_by_channel.csv")
RECONCILE_LOG = os.path.join(REFERENCE_DIR, "reconciliation-log.csv")

# How far back the daily agent re-checks for drift. 30 days comfortably covers normal refund and
# chargeback windows; a one-off manual reconcile() call can cover a wider range if ever needed.
RECONCILE_LOOKBACK_DAYS = 30


def _fmt_money(x) -> str:
    """
    Match the backfill's own formatting -- ShopifyQL's JSON gives whole-dollar amounts as bare
    integers ("0", "919"), not "0.0". Writing plain str(float) instead would rewrite the whole
    cache's number formatting on the next reconcile without changing a single real value, turning
    a diffable file (see brain/README.md) into a wall of no-op noise.
    """
    x = round(float(x), 2)
    return str(int(x)) if x == int(x) else str(x)


def load_location() -> list:
    """Every row of daily_sales_by_location.csv: dicts with date/pos_location_name/total_sales/orders."""
    return read_rows(LOCATION_CSV)


def load_channel() -> list:
    """Every row of daily_sales_by_channel.csv: dicts with date/sales_channel/total_sales/orders."""
    return read_rows(CHANNEL_CSV)


def upsert_day(day: str, location_rows: list, channel_rows: list) -> None:
    """
    Replace whatever rows exist for `day` with the given ones, in both CSVs.

    `location_rows` / `channel_rows` are the list shapes ShopifyClient.get_location_day() and
    get_channel_day_all() return: [{"location"|"channel": str, "revenue": float, "orders": int}].
    Replacing rather than appending makes this safe to call again on a retried or re-run day.
    """
    loc = [r for r in load_location() if r["date"] != day]
    for row in location_rows:
        loc.append({
            "date": day, "pos_location_name": row["location"],
            "total_sales": _fmt_money(row["revenue"]), "orders": row["orders"],
        })
    write_rows(LOCATION_CSV, loc, ["date", "pos_location_name", "total_sales", "orders"],
               sort_key=lambda r: (r["date"], r["pos_location_name"]))

    chan = [r for r in load_channel() if r["date"] != day]
    for row in channel_rows:
        chan.append({
            "date": day, "sales_channel": row["channel"],
            "total_sales": _fmt_money(row["revenue"]), "orders": row["orders"],
        })
    write_rows(CHANNEL_CSV, chan, ["date", "sales_channel", "total_sales", "orders"],
               sort_key=lambda r: (r["date"], r["sales_channel"]))


def reconcile(location_range_rows: list, channel_range_rows: list, start: str, end: str) -> dict:
    """
    Re-check [start, end] against fresh Shopify data and self-heal any difference.

    `location_range_rows` / `channel_range_rows` are ShopifyClient.get_location_range() /
    get_channel_range() output: [{"date", "location"|"channel", "revenue", "orders"}, ...] for the
    whole window in one call each. Shopify's current totals are always treated as the source of
    truth -- any (date, location/channel) whose cached total_sales or orders no longer matches gets
    overwritten, and every change is appended to reconciliation-log.csv so a revision is visible
    rather than silently rewriting history.

    Returns {"window": {...}, "revised_count": int, "revisions": [...]}. Refuses to run -- rather
    than treat it as "everything genuinely went to zero" -- if either fetch comes back empty, since
    ShopifyClient swallows failures into [] and an empty result is far more likely a dropped API
    call than a real report of no sales anywhere in the window.
    """
    if not location_range_rows or not channel_range_rows:
        return {"window": {"start": start, "end": end}, "revised_count": 0, "revisions": [],
                "skipped": "empty fetch -- refusing to reconcile against no data"}

    revisions = []

    def _reconcile_one(cache_rows, fresh_rows, dim_col, fresh_key, csv_path, fieldnames):
        cached, untouched = {}, []
        for r in cache_rows:
            if start <= r["date"] <= end:
                cached[(r["date"], r[dim_col])] = (round(float(r["total_sales"]), 2), int(r["orders"]))
            else:
                untouched.append(r)

        fresh = {
            (r["date"], r[fresh_key]): (round(float(r["revenue"]), 2), int(r["orders"]))
            for r in fresh_rows
        }

        for key in sorted(set(cached) | set(fresh)):
            old, new = cached.get(key, (0.0, 0)), fresh.get(key, (0.0, 0))
            if abs(old[0] - new[0]) > 0.01 or old[1] != new[1]:
                date, dim_value = key
                revisions.append({
                    "dimension": dim_col, "date": date, "key": dim_value,
                    "old_total_sales": old[0], "new_total_sales": new[0],
                    "old_orders": old[1], "new_orders": new[1],
                })

        rebuilt = untouched + [
            {"date": d, dim_col: k, "total_sales": _fmt_money(v[0]), "orders": v[1]}
            for (d, k), v in fresh.items()
        ]
        write_rows(csv_path, rebuilt, fieldnames, sort_key=lambda r: (r["date"], r[dim_col]))

    _reconcile_one(load_location(), location_range_rows, "pos_location_name", "location",
                    LOCATION_CSV, ["date", "pos_location_name", "total_sales", "orders"])
    _reconcile_one(load_channel(), channel_range_rows, "sales_channel", "channel",
                    CHANNEL_CSV, ["date", "sales_channel", "total_sales", "orders"])

    if revisions:
        _log_revisions(revisions)

    return {"window": {"start": start, "end": end}, "revised_count": len(revisions), "revisions": revisions}


def _log_revisions(revisions: list) -> None:
    detected_at = datetime.now(timezone.utc).isoformat()
    existing = read_rows(RECONCILE_LOG)
    for rev in revisions:
        existing.append({"detected_at": detected_at, "sales_date": rev["date"],
                          "dimension": rev["dimension"], "key": rev["key"],
                          "old_total_sales": rev["old_total_sales"], "new_total_sales": rev["new_total_sales"],
                          "old_orders": rev["old_orders"], "new_orders": rev["new_orders"]})
    write_rows(RECONCILE_LOG, existing,
               ["detected_at", "sales_date", "dimension", "key",
                "old_total_sales", "new_total_sales", "old_orders", "new_orders"],
               sort_key=lambda r: (r["detected_at"], r["sales_date"]))
