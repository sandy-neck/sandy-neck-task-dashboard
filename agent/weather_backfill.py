#!/usr/bin/env python3
"""
Historical weather + tide backfill, for correlating past conditions against past sales.

Runs only where outbound internet reaches Open-Meteo and NOAA — that's GitHub Actions
(`.github/workflows/weather-backfill.yml`), not the sandboxed agent session, which sits behind an
egress allowlist that blocks both. Reuses the exact SNP 500 engine (`snp500.score_day`) that scores
days live, so backfilled history reads on the same scale as what the daily agent already logs.

Deliberately does not touch Shopify: sales data is pulled and joined separately by whoever is doing
the analysis, so this script — and the workflow that runs it — needs no store credentials at all.

Output: a single JSON file keyed by ISO date, each value carrying the raw weather/tide inputs plus
the full score_day() payload.

Data sources (both free, no API key):
  - Open-Meteo Historical Weather API (archive-api.open-meteo.com) — ERA5 reanalysis, back to 1940,
    with a ~5 day lag from the present. Unlike the live forecast endpoint this has no precipitation
    *probability* field (it's observed, not forecast) — precip_sum is converted to an equivalent
    "prob" input for score_precipitation via precip_prob_proxy() below.
  - NOAA CO-OPS tide predictions — deterministic/astronomical, so past dates are exact, not modeled.
    Chunked to one calendar year per request; NOAA's datagetter has been unreliable with large
    multi-year single requests.
"""
import argparse
import json
import os
import time as time_module
from datetime import date, datetime, time, timedelta, timezone

import requests

from snp500 import score_day
from weather_client import LATITUDE, LONGITUDE, TIDE_STATION, TIDE_STATION_NAME, WEATHER_CODES

SESSION = requests.Session()


def resolve_station() -> dict:
    """Same resolution order as WeatherClient: explicit id, then name match, then proximity."""
    if TIDE_STATION:
        return {"id": TIDE_STATION, "name": f"station {TIDE_STATION} (explicitly set)"}

    resp = SESSION.get(
        "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json",
        params={"type": "tidepredictions"},
        timeout=25,
    )
    resp.raise_for_status()
    stations = resp.json().get("stations", [])
    if not stations:
        raise RuntimeError("NOAA station list came back empty.")

    wanted = TIDE_STATION_NAME.lower()
    named = [s for s in stations if wanted in (s.get("name") or "").lower()]
    pool = named or stations

    def distance(station):
        try:
            return ((float(station["lat"]) - LATITUDE) ** 2
                     + (float(station["lng"]) - LONGITUDE) ** 2) ** 0.5
        except (KeyError, TypeError, ValueError):
            return float("inf")

    best = min(pool, key=distance)
    if not named and distance(best) > 1.0:
        raise RuntimeError(f"No NOAA station resembling '{TIDE_STATION_NAME}' found nearby.")
    return {"id": best["id"], "name": f"{best.get('name')} ({best['id']})"}


def fetch_weather(start: date, end: date) -> dict:
    resp = SESSION.get(
        "https://archive-api.open-meteo.com/v1/archive",
        params={
            "latitude": LATITUDE,
            "longitude": LONGITUDE,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": ",".join([
                "weather_code", "temperature_2m_max", "precipitation_sum",
                "wind_speed_10m_max", "sunshine_duration",
            ]),
            # Same 10am-6pm core-window approach as the live client: the SNP 500 scores the usable
            # beach window, not a blunt daily average.
            "hourly": ",".join([
                "temperature_2m", "cloud_cover", "dew_point_2m", "wind_speed_10m",
            ]),
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "America/New_York",
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def core_window_means(hourly: dict, start_hour: int = 10, end_hour: int = 18) -> dict:
    times = hourly.get("time") or []
    fields = ["temperature_2m", "cloud_cover", "dew_point_2m", "wind_speed_10m"]
    buckets = {}
    for i, stamp in enumerate(times):
        if "T" not in stamp:
            continue
        day, clock = stamp.split("T", 1)
        try:
            hour = int(clock[:2])
        except ValueError:
            continue
        if not (start_hour <= hour < end_hour):
            continue
        slot = buckets.setdefault(day, {f: [] for f in fields})
        for field in fields:
            values = hourly.get(field) or []
            if i < len(values) and values[i] is not None:
                slot[field].append(values[i])

    out = {}
    for day, slot in buckets.items():
        out[day] = {
            "temp_f": _mean(slot["temperature_2m"]),
            "cloud_pct": _mean(slot["cloud_cover"]),
            "dew_point_f": _mean(slot["dew_point_2m"]),
            "wind_mph": _mean(slot["wind_speed_10m"]),
        }
    return out


def _mean(values):
    return round(sum(values) / len(values), 1) if values else None


def precip_prob_proxy(precip_in) -> int:
    """
    Map observed precipitation (inches) onto the 0-100 "chance of rain" scale score_precipitation()
    expects. ERA5 reanalysis reports what actually fell, not a forecast probability — for
    backtesting, knowing it rained is strictly better information than a probability would have
    been; this just reshapes it to fit the existing scorer rather than forking the scoring logic.
    """
    precip_in = precip_in or 0
    if precip_in <= 0:
        return 0
    if precip_in < 0.02:
        return 12
    if precip_in < 0.1:
        return 45
    if precip_in < 0.25:
        return 65
    if precip_in < 0.4:
        return 80
    return 95


def fetch_tides(station_id: str, start: date, end: date) -> dict:
    """NOAA predictions, chunked to one calendar year per request."""
    by_day = {}
    chunk_start = start
    while chunk_start <= end:
        chunk_end = min(end, date(chunk_start.year, 12, 31))
        resp = SESSION.get(
            "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            params={
                "product": "predictions",
                "application": "SandyNeckProvisions",
                "begin_date": chunk_start.strftime("%Y%m%d"),
                "end_date": chunk_end.strftime("%Y%m%d"),
                "datum": "MLLW",
                "station": station_id,
                "time_zone": "lst_ldt",
                "units": "english",
                "interval": "hilo",
                "format": "json",
            },
            timeout=60,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            raise RuntimeError(payload["error"].get("message", "NOAA error"))

        for entry in payload.get("predictions", []):
            stamp, kind = entry.get("t", ""), entry.get("type")
            if " " not in stamp:
                continue
            day, clock = stamp.split(" ", 1)
            by_day.setdefault(day, []).append({
                "time": clock,
                "type": "low" if kind == "L" else "high",
                "feet": round(float(entry.get("v", 0)), 1),
            })

        chunk_start = chunk_end + timedelta(days=1)
        time_module.sleep(0.5)  # be polite to NOAA between chunked requests
    return by_day


def build_days(weather_payload: dict, tides_by_day: dict) -> dict:
    daily = weather_payload.get("daily", {})
    core = core_window_means(weather_payload.get("hourly", {}))

    results = {}
    for i, day in enumerate(daily.get("time", [])):
        def at(key):
            values = daily.get(key) or []
            return values[i] if i < len(values) else None

        code = at("weather_code")
        precip_in = at("precipitation_sum")
        sun_hours = (at("sunshine_duration") or 0) / 3600
        c = core.get(day, {})

        low_tide = None
        for event in tides_by_day.get(day, []):
            if event["type"] != "low":
                continue
            hour, minute = (int(x) for x in event["time"].split(":")[:2])
            candidate = time(hour, minute)
            # Prefer the low tide closest to the middle of the beach day, same as the live client.
            if low_tide is None or abs(hour - 15) < abs(low_tide.hour - 15):
                low_tide = candidate

        precip_prob = precip_prob_proxy(precip_in)
        persistent_rain = (precip_in or 0) >= 0.4
        thunderstorms = code in (95, 96, 99)

        score = score_day({
            "date_local": day,
            "temp_f": c.get("temp_f") or at("temperature_2m_max"),
            "precip_prob": precip_prob,
            "cloud_pct": c.get("cloud_pct"),
            "dew_point_f": c.get("dew_point_f"),
            "wind_mph": c.get("wind_mph") or at("wind_speed_10m_max"),
            "low_tide_local": low_tide,
            "persistent_rain": persistent_rain,
            "thunderstorms": thunderstorms,
            "source_reliability": 95,  # observed history, not a forecast
        })

        results[day] = {
            "weekday": datetime.fromisoformat(day).strftime("%A"),
            "conditions": WEATHER_CODES.get(code, "unsettled"),
            "high_f": at("temperature_2m_max"),
            "core_temp_f": c.get("temp_f"),
            "precip_in": precip_in,
            "precip_prob_proxy": precip_prob,
            "sunshine_hours": round(sun_hours, 1),
            "wind_mph": c.get("wind_mph") or at("wind_speed_10m_max"),
            "cloud_pct": c.get("cloud_pct"),
            "low_tide": low_tide.strftime("%H:%M") if low_tide else None,
            "snp500": score,
        }
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--out", default="../brain/reference/historical-weather.json",
                         help="Output path, relative to this script's directory.")
    args = parser.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    if end < start:
        raise SystemExit("--end must not be before --start")

    print(f"Resolving tide station near '{TIDE_STATION_NAME}'...")
    station = resolve_station()
    print(f"Using station: {station['name']}")

    print(f"Fetching weather {start} to {end}...")
    weather_payload = fetch_weather(start, end)

    print(f"Fetching tides {start} to {end}...")
    tides_by_day = fetch_tides(station["id"], start, end)

    days = build_days(weather_payload, tides_by_day)

    out_path = os.path.join(os.path.dirname(__file__), args.out)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "range": {"start": args.start, "end": args.end},
            "tide_station": station["name"],
            "days": days,
        }, f, indent=2, sort_keys=True)

    print(f"Wrote {len(days)} days to {out_path}")


if __name__ == "__main__":
    main()
