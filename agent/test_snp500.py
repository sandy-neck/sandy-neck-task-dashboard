"""
Golden-day tests — SNP 500 PRD Appendix C.

Per PRD §11: every algorithm change runs against this set to detect unintended drift. These assert
bands and behaviour, not exact integers, so calibration can move numbers without breaking the suite.

Run: python test_snp500.py
"""
from datetime import time
from snp500 import score_day, _band, SCALE_MAX

CASES = []


def case(name):
    def wrap(fn):
        CASES.append((name, fn))
        return fn
    return wrap


@case("Ideal summer — 78F, dry, 7mph, low tide 3:30, low bugs → likely 90+")
def ideal_summer():
    r = score_day({
        "date_local": "2026-07-15", "temp_f": 78, "precip_prob": 0, "cloud_pct": 30,
        "dew_point_f": 60, "wind_mph": 7, "low_tide_local": time(15, 30), "bugs": "low",
        "access": "open", "favorable_window_hours": 6,
    })
    assert r["score_100"] >= 90, f"expected Exceptional, got {r['score']}"
    assert 1 <= r["score"] <= SCALE_MAX, f"published score must be 1-500: {r['score']}"
    named = set(r["drivers_positive"])
    assert named & {"tide", "temperature", "wind"}, f"drivers should name tide/temp/wind: {named}"
    return r


@case("Pretty but windy — 76F sunny, 22mph, good tide → wind holds it below Great")
def pretty_but_windy():
    r = score_day({
        "date_local": "2026-07-20", "temp_f": 76, "precip_prob": 0, "cloud_pct": 15,
        "dew_point_f": 60, "wind_mph": 22, "low_tide_local": time(15, 0), "bugs": "low",
        "access": "open",
    })
    assert r["score_100"] < 80, f"wind should keep it below Great, got {r['score']}"
    assert any("wind" in d for d in r["drivers_negative"]), f"wind should be named limiting: {r['drivers_negative']}"
    return r


@case("Rain + ideal tide — rain cap prevents a misleadingly high score")
def rain_ideal_tide():
    r = score_day({
        "date_local": "2026-07-22", "temp_f": 75, "precip_prob": 85, "persistent_rain": True,
        "cloud_pct": 95, "dew_point_f": 70, "wind_mph": 10, "low_tide_local": time(15, 0),
        "bugs": "low", "access": "open",
    })
    assert r["score_100"] <= 55, f"rain cap should bind at 55, got {r['score']}"
    assert any("rain" in x for x in r["penalty_reasons"]), r["penalty_reasons"]
    return r


@case("Buggy sunset — 80F calm, high bugs after 6 → earlier window, evening reduced")
def buggy_sunset():
    r = score_day({
        "date_local": "2026-07-25", "temp_f": 80, "precip_prob": 0, "cloud_pct": 25,
        "dew_point_f": 64, "wind_mph": 3, "low_tide_local": time(15, 30), "bugs": "high",
        "access": "open",
    })
    assert r["best_window"] is not None
    assert r["best_window"]["end"] <= "18:00", f"window should pull in: {r['best_window']}"
    assert any("bug" in d for d in r["drivers_negative"]), f"bugs should limit: {r['drivers_negative']}"
    return r


@case("Stale bug data — otherwise excellent → quality holds, confidence falls")
def stale_bugs():
    fresh = score_day({
        "date_local": "2026-07-28", "temp_f": 78, "precip_prob": 0, "cloud_pct": 30,
        "dew_point_f": 58, "wind_mph": 8, "low_tide_local": time(15, 30), "bugs": "low",
        "access": "open",
    })
    stale = score_day({
        "date_local": "2026-07-28", "temp_f": 78, "precip_prob": 0, "cloud_pct": 30,
        "dew_point_f": 58, "wind_mph": 8, "low_tide_local": time(15, 30), "bugs": "low",
        "access": "open", "source_freshness": 30,
    })
    assert stale["confidence"] < fresh["confidence"], "stale source must reduce confidence"
    assert stale["score"] == fresh["score"], "confidence must not alter quality"
    return stale


@case("Official closure — perfect weather, closed → closure supersedes score")
def official_closure():
    r = score_day({
        "date_local": "2026-07-30", "temp_f": 78, "precip_prob": 0, "wind_mph": 7,
        "low_tide_local": time(15, 30), "bugs": "low",
        "official_closure": True, "closure_reason": "Beach closed — piping plover nesting.",
    })
    assert r["status"] == "closure", r["status"]
    assert r["score"] is None, "closure must not publish a normal score"
    assert "plover" in r["headline"]
    return r


@case("Cold clear spring — 58F sunny, light wind → moderate, not inflated by sun")
def cold_clear_spring():
    r = score_day({
        "date_local": "2026-04-12", "temp_f": 58, "precip_prob": 0, "cloud_pct": 10,
        "dew_point_f": 45, "wind_mph": 8, "low_tide_local": time(15, 0), "bugs": "low",
        "access": "open",
    })
    assert r["score_100"] < 70, f"sun must not inflate a cold day, got {r['score']}"
    assert any(d=="temperature" or "cold" in d for d in r["drivers_negative"]), r["drivers_negative"]
    return r


@case("No tide feed — excellent weather, tide unavailable → fallback, confidence drops")
def no_tide_feed():
    r = score_day({
        "date_local": "2026-08-02", "temp_f": 79, "precip_prob": 0, "cloud_pct": 30,
        "dew_point_f": 60, "wind_mph": 8, "bugs": "low", "access": "open",
    })
    assert r["score"] is not None, "must still produce a score without tide"
    assert r["confidence"] < 100, "missing source must reduce confidence"
    assert r["best_window"] is None, "no tide means no confident window"
    return r


@case("90+ stays special — an ordinary pleasant day must not score Exceptional")
def ordinary_day_not_exceptional():
    r = score_day({
        "date_local": "2026-06-18", "temp_f": 72, "precip_prob": 15, "cloud_pct": 55,
        "dew_point_f": 66, "wind_mph": 12, "low_tide_local": time(11, 0), "bugs": "moderate",
        "access": "open",
    })
    assert r["score_100"] < 90, f"ordinary day must not hit Exceptional, got {r['score']}"
    return r


def main():
    print("SNP 500 — golden-day tests (PRD Appendix C)\n" + "=" * 68)
    failures = 0
    for name, fn in CASES:
        try:
            r = fn()
            detail = (f"{r['score']:>3} {r['rating']:<12} conf {r['confidence']:>3}"
                      if r.get("score") is not None else f"    {r['status']:<12}")
            print(f"  PASS  {detail}  {name}")
        except AssertionError as e:
            failures += 1
            print(f"  FAIL  {name}\n          {e}")
        except Exception as e:
            failures += 1
            print(f"  ERROR {name}\n          {type(e).__name__}: {e}")

    print("=" * 68)
    print(f"{len(CASES) - failures}/{len(CASES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
