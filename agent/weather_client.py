"""
Weather and tide context for Sandy Neck.

The reason this exists: a summer Friday is not a unit of measurement. A hot, muggy, beach-bound
Friday should substantially outbill a cool or rainy one, and comparing them without that context
produces confidently wrong conclusions — exactly what happened on 2026-08-07, where a day that beat
the running average by 25% was, given the conditions, actually a slight underperformance.

Sources (both free, no API key, both fine inside GitHub Actions):
  - Open-Meteo forecast endpoint with `past_days` for recent actuals. The separate archive endpoint
    lags several days, which is useless for a daily report.
  - NOAA CO-OPS tide predictions. Requires a station id; see NOAA_TIDE_STATION below.
"""
import os
import requests
from datetime import datetime, time, timedelta

# Sandy Neck Beach, East Sandwich MA
LATITUDE = float(os.environ.get("STORE_LATITUDE", "41.7370"))
LONGITUDE = float(os.environ.get("STORE_LONGITUDE", "-70.3870"))

# Tide station. An explicit id always wins; otherwise the station is resolved by name at runtime
# against NOAA's own station list. Resolving beats hardcoding a guessed id — a wrong station
# silently reports tides for the wrong body of water, which is worse than no tides at all. The
# resolved station is logged every run so it can be eyeballed.
TIDE_STATION = os.environ.get("NOAA_TIDE_STATION", "").strip()
TIDE_STATION_NAME = os.environ.get("NOAA_TIDE_STATION_NAME", "Barnstable Harbor").strip()

# WMO weather codes → plain description.
WEATHER_CODES = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "freezing fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    56: "freezing drizzle", 57: "freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    66: "freezing rain", 67: "freezing rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "light showers", 81: "showers", 82: "heavy showers",
    85: "snow showers", 86: "snow showers",
    95: "thunderstorms", 96: "thunderstorms with hail", 99: "thunderstorms with hail",
}


class WeatherClient:
    def __init__(self):
        self.session = requests.Session()

    def get_context(self, days_back: int = 14) -> dict:
        try:
            days = self._fetch_weather(days_back)
        except Exception as e:
            return {"available": False, "error": str(e)}

        result = {"available": True, "days": days}
        try:
            station = self._resolve_station()
            result["tides"] = (
                self._fetch_tides(station["id"]) | {"station_name": station["name"]}
                if station else
                {"available": False, "reason": f"No NOAA station matching '{TIDE_STATION_NAME}'."}
            )
        except Exception as e:
            result["tides"] = {"available": False, "error": str(e)}
        return result

    # ── Station resolution ────────────────────────────────────────────────────

    def _resolve_station(self) -> dict | None:
        """
        Find the tide station, preferring an explicit id, then a name match, then proximity.

        Looked up live rather than hardcoded: NOAA station ids are not guessable, and a wrong one
        fails silently with plausible-looking numbers for the wrong harbour.
        """
        if TIDE_STATION:
            return {"id": TIDE_STATION, "name": f"station {TIDE_STATION} (explicitly set)"}

        resp = self.session.get(
            "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/stations.json",
            params={"type": "tidepredictions"},
            timeout=25,
        )
        resp.raise_for_status()
        stations = resp.json().get("stations", [])
        if not stations:
            return None

        wanted = TIDE_STATION_NAME.lower()
        named = [s for s in stations if wanted in (s.get("name") or "").lower()]

        # Several stations can share a harbour name across states — pick whichever is nearest.
        pool = named or stations
        def distance(station):
            try:
                return ((float(station["lat"]) - LATITUDE) ** 2
                        + (float(station["lng"]) - LONGITUDE) ** 2) ** 0.5
            except (KeyError, TypeError, ValueError):
                return float("inf")

        best = min(pool, key=distance)
        if not named and distance(best) > 1.0:  # ~60 miles; nothing sensible nearby
            return None
        return {"id": best["id"], "name": f"{best.get('name')} ({best['id']})"}

    # ── Weather ───────────────────────────────────────────────────────────────

    def _fetch_weather(self, days_back: int) -> dict:
        resp = self.session.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": LATITUDE,
                "longitude": LONGITUDE,
                "daily": ",".join([
                    "weather_code",
                    "temperature_2m_max",
                    "apparent_temperature_max",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "wind_speed_10m_max",
                    "sunshine_duration",
                ]),
                # The SNP 500 scores the usable beach window, not the whole calendar day — the PRD
                # is explicit that an overnight low or blunt daily average is the wrong input.
                "hourly": ",".join([
                    "temperature_2m",
                    "precipitation_probability",
                    "cloud_cover",
                    "dew_point_2m",
                    "wind_speed_10m",
                ]),
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "precipitation_unit": "inch",
                "timezone": "America/New_York",
                "past_days": days_back,
                "forecast_days": 2,
            },
            timeout=25,
        )
        resp.raise_for_status()
        payload = resp.json()
        daily = payload.get("daily", {})
        core = self._core_window_means(payload.get("hourly", {}))

        days = {}
        for i, day in enumerate(daily.get("time", [])):
            def at(key):
                values = daily.get(key) or []
                return values[i] if i < len(values) else None

            code = at("weather_code")
            feels = at("apparent_temperature_max")
            precip = at("precipitation_sum")
            wind = at("wind_speed_10m_max")
            sun_hours = (at("sunshine_duration") or 0) / 3600

            score = self._beach_score(feels, precip, wind, code, sun_hours)
            days[day] = {
                "conditions": WEATHER_CODES.get(code, "unsettled"),
                "high_f": at("temperature_2m_max"),
                "feels_like_f": feels,
                "precip_in": precip,
                "precip_prob": at("precipitation_probability_max"),
                "wind_mph": wind,
                "sunshine_hours": round(sun_hours, 1),
                "weather_code": code,
                # Core-window (10am–6pm) averages — what the SNP 500 actually scores.
                "core": core.get(day, {}),
                "beach_score": score,
                "beach_label": self._label(score),
            }
        return days

    @staticmethod
    def _core_window_means(hourly: dict, start_hour: int = 10, end_hour: int = 18) -> dict:
        """Average each hourly field across the usable beach window, grouped by local date."""
        times = hourly.get("time") or []
        if not times:
            return {}

        fields = ["temperature_2m", "precipitation_probability", "cloud_cover",
                  "dew_point_2m", "wind_speed_10m"]
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
                "precip_prob": _mean(slot["precipitation_probability"]),
                "cloud_pct": _mean(slot["cloud_cover"]),
                "dew_point_f": _mean(slot["dew_point_2m"]),
                "wind_mph": _mean(slot["wind_speed_10m"]),
            }
        return out

    @staticmethod
    def _beach_score(feels, precip, wind, code, sun_hours) -> int:
        """
        A 0–100 read on how much the day pushed people toward the beach.

        Deliberately simple and legible — the goal is a defensible basis for "compare this day to
        similar days", not a meteorological model. Every term is one someone can argue with.
        """
        if feels is None:
            return 50  # unknown: stay neutral rather than inventing a signal

        if feels >= 95:
            warmth = 42          # oppressive; some people stay home
        elif feels >= 85:
            warmth = 55
        elif feels >= 78:
            warmth = 50
        elif feels >= 72:
            warmth = 37
        elif feels >= 65:
            warmth = 22
        else:
            warmth = 8

        if sun_hours >= 9:
            sun = 25
        elif sun_hours >= 6:
            sun = 19
        elif sun_hours >= 3:
            sun = 11
        elif sun_hours > 0:
            sun = 5
        else:
            sun = {0: 25, 1: 21, 2: 15, 3: 8}.get(code, 6)

        precip = precip or 0
        if precip >= 0.4:
            weather_penalty = -42
        elif precip >= 0.1:
            weather_penalty = -24
        elif precip >= 0.02:
            weather_penalty = -9
        else:
            weather_penalty = 0

        wind = wind or 0
        wind_penalty = -15 if wind >= 25 else (-8 if wind >= 18 else 0)

        return max(0, min(100, round(warmth + sun + weather_penalty + wind_penalty)))

    @staticmethod
    def _label(score: int) -> str:
        if score >= 78:
            return "prime beach day"
        if score >= 60:
            return "good beach day"
        if score >= 42:
            return "mixed"
        if score >= 25:
            return "poor beach weather"
        return "washout"

    # ── Tides ─────────────────────────────────────────────────────────────────

    def _fetch_tides(self, station_id: str) -> dict:
        today = datetime.now().date()
        start = today - timedelta(days=14)
        resp = self.session.get(
            "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter",
            params={
                "product": "predictions",
                "application": "SandyNeckProvisions",
                "begin_date": start.strftime("%Y%m%d"),
                "end_date": (today + timedelta(days=1)).strftime("%Y%m%d"),
                "datum": "MLLW",
                "station": station_id,
                "time_zone": "lst_ldt",
                "units": "english",
                "interval": "hilo",
                "format": "json",
            },
            timeout=25,
        )
        resp.raise_for_status()
        payload = resp.json()
        if "error" in payload:
            return {"available": False, "error": payload["error"].get("message", "NOAA error")}

        by_day = {}
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

        # Sandy Neck's flats are dramatic at low water, so a midday low plausibly changes how
        # people plan a beach trip. Flagged for correlation, not asserted as a driver.
        for day, events in by_day.items():
            lows = [e for e in events if e["type"] == "low"]
            by_day[day] = {
                "events": events,
                "midday_low": any(10 <= int(e["time"].split(":")[0]) <= 16 for e in lows),
            }
        return {"available": True, "station": station_id, "by_day": by_day}


def _mean(values):
    return round(sum(values) / len(values), 1) if values else None


def score_days_with_snp500(weather: dict, bugs: str = None, access: str = None) -> dict:
    """
    Run every fetched day through the SNP 500 engine.

    This is the consolidation the PRD calls for — one environmental model, two consumers. The
    customer-facing widget and the internal sales analysis read the same score, so the engine gets
    exercised against real days every morning instead of sitting untested until launch.
    """
    from snp500 import score_day

    days = weather.get("days") or {}
    tides = (weather.get("tides") or {}).get("by_day") or {}
    scored = {}

    for day, info in days.items():
        core = info.get("core") or {}
        low_tide = None
        for event in (tides.get(day) or {}).get("events", []):
            if event["type"] == "low":
                hour, minute = (int(x) for x in event["time"].split(":")[:2])
                candidate = time(hour, minute)
                # Prefer the low tide closest to the middle of the beach day.
                if low_tide is None or abs(hour - 15) < abs(low_tide.hour - 15):
                    low_tide = candidate

        code = info.get("weather_code")
        scored[day] = score_day({
            "date_local": day,
            "temp_f": core.get("temp_f") or info.get("high_f"),
            "precip_prob": core.get("precip_prob", info.get("precip_prob")),
            "cloud_pct": core.get("cloud_pct"),
            "dew_point_f": core.get("dew_point_f"),
            "wind_mph": core.get("wind_mph") or info.get("wind_mph"),
            "low_tide_local": low_tide,
            "persistent_rain": (info.get("precip_in") or 0) >= 0.4,
            "thunderstorms": code in (95, 96, 99),
            "bugs": bugs,
            "access": access,
            # Forecast for future days is inherently less certain than observed history.
            "source_reliability": 90,
        })
    return scored


def comparable_days(weather_days: dict, target: str, tolerance: int = 10, limit: int = 5) -> list:
    """
    Recent days whose conditions resembled the target day's.

    This is the whole point of the module: it lets the report say "against other prime beach days,
    this one came up short" instead of comparing a beach day to a rainy Tuesday and calling it
    growth.
    """
    target_day = (weather_days or {}).get(target)
    if not target_day:
        return []
    baseline = target_day["beach_score"]
    matches = [
        {"date": day, **info, "score_gap": info["beach_score"] - baseline}
        for day, info in weather_days.items()
        if day < target and abs(info["beach_score"] - baseline) <= tolerance
    ]
    matches.sort(key=lambda d: d["date"], reverse=True)
    return matches[:limit]
