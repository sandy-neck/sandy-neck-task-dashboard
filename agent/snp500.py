"""
SNP 500 — the Sandy Neck beach decision engine.

Implements the SNP 500 Comprehensive PRD v1.0 (August 2026).

  North Star: this is not a weather score. It is a beach decision engine. It scores the quality and
  usability of a Sandy Neck beach day, not meteorological pleasantness in the abstract.

Two consumers, one engine — per the PRD's own principle that one environmental model supports
multiple profiles:

  1. Customer-facing: the Shopify widget, via the canonical payload in `score_day()`.
  2. Internal analytics: the daily email uses the score as a denominator, so "was yesterday good?"
     is answered against beach quality rather than raw revenue.

The PRD specifies Google Sheets as the MVP computation layer while explicitly noting it "is not the
permanent product boundary". This is that migration, done early — the daily agent already ingests
weather and tides, and reproducible scoring plus the Appendix C golden-day suite are far easier to
hold onto in code. Published payload matches the PRD schema exactly.

Every threshold lives in CONFIG so weights stay tunable without touching logic.
"""
from datetime import time

ALGORITHM_VERSION = "1.1"

# The published score runs 1–500. That's the joke — the Sandy Neck Provisions 500, against the
# Standard & Poor's 500 — and the joke is the point, so it's the number customers see.
# Factor tables stay 0–100 internally because that's how the PRD specifies them; `score_100` is
# retained in the payload for debugging and calibration.
SCALE_MAX = 500


def to_scale(score_100):
    """0–100 internal → 1–500 published."""
    if score_100 is None:
        return None
    return max(1, min(SCALE_MAX, round(score_100 * SCALE_MAX / 100)))

CONFIG = {
    # PRD §5 — category weights
    "weights": {
        "weather": 0.25, "wind": 0.15, "tide": 0.20,
        "beach": 0.20, "day_extension": 0.10, "experience": 0.10,
    },
    # PRD Appendix A — subfactor shares
    "weather_shares": {"temperature": 0.40, "precipitation": 0.35, "cloud": 0.15, "dew_point": 0.10},
    "beach_shares": {"bugs": 0.55, "access": 0.25, "other": 0.20},

    "max_bonus": 8,           # Appendix A
    "max_penalty": 20,
    "rain_cap": 55,           # PRD §7 — persistent rain cap
    "thunderstorm_penalty": 18,

    # Interaction bonuses only fire when every category clears this — favorable conditions
    # "occurring together" means together, not three good ones and a disqualifying fourth.
    "bonus_floor": 70,

    # Caps for conditions that gate beach usability regardless of everything else.
    # (threshold, ceiling, explanation) — first match wins, ascending.
    "temperature_caps": [
        (55, 48, "too cold for general beach use"),
        (62, 66, "cool for the beach"),
        (68, 80, "mild rather than warm"),
    ],
    "wind_caps": [
        (26, 52, "strong wind makes a beach setup impractical"),
        (21, 72, "wind limits a comfortable beach day"),
    ],
    "bug_caps": {"high": 82, "severe": 68},

    # Explanation threshold. Factor scores skew high, so neutral sits above the midpoint:
    # a factor at 70 is a mild negative here, not "average". Calibrate with back-testing.
    "neutral": 75,
    "driver_threshold": 1.0,

    "ideal_low_tide": (time(14, 30), time(16, 30)),
    "core_beach_hours": (time(10, 0), time(18, 0)),
    "min_window_hours": 3,
}

BANDS = [
    (90, "Exceptional"), (80, "Great"), (70, "Good"),
    (60, "Mixed"), (45, "Marginal"), (0, "Poor"),
]


def _band(score: int) -> str:
    for floor, label in BANDS:
        if score >= floor:
            return label
    return "Poor"


def _table(value, breakpoints, default):
    """First matching (predicate_ceiling, score) pair. Breakpoints are ascending ceilings."""
    if value is None:
        return default
    for ceiling, score in breakpoints:
        if value <= ceiling:
            return score
    return breakpoints[-1][1] if breakpoints else default


# ── Factor scorers (PRD §6) ──────────────────────────────────────────────────
# Each returns (score, reason) so the explanation layer never reverse-engineers a result.

def score_temperature(temp_f):
    if temp_f is None:
        return 70, "temperature unknown"
    score = _table(temp_f, [
        (54.9, 20), (61, 45), (67, 65), (73, 82), (82, 100), (87, 92), (92, 78),
    ], 62)
    if temp_f > 92:
        score = 62
    labels = {100: "sweet-spot temperatures", 92: "hot but favorable near the water",
              82: "comfortable", 78: "heat reduces comfort", 65: "pleasant for walking",
              62: "heat stress concern", 45: "cool", 20: "cold for general beach use"}
    return score, labels.get(score, "temperature")


def score_precipitation(precip_prob, persistent_rain=False, thunderstorms=False):
    """precip_prob is percent chance across the core window."""
    if thunderstorms:
        return 8, "thunderstorm risk"
    if persistent_rain:
        return 12, "persistent rain"
    score = _table(precip_prob, [(0, 100), (19, 90), (39, 75), (59, 55), (79, 30)], 15)
    labels = {100: "dry", 90: "essentially dry", 75: "some rain uncertainty",
              55: "scattered showers possible", 30: "rain likely", 15: "heavy rain"}
    return score, labels.get(score, "precipitation")


def score_cloud(cloud_pct):
    if cloud_pct is None:
        return 90, "cloud cover unknown"
    # Partly sunny beats relentless full sun — 21-45% is the peak, not 0%.
    score = _table(cloud_pct, [(20, 95), (45, 100), (65, 88), (80, 72)], 55)
    labels = {100: "partly sunny", 95: "full sun", 88: "some cloud",
              72: "mostly cloudy", 55: "overcast"}
    return score, labels.get(score, "cloud cover")


def score_dew_point(dew_f):
    if dew_f is None:
        return 85, "humidity unknown"
    score = _table(dew_f, [(58, 100), (64, 90), (69, 75), (73, 58)], 40)
    labels = {100: "comfortable air", 90: "slightly humid", 75: "humid",
              58: "muggy", 40: "oppressively humid"}
    return score, labels.get(score, "humidity")


def score_wind(wind_mph):
    if wind_mph is None:
        return 85, "wind unknown"
    # 0-4 scores below 5-10: dead calm worsens bugs and heat.
    score = _table(wind_mph, [(4, 92), (10, 100), (15, 85), (20, 62), (25, 38)], 15)
    labels = {100: "comfortable breeze", 92: "calm", 85: "noticeable breeze",
              62: "windy", 38: "uncomfortably windy", 15: "strong wind"}
    return score, labels.get(score, "wind")


def score_tide(low_tide_local):
    """
    PRD §6.7. Afternoon low tide is privileged: 2:30-4:30 PM creates the broad lunch-to-dinner
    experience — outgoing tide, exposed beach at low, incoming water afterward.
    """
    if low_tide_local is None:
        return None, "no tide data"
    minutes = low_tide_local.hour * 60 + low_tide_local.minute

    def between(start_h, start_m, end_h, end_m):
        return start_h * 60 + start_m <= minutes <= end_h * 60 + end_m

    if between(14, 30, 16, 30):
        return 100, "near-ideal afternoon low tide"
    if between(13, 30, 14, 29) or between(16, 31, 17, 30):
        return 92, "strong afternoon low tide"
    if between(12, 0, 13, 29) or between(17, 31, 18, 30):
        return 80, "workable low tide"
    if between(10, 0, 11, 59):
        return 68, "late-morning low tide"
    if between(18, 31, 20, 0):
        return 65, "evening low tide"
    if between(8, 0, 9, 59):
        return 55, "early low tide"
    return 45, "low tide outside useful hours"


def score_bugs(level):
    scores = {"low": (100, "few bugs"), "moderate": (78, "some bugs toward evening"),
              "high": (48, "bugs a meaningful factor"), "severe": (20, "severe bugs")}
    return scores.get((level or "").lower(), (78, "bug level assumed moderate"))


def score_access(status):
    scores = {"open": (100, "full beach access"), "partial": (80, "some access restrictions"),
              "substantial": (55, "substantial access restrictions"),
              "closed": (40, "ORV access closed")}
    return scores.get((status or "").lower(), (100, "access assumed open"))


def score_day_extension(sunset_usable, bonfire_allowed, day_otherwise_good):
    """Sunset/bonfire adds experience value only when the day is otherwise usable (PRD §6.10)."""
    if not day_otherwise_good:
        return 50, "limited evening value"
    if sunset_usable and bonfire_allowed:
        return 95, "good sunset and bonfire window"
    if sunset_usable:
        return 82, "usable sunset"
    return 60, "limited evening extension"


# ── Engine ───────────────────────────────────────────────────────────────────

def score_day(data: dict, config: dict = None) -> dict:
    """
    Compute the SNP 500 for one day.

    Expected keys (all optional — missing inputs reduce confidence rather than crashing):
      temp_f, precip_prob, persistent_rain, thunderstorms, cloud_pct, dew_point_f, wind_mph,
      low_tide_local (datetime.time), bugs, access, sunset_usable, bonfire_allowed,
      favorable_window_hours, official_closure, closure_reason, source_freshness,
      source_completeness, source_reliability, date_local
    """
    cfg = {**CONFIG, **(config or {})}
    weights = cfg["weights"]

    confidence = compute_confidence(data)

    # PRD §7 — override precedence: official closure supersedes everything.
    if data.get("official_closure"):
        return {
            "date_local": data.get("date_local"),
            "score": None, "rating": None, "confidence": confidence,
            "status": "closure",
            "headline": data.get("closure_reason") or "Sandy Neck is closed or restricted today.",
            "algorithm_version": ALGORITHM_VERSION,
        }

    temp, temp_why = score_temperature(data.get("temp_f"))
    precip, precip_why = score_precipitation(
        data.get("precip_prob"), data.get("persistent_rain"), data.get("thunderstorms"))
    cloud, cloud_why = score_cloud(data.get("cloud_pct"))
    dew, dew_why = score_dew_point(data.get("dew_point_f"))
    wind, wind_why = score_wind(data.get("wind_mph"))
    tide, tide_why = score_tide(data.get("low_tide_local"))
    bugs, bugs_why = score_bugs(data.get("bugs"))
    access, access_why = score_access(data.get("access"))

    ws = cfg["weather_shares"]
    weather = (temp * ws["temperature"] + precip * ws["precipitation"]
               + cloud * ws["cloud"] + dew * ws["dew_point"])

    bs = cfg["beach_shares"]
    other_local, other_why = data.get("other_local_score", 85), "local conditions"
    beach = bugs * bs["bugs"] + access * bs["access"] + other_local * bs["other"]

    day_ok = weather >= 70 and wind >= 60
    extension, ext_why = score_day_extension(
        data.get("sunset_usable", True), data.get("bonfire_allowed", True), day_ok)

    # Hourly data would drive this properly; without it, approximate from the day's shape.
    window_hours = data.get("favorable_window_hours")
    experience = 85 if window_hours is None else _table(
        window_hours, [(1, 40), (2, 55), (3, 70), (4, 85), (6, 95)], 100)

    # No tide feed: redistribute its weight rather than scoring a missing input as zero.
    if tide is None:
        usable = {k: v for k, v in weights.items() if k != "tide"}
        total = sum(usable.values())
        weights = {k: v / total for k, v in usable.items()}
        tide, tide_why = 0, "no tide data"
        tide_weight = 0.0
    else:
        tide_weight = weights["tide"]

    base = (weights["weather"] * weather + weights["wind"] * wind + tide_weight * tide
            + weights["beach"] * beach + weights["day_extension"] * extension
            + weights["experience"] * experience)

    categories = {"weather": weather, "wind": wind, "beach": beach,
                  **({"tide": tide} if tide_weight else {})}
    bonus, bonus_reasons = _interaction_bonuses(
        data, tide, temp, precip, wind, extension, categories, base, cfg)
    penalty, cap, penalty_reasons = _penalties_and_caps(data, cfg)

    uncapped = base + bonus - penalty
    score = uncapped if cap is None else min(uncapped, cap)
    score = max(0, min(100, round(score)))

    factors = {"weather": round(weather), "wind": wind, "tide": tide,
               "beach": round(beach), "day_extension": extension, "experience": experience}
    reasons = {"temperature": temp_why, "precipitation": precip_why, "cloud": cloud_why,
               "dew_point": dew_why, "wind": wind_why, "tide": tide_why, "bugs": bugs_why,
               "access": access_why, "day_extension": ext_why}

    # Effective weight of each subfactor within the final score.
    w, ws_, bs_ = weights, cfg["weather_shares"], cfg["beach_shares"]
    subfactors = [
        ("temperature", temp, w["weather"] * ws_["temperature"]),
        ("precipitation", precip, w["weather"] * ws_["precipitation"]),
        ("cloud", cloud, w["weather"] * ws_["cloud"]),
        ("dew_point", dew, w["weather"] * ws_["dew_point"]),
        ("wind", wind, w["wind"]),
        ("tide", tide, tide_weight),
        ("bugs", bugs, w["beach"] * bs_["bugs"]),
        ("access", access, w["beach"] * bs_["access"]),
        ("day_extension", extension, w["day_extension"]),
    ]

    # A cap that actually binds is the dominant limiting factor and must be stated.
    binding = penalty_reasons[0] if (cap is not None and uncapped > cap and penalty_reasons) else None
    drivers_pos, drivers_neg = _rank_contributions(subfactors, cfg, binding)
    window = _best_window(data, tide, bugs, cfg)
    status = "normal" if confidence >= 50 else "provisional"

    return {
        "date_local": data.get("date_local"),
        "score": to_scale(score),      # 1–500, the published number
        "score_100": score,            # internal, for calibration and debugging
        "rating": _band(score),
        "confidence": confidence,
        "status": status,
        "best_window": window,
        "headline": _headline(score, drivers_pos, drivers_neg, reasons, window),
        "drivers_positive": [d[0] for d in drivers_pos],
        "drivers_negative": [d[0] for d in drivers_neg],
        "factors": factors,
        "factor_reasons": reasons,
        "bonus_total": round(bonus, 1),
        "penalty_total": round(penalty, 1),
        "bonus_reasons": bonus_reasons,
        "penalty_reasons": penalty_reasons,
        "algorithm_version": ALGORITHM_VERSION,
    }


def _interaction_bonuses(data, tide, temp, precip, wind, extension, categories, base, cfg):
    """
    PRD §7 — adjustments for favorable conditions *occurring together*.

    Two guardrails beyond the stated cap, both needed to keep the top of the scale meaningful:

    - Bonuses do not fire at all when any category is weak. "Ideal tide + warm + dry" is not a
      coincidence of good conditions when it is blowing 22 mph; without this, a windy day collected
      the full tide bonus and landed in Great.
    - Bonuses cannot carry a day past 99. A perfect 100 has to be earned by the base score alone,
      otherwise stacked bonuses make 100 routine and the band stops meaning anything.
    """
    weakest = min(categories.values()) if categories else 100
    if weakest < cfg["bonus_floor"]:
        return 0.0, []

    bonus, reasons = 0.0, []
    dry = precip >= 90

    if tide >= 100 and temp >= 100 and dry:
        bonus += 5
        reasons.append("ideal tide with sweet-spot temperatures and a dry day")
    if extension >= 82 and tide >= 80 and dry:
        bonus += 2
        reasons.append("good afternoon extending into a usable sunset")
    if temp >= 92 and 5 <= (data.get("wind_mph") or 0) <= 12:
        bonus += 1.5
        reasons.append("warm with a light breeze")

    hours = data.get("favorable_window_hours")
    if hours and hours >= 4:
        bonus += 3
        reasons.append(f"broad {int(hours)}-hour favorable window")

    bonus = min(bonus, cfg["max_bonus"], max(0.0, 99 - base))
    return bonus, reasons


def _penalties_and_caps(data, cfg):
    """
    PRD §7. Caps exist to prevent a misleadingly high result — the spec's example is persistent
    rain, but the same logic applies to any condition that gates beach usability outright.

    Temperature and wind need caps because their weighted share understates them. Temperature is
    40% of a 25% category, so it moves the total by only ~10 points; without a cap a 58°F day
    scored 94 on the strength of sun and tide, which is not a beach day by any reading.
    """
    penalty, cap, reasons = 0.0, None, []

    def apply_cap(value):
        return value if cap is None else min(cap, value)

    if data.get("thunderstorms"):
        penalty += cfg["thunderstorm_penalty"]
        cap = apply_cap(45)
        reasons.append("thunderstorm risk in the recommended window")
    if data.get("persistent_rain"):
        cap = apply_cap(cfg["rain_cap"])
        reasons.append("persistent rain caps the day")

    temp_f = data.get("temp_f")
    if temp_f is not None:
        for threshold, ceiling, why in cfg["temperature_caps"]:
            if temp_f < threshold:
                cap = apply_cap(ceiling)
                reasons.append(why)
                break

    wind_mph = data.get("wind_mph")
    if wind_mph is not None:
        for threshold, ceiling, why in cfg["wind_caps"]:
            if wind_mph >= threshold:
                cap = apply_cap(ceiling)
                reasons.append(why)
                break

    bugs = (data.get("bugs") or "").lower()
    if bugs == "severe":
        penalty += 6
        cap = apply_cap(cfg["bug_caps"]["severe"])
        reasons.append("severe bugs cut the evening short")
    elif bugs == "high":
        cap = apply_cap(cfg["bug_caps"]["high"])
        reasons.append("bugs limit the back half of the day")

    return min(penalty, cfg["max_penalty"]), cap, reasons


def _rank_contributions(subfactors, cfg, binding_cap_reason=None):
    """
    PRD §8: explanations must be grounded in actual scoring contributions, never generated
    independently. contribution = effective_weight × (factor_score − neutral).

    Ranked at subfactor level, matching the PRD's canonical payload ("temperature", "evening_bugs")
    rather than whole categories. Category-level ranking hides the thing that actually matters: a
    58°F day scored 77 on weather because sun and dry air masked the cold, so nothing surfaced as
    limiting and the customer got a low score with no stated reason.

    A binding cap is by definition the dominant negative contribution, so it leads.
    """
    neutral = cfg["neutral"]
    contributions = [
        (name, weight * (score - neutral))
        for name, score, weight in subfactors
        if weight > 0
    ]

    positives = sorted([c for c in contributions if c[1] > cfg["driver_threshold"]],
                       key=lambda c: c[1], reverse=True)[:3]
    negatives = sorted([c for c in contributions if c[1] < -cfg["driver_threshold"]],
                       key=lambda c: c[1])[:2]

    if binding_cap_reason:
        negatives = [(binding_cap_reason, None)] + [
            n for n in negatives if n[0] != binding_cap_reason
        ][:1]
    return positives, negatives


def _best_window(data, tide, bugs, cfg):
    """
    Approximate best window. Real hourly scoring is a post-MVP item (PRD §8); this anchors on the
    low tide and pulls the end in when bugs make the evening unpleasant.
    """
    low_tide = data.get("low_tide_local")
    if data.get("thunderstorms") or data.get("persistent_rain") or low_tide is None:
        return None

    center = low_tide.hour + low_tide.minute / 60
    start = max(9.0, center - 2)
    end = min(20.0, center + 2.5)
    if (data.get("bugs") or "").lower() in ("high", "severe"):
        end = min(end, 18.0)
    if end - start < cfg["min_window_hours"]:
        return None

    def fmt(hours):
        return f"{int(hours):02d}:{int(round((hours % 1) * 60)):02d}"

    return {"start": fmt(start), "end": fmt(end)}


def compute_confidence(data) -> int:
    """PRD §7 — data quality, deliberately separate from beach quality."""
    freshness = data.get("source_freshness", 100)
    reliability = data.get("source_reliability", 90)
    completeness = data.get("source_completeness")
    if completeness is None:
        expected = ["temp_f", "precip_prob", "wind_mph", "low_tide_local", "bugs"]
        present = sum(1 for key in expected if data.get(key) is not None)
        completeness = present / len(expected) * 100
    return max(0, min(100, round(0.50 * freshness + 0.30 * completeness + 0.20 * reliability)))


def _headline(score_100, positives, negatives, reasons, window):
    band = _band(score_100)
    score = to_scale(score_100)
    if positives:
        lead = ", ".join(reasons.get(name, name) for name, _ in positives[:2])
        sentence = f"{lead.capitalize()}"
    else:
        sentence = "Conditions are mixed"
    if window:
        sentence += f", best {window['start']}–{window['end']}"
    if negatives:
        limiter = reasons.get(negatives[0][0], negatives[0][0])
        sentence += f", though {limiter} keeps it out of the top band"
    return f"{score} — {band}. {sentence}."
