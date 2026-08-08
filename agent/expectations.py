"""
What a day *should* have done, given how good a beach day it was.

This is the rudimentary version on purpose. The whole problem with the early reports was reporting
revenue with no sense of whether it was any good — "$1,468, up 25%" reads as a win right up until
you remember it was a near-perfect beach Friday and should have done far better.

The anchors are Sandy's, stated plainly:

    "If it is a rainy Tuesday then I am happy to surpass 500, whereas a great beach Friday like
     yesterday I would hope to be at 2000."

So they're a gut baseline, not a fitted model — which is fine and honest, and better than no
expectation at all. Every day the agent logs expected vs actual, so after a season there's real data
to replace the guess. Adjust ANCHORS freely; nothing else needs to change.
"""

# (SNP 500 score on the published 1–500 scale, expected in-store revenue)
ANCHORS = [
    (150, 500),    # poor beach day — rainy Tuesday. Clearing $500 is a good outcome.
    (480, 2000),   # near-perfect beach day. This is the number to hope for.
]


def expected_revenue(snp_score, anchors=None):
    """
    Linear interpolation between the anchors, extended flat beyond them.

    Flat rather than extrapolated at the ends: below the low anchor there's a floor of people who
    come in regardless of weather, and above the high anchor the store runs into its own capacity.
    Straight-lining either direction would invent numbers the anchors don't support.
    """
    points = sorted(anchors or ANCHORS)
    if snp_score is None or not points:
        return None
    if snp_score <= points[0][0]:
        return float(points[0][1])
    if snp_score >= points[-1][0]:
        return float(points[-1][1])

    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= snp_score <= x1:
            span = x1 - x0
            return float(y0 if span == 0 else y0 + (y1 - y0) * (snp_score - x0) / span)
    return float(points[-1][1])


def weekday_adjusted(snp_score, day=None, curve=None, anchors=None):
    """
    Expected revenue for a given day quality, adjusted for which day of the week it is.

    A great beach Tuesday should not be held to a Saturday's number. Without this the report keeps
    "discovering" that midweek is quieter, which is something Sandy already knows and doesn't need
    explained. Factors come from measured prior-year data; absent that, the day quality stands alone.
    """
    base = expected_revenue(snp_score, anchors)
    if base is None or day is None or not curve:
        return base, 1.0
    factor = (curve.get("weekday_factor") or {}).get(str(day.weekday()))
    if not factor:
        return base, 1.0
    return base * float(factor), float(factor)


def assess(actual_revenue, snp_score, anchors=None, day=None, curve=None):
    """
    Compare what happened to what the conditions warranted.

    Returns the expectation, the ratio, and a verdict — the verdict bands are deliberately wide,
    because the anchors are a gut estimate and narrow bands would imply a precision that isn't there.
    """
    expected, weekday_factor = weekday_adjusted(snp_score, day, curve, anchors)
    if not expected or actual_revenue is None:
        return {"available": False}

    ratio = actual_revenue / expected
    if ratio >= 1.25:
        verdict = "well above what the day warranted"
    elif ratio >= 1.05:
        verdict = "above what the day warranted"
    elif ratio >= 0.90:
        verdict = "about right for the day"
    elif ratio >= 0.75:
        verdict = "slightly under what the day warranted"
    else:
        verdict = "well under what the day warranted"

    return {
        "available": True,
        "expected_revenue": round(expected),
        "actual_revenue": round(actual_revenue, 2),
        "ratio": round(ratio, 2),
        "pct_of_expected": round(ratio * 100),
        "verdict": verdict,
        "gap": round(actual_revenue - expected, 2),
        "weekday_factor": round(weekday_factor, 3),
        "weekday_adjusted": weekday_factor != 1.0,
    }
