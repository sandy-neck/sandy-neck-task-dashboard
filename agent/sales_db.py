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
"""
import csv
import os

REFERENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "brain", "reference")
LOCATION_CSV = os.path.join(REFERENCE_DIR, "daily_sales_by_location.csv")
CHANNEL_CSV = os.path.join(REFERENCE_DIR, "daily_sales_by_channel.csv")


def _read(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _write(path: str, rows: list, dim_col: str) -> None:
    rows = sorted(rows, key=lambda r: (r["date"], r[dim_col]))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["date", dim_col, "total_sales", "orders"])
        w.writeheader()
        w.writerows(rows)


def load_location() -> list:
    """Every row of daily_sales_by_location.csv: dicts with date/pos_location_name/total_sales/orders."""
    return _read(LOCATION_CSV)


def load_channel() -> list:
    """Every row of daily_sales_by_channel.csv: dicts with date/sales_channel/total_sales/orders."""
    return _read(CHANNEL_CSV)


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
            "date": day,
            "pos_location_name": row["location"],
            "total_sales": row["revenue"],
            "orders": row["orders"],
        })
    _write(LOCATION_CSV, loc, "pos_location_name")

    chan = [r for r in load_channel() if r["date"] != day]
    for row in channel_rows:
        chan.append({
            "date": day,
            "sales_channel": row["channel"],
            "total_sales": row["revenue"],
            "orders": row["orders"],
        })
    _write(CHANNEL_CSV, chan, "sales_channel")
