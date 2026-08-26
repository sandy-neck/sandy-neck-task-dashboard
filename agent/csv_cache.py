"""Tiny CSV-backed cache helpers shared by sales_db.py and inventory_db.py."""
import csv
import os


def read_rows(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_rows(path: str, rows: list, fieldnames: list, sort_key) -> None:
    rows = sorted(rows, key=sort_key)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
