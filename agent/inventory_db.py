"""
Local daily history of reorder-signal snapshots: on-hand stock, recent sell-through velocity,
days of cover, and urgency -- backed by brain/reference/daily_reorder_signals.csv.

ShopifyClient.get_reorder_signals() already computes this fresh every morning for the daily
report. This just keeps a dated copy of it. Unlike the sales cache, the point here isn't avoiding
a repeat query -- current stock is a point-in-time number and the live query for it is already
cheap -- it's having *history* a live query can't give you: whether a product's velocity is rising
or falling, and when it first crossed into "low", without re-deriving 14 days of trend by hand.

No backfill: stock-on-hand isn't a queryable time series the way sales history is, so this starts
empty and only accumulates from the day it was added onward.
"""
import os

from csv_cache import read_rows, write_rows

REFERENCE_DIR = os.path.join(os.path.dirname(__file__), "..", "brain", "reference")
SIGNALS_CSV = os.path.join(REFERENCE_DIR, "daily_reorder_signals.csv")
FIELDS = ["date", "title", "on_hand", "units_sold_recent", "units_per_day",
          "days_of_cover", "revenue_recent", "urgency"]


def load() -> list:
    """Every row of daily_reorder_signals.csv."""
    return read_rows(SIGNALS_CSV)


def upsert_day(day: str, signals: list) -> None:
    """
    Replace whatever rows exist for `day` with the given signals.

    `signals` is ShopifyClient.get_reorder_signals() output: dicts with title/on_hand/
    units_sold_recent/units_per_day/days_of_cover/revenue_recent/urgency.
    """
    rows = [r for r in load() if r["date"] != day]
    for s in signals:
        rows.append({"date": day, **{k: s.get(k) for k in FIELDS if k != "date"}})
    write_rows(SIGNALS_CSV, rows, FIELDS, sort_key=lambda r: (r["date"], r["title"]))
