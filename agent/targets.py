"""
Annual revenue target and season pacing.

A seasonal business can't be paced against a straight line. Being 55% of the way through the
calendar means nothing when August alone carries a fifth of the year — the only honest question is
"how much of the year's revenue has normally landed by this date, and are we ahead of that?"

Prior year's shape answers it. The curve is learned from actual history the first time it's
computed and cached in brain/reference/, because last year's numbers don't change and re-pulling a
full year of orders on every run is wasteful. Until that cache exists, the fallback below is a
documented estimate of Sandy Neck's season, not measured fact, and the agent is told to say so.
"""
import json
from datetime import date
from pathlib import Path

ANNUAL_TARGET = 190_000

CACHE = Path(__file__).resolve().parent.parent / "brain" / "reference" / "prior-year-seasonality.json"

# Sandy's own description of the year, used to date the phases and to shape the fallback curve:
#   peak through late August, early shoulder to mid-September dropping to weekends only,
#   late shoulder through Columbus Day weekend, then online/social carries the rest.
SEASON_PHASES = [
    ("Deep off-season", (1, 1), (4, 30), "Online and social only. Store effectively closed."),
    ("Spring ramp", (5, 1), (5, 24), "Getting ready. Weekend traffic begins."),
    ("Peak", (5, 25), (8, 22), "Memorial Day to late August. The year is won or lost here."),
    ("Early shoulder", (8, 23), (9, 15), "Drops toward weekends only. Volume falls fast."),
    ("Late shoulder", (9, 16), (10, 12), "Weekends through Columbus Day. Last of the foot traffic."),
    ("Off-season", (10, 13), (12, 31), "Online, social and TikTok. The growth opportunity."),
]

# Share of annual revenue by month when no measured history is available. Estimated from the phase
# calendar above — replaced automatically once a real prior year has been cached.
FALLBACK_MONTHLY_SHARE = {
    1: 0.01, 2: 0.01, 3: 0.02, 4: 0.03, 5: 0.08, 6: 0.15,
    7: 0.22, 8: 0.24, 9: 0.12, 10: 0.07, 11: 0.03, 12: 0.02,
}


def current_phase(day: date = None):
    day = day or date.today()
    for name, (m0, d0), (m1, d1), note in SEASON_PHASES:
        if date(day.year, m0, d0) <= day <= date(day.year, m1, d1):
            remaining = (date(day.year, m1, d1) - day).days
            return {"phase": name, "note": note, "days_remaining": remaining,
                    "ends": date(day.year, m1, d1).isoformat()}
    return {"phase": "Unknown", "note": "", "days_remaining": None, "ends": None}


def load_prior_year_curve():
    """Cached cumulative-share-by-day-of-year curve, if one has been built."""
    try:
        data = json.loads(CACHE.read_text(encoding="utf-8"))
        if data.get("cumulative_by_doy"):
            return data
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        pass
    return None


def save_prior_year_curve(year: int, daily_revenue: dict):
    """
    Build and cache the cumulative curve from {YYYY-MM-DD: revenue}.

    Stored as cumulative share of the year by day-of-year, so it can pace any target without
    re-deriving anything.
    """
    total = sum(daily_revenue.values())
    if total <= 0:
        return None

    running, cumulative = 0.0, {}
    for day_str in sorted(daily_revenue):
        running += daily_revenue[day_str]
        try:
            doy = date.fromisoformat(day_str).timetuple().tm_yday
        except ValueError:
            continue
        cumulative[str(doy)] = round(running / total, 6)

    payload = {"year": year, "total_revenue": round(total, 2), "cumulative_by_doy": cumulative}
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def _expected_share(day: date, curve=None) -> tuple:
    """Share of annual revenue normally banked by this date. Returns (share, basis)."""
    if curve and curve.get("cumulative_by_doy"):
        doy = day.timetuple().tm_yday
        by_doy = curve["cumulative_by_doy"]
        for candidate in range(doy, 0, -1):
            if str(candidate) in by_doy:
                return by_doy[str(candidate)], f"{curve['year']} actuals"

    # Fallback: whole months elapsed, plus a pro-rated slice of the current month.
    share = sum(FALLBACK_MONTHLY_SHARE[m] for m in range(1, day.month))
    days_in_month = (date(day.year + (day.month == 12), day.month % 12 + 1, 1)
                     - date(day.year, day.month, 1)).days
    share += FALLBACK_MONTHLY_SHARE[day.month] * (day.day / days_in_month)
    return share, "estimated seasonality (no prior-year data cached yet)"


def pace(ytd_revenue, day: date = None, target: int = ANNUAL_TARGET, curve=None) -> dict:
    """Where the year stands against target, adjusted for how seasonal the business is."""
    day = day or date.today()
    if ytd_revenue is None:
        return {"available": False}

    share, basis = _expected_share(day, curve)
    share = max(share, 1e-6)
    expected = target * share
    projected = ytd_revenue / share

    delta = ytd_revenue - expected
    if abs(delta) < target * 0.02:
        status = "on pace"
    elif delta > 0:
        status = "ahead of pace"
    else:
        status = "behind pace"

    return {
        "available": True,
        "target": target,
        "ytd_revenue": round(ytd_revenue, 2),
        "expected_by_now": round(expected),
        "pct_of_target": round(ytd_revenue / target * 100, 1),
        "pct_of_year_normally_banked": round(share * 100, 1),
        "projected_year_end": round(projected),
        "gap_to_pace": round(delta),
        "status": status,
        "basis": basis,
        "phase": current_phase(day),
    }
