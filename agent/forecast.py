"""
Week-ahead projections, and what each day needs to earn.

Two different numbers, and the gap between them is the whole point:

  EXPECTED — what a day like this normally does. Descriptive, from the SNP 500 score and BJ's
             revenue anchors. "A 480 day usually brings about $2,000."

  REQUIRED — what a day like this needs to do to stay on track for the annual target. Prescriptive,
             back-solved from what's left to earn and how much of the year remains.

A day can clear EXPECTED and still miss REQUIRED. That is exactly the question BJ asked: today
was a great Saturday compared to other days, but was it a great Saturday *given that August has to
carry the year*? Reporting only the first number quietly congratulates the business for keeping pace
with itself while the target slips away.

The remaining target is allocated across future days in proportion to what each can realistically
earn — a washout Tuesday isn't asked to make up a shortfall a beach Saturday should carry.
"""
from datetime import date, timedelta

from expectations import expected_revenue
from targets import ANNUAL_TARGET, _expected_share


def project_week(snp_scores: dict, ytd_revenue, today: date = None,
                 target: int = ANNUAL_TARGET, curve=None, days: int = 7) -> dict:
    """
    Project the days ahead and say what each one needs to earn.

    snp_scores: {"YYYY-MM-DD": {"score": int, "rating": str, ...}} from the SNP 500 engine,
    covering forecast days as well as history.
    """
    today = today or date.today()
    horizon = [today + timedelta(days=i) for i in range(1, days + 1)]

    upcoming = []
    for day in horizon:
        key = day.isoformat()
        scored = snp_scores.get(key) or {}
        score = scored.get("score")
        if score is None:
            continue
        upcoming.append({
            "date": key,
            "weekday": day.strftime("%a"),
            "snp500": score,
            "rating": scored.get("rating"),
            "headline": scored.get("headline"),
            "expected": round(expected_revenue(score) or 0),
        })

    if not upcoming:
        return {"available": False, "reason": "no scored forecast days"}

    result = {"available": True, "days": upcoming,
              "expected_week_total": round(sum(d["expected"] for d in upcoming))}

    if ytd_revenue is None:
        result["required_available"] = False
        return result

    # How much of the year's revenue normally lands during this window, relative to everything
    # still to come. Uses the seasonality curve so a week in August carries its real weight.
    share_now, basis = _expected_share(today, curve)
    share_end, _ = _expected_share(horizon[-1], curve)
    remaining_share = max(1.0 - share_now, 1e-6)
    window_share = max(share_end - share_now, 0.0)

    remaining_target = max(target - ytd_revenue, 0.0)
    required_week = remaining_target * (window_share / remaining_share)

    # Spread the week's requirement across days by earning capacity, not evenly — a rainy Tuesday
    # shouldn't be asked to cover what a beach Saturday should.
    capacity = sum(d["expected"] for d in upcoming) or 1
    for day in upcoming:
        day["required"] = round(required_week * (day["expected"] / capacity))
        day["gap"] = day["required"] - day["expected"]

    total_required = sum(d["required"] for d in upcoming)
    total_expected = result["expected_week_total"]
    shortfall = total_required - total_expected

    result.update({
        "required_available": True,
        "required_week_total": round(total_required),
        "week_shortfall": round(shortfall),
        "basis": basis,
        "verdict": _verdict(total_expected, total_required),
        "remaining_target": round(remaining_target),
    })
    return result


def _verdict(expected, required) -> str:
    """Whether normal performance is enough, in plain words."""
    if required <= 0:
        return "target already covered — anything this week is upside"
    ratio = expected / required
    if ratio >= 1.15:
        return "the week ahead should comfortably beat what the target needs"
    if ratio >= 1.0:
        return "normal performance is roughly enough to stay on track"
    if ratio >= 0.85:
        return "slightly short — normal days won't quite keep pace"
    if ratio >= 0.6:
        return "meaningfully short — the week needs more than conditions will hand us"
    return "well short — conditions alone won't get near what the target needs"


def best_opportunity(projection: dict):
    """
    The day where effort pays best: the highest-quality day still carrying a gap.

    Deliberately not the day with the biggest shortfall — that's usually a washout nobody can fix.
    A promo lands hardest on a day people were already coming.
    """
    if not projection.get("available") or not projection.get("required_available"):
        return None
    candidates = [d for d in projection["days"] if d.get("gap", 0) > 0]
    if not candidates:
        return None
    return max(candidates, key=lambda d: d["snp500"])
