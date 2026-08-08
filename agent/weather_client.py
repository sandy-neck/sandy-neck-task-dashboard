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
from datetime import datetime, timedelta

# Sandy Neck Beach, East Sandwich MA
LATITUDE = float(os.environ.get("STORE_LATITUDE", "41.7370"))
LONGITUDE = float(os.environ.get("STORE_LONGITUDE", "-70.3870"))

# NOAA station id for tide predictions. Unset by default on purpose — guessing a station would
# silently produce tides for the wrong body of water. Find the nearest station at
# https://tidesandcurrents.noaa.gov/map/ and set the id here.
TIDE_STATION = os.environ.get("NOAA_TIDE_STATION", "").strip()

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
        if TIDE_STATION:
            try:
                result["tides"] = self._fetch_tides()
            except Exception as e:
                result["tides"] = {"available": False, "error": str(e)}
        else:
            result["tides"] = {
                "available": False,
                "reason": "NOAA_TIDE_STATION not set — find the nearest station at "
                          "https://tidesandcurrents.noaa.gov/map/ and set it to enable tide context.",
            }
        return result

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
                    "wind_speed_10m_max",
                    "sunshine_duration",
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
        daily = resp.json().get("daily", {})

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
                "wind_mph": wind,
                "sunshine_hours": round(sun_hours, 1),
                "beach_score": score,
                "beach_label": self._label(score),
            }
        return days

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

    def _fetch_tides(self) -> dict:
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
                "station": TIDE_STATION,
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
        return {"available": True, "station": TIDE_STATION, "by_day": by_day}


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
