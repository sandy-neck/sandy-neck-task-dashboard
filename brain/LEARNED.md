# Learned

Append-only. The agent adds observations here as it accumulates them across daily runs.

This file is the agent's working memory, not established truth. Entries start as hypotheses and earn
confidence by holding up over repeated days. Promote anything that proves out into `CONTEXT.md`;
delete anything that doesn't.

Format: `### YYYY-MM-DD — short claim` followed by the evidence and a confidence level.

---

### 2026-08-07 — Ice volume distorts average basket
**Confidence: medium** — consistent with one week of data, not yet tested across varied conditions.

Ice ran 33 orders / $210 in the week ending 2026-08-07 (~$6.36 per ticket), the highest order count
of any product. On days weighted toward ice, average basket falls without any change in customer
behavior worth acting on.

Aug 7 vs Jul 31 is the case in point: near-identical revenue ($1,468.65 vs $1,454.02) on very
different order counts (57 vs 40), average basket $25.68 vs $36.03. Ice mix is a candidate
explanation and should be checked before concluding baskets are shrinking.

**To test:** split average basket with and without ice, across several days of differing weather.

---

### 2026-08-07 — Online store converts near zero at current traffic
**Confidence: high on the fact, low on the cause.**

121 sessions on Aug 7 produced 0 completed checkouts. Across the week: ~700 sessions, 4 orders.
Cart additions were 0–4 per day all week.

The fact is solid. The cause is not — could be traffic quality, product mix, pricing, shipping
costs, or the checkout itself. Nothing here identifies which, and the numbers are too small for
funnel analysis to say anything reliable.

**To test:** what are those ~100 daily sessions landing on, and where are they coming from?

---

### 2026-08-08 — A morning event may lift the whole day, not just its own hour
**Confidence: low** — one Saturday against one Saturday, weather not yet controlled for.

Allie ran a pilates class in the sand area at 8am. BJ's read: small direct sales, but it "set the
tone." The hourly data is consistent with that, and the shape is more interesting than the totals.

Same hours, both ET, against the previous Saturday:

| Window | Sat 2026-08-01 | Sat 2026-08-08 (event) |
|---|---:|---:|
| 8am | 3 orders · $37.50 | 5 orders · $141.48 |
| 9am | 4 orders · $143.96 | 9 orders · $368.98 |
| 8–10am | 7 orders · $181 | 14 orders · $510 |
| Full day | 66 orders · $1,910.20 | ~95 orders · ~$2,978 (still open) |

The class hour itself was modest. The lift shows up in the **hours after it** — roughly double the
orders and 2.8x the revenue across the early window, and a day tracking ~56% past the comparable
Saturday's full total.

Worth noting what this is *not*: proof. Two Saturdays is not a pattern, weather differed, and the
store may simply have had a strong day. A plausible mechanism exists — an 8am event puts people on
the sand early, and early beach traffic is exactly what drives ice and provisions — but mechanism is
not evidence.

**To test:** log every event with its date and time, then compare the event day against
weather-matched non-event days rather than the adjacent calendar. Three or four events would make
this either real or dead. The 8–10am window is the specific thing to watch — that's where the signal
appeared, not in the class hour.

**Why it matters if true:** events would be a demand lever the business can actually pull, unlike
weather. That makes it worth measuring properly rather than on vibes.

---

### 2026-08-08 — The expectation curve has no weekday term, and weekday looks like a bigger factor than weather at the top of the range
**Confidence: medium** — clean ordering across three scored days plus two unscored Saturdays, obvious mechanism, but n is small and the Saturdays lack SNP 500 scores.

The SNP 500 → expected-revenue curve is weather-only. Three recent days with near-identical scores landed in strict weekday order as a fraction of what they "should" have done:

| Day | Score | Actual | % of expected |
|---|---:|---:|---:|
| Tue Jul 28 | 450 | $668.79 | 36% |
| Tue Aug 4 | 440 | $1,225.94 | 67% |
| Fri Aug 7 | 445 | $1,468.65 | 80% |
| Sat Aug 1 | — | $1,910.20 | — |
| Sat Aug 8 | — | ~$3,022.95 | — |

Both Saturdays cleared the entire band that the scored days sat inside, and Aug 8 nearly doubled the top of it.

The mechanism is unremarkable and that's a point in its favour: weekend visitor volume on the Cape is a demand input that operates independently of the sky. BJ's $2,000-for-a-perfect-day anchor was almost certainly formed thinking about a *weekend* perfect day — the note that generated it referenced "a great beach Friday." So the curve may be roughly right for Fri/Sat/Sun and materially too high for Mon–Thu.

**Why it matters:** two things flip. First, days like Aug 7 get labelled misses when they may be near the realistic weekday ceiling — the same inversion error in the opposite direction. Second, forward planning breaks: the week of Aug 9 has four Sun–Wed days scored 400–460 and the forecast expects ~$12.9k from the week. If a weekday discount is real, actual is likelier $10–11k, and the shortfall against the $17.8k the target needs is closer to $7k than $5k. That's the difference between "push a little" and "this week cannot be saved by weather."

**To test:** attach SNP 500 scores to every day including weekends (Aug 1 and Aug 8 are the immediate gaps), then bucket % -of-expected by weekday across 3–4 weeks. If Mon–Thu clusters materially below Fri–Sun at matched scores, add a weekday multiplier to `agent/expectations.py`. What would kill it: a weekday Exceptional day that clears 95%+ of expected, or a weekend day that lands at 50%.

**Caution:** do not over-fit to Jul 28. A 450-score day doing 36% is an outlier by any reading and may have a cause nothing to do with weekday — late July, post-holiday lull, something local. The Aug 4 / Aug 7 / Aug 8 progression is the sturdier part of the evidence.

---

### 2026-08-08 — The online store's proven sellers are Jeep apparel and off-season clothing, not beach goods
**Confidence: low-medium** — consistent across the week's small order count, plausible mechanism, but 5 orders is not a sample.

Top online-store sellers for the week ending 2026-08-07: Jeep Sun Dog long sleeve ($42.81), Jeep Duck Duck long sleeve ($42.81), Jeep Logo Pom Hat ($35.68), Jeep Beach Sunset Hat ($35), plus an SNP Lighthouse cropped sweatshirt ($49) and the online-exclusive Plovers tee ($34). Surfer Dudes at $99.96 was a single 4-unit order. Almost nothing beach-consumable, and two items (pom hat, cropped sweatshirt) are actively wrong for August on Cape Cod.

Reading: the web audience is not the person driving to Sandy Neck. It looks more like a Jeep/beach-culture apparel buyer who may never come to the store, and who is not shopping on weather. If that holds, it explains why the online funnel doesn't respond to beach days, and it points the post-Labor Day push at apparel and Jeep-community content rather than at gear.

**To test:** pull the online product mix across a rain week and a heat week. If the mix is stable regardless of weather while in-store swings hard, the two audiences are genuinely separate. Also check whether the Jeep orders ship out of state.

**What would kill it:** a run of online orders for ice-adjacent or beach-gear items, or evidence the Jeep buyers are local pickup.

---

### 2026-08-07 — Within a given week, weekday in-store revenue is a flat ceiling, not a function of weather quality
**Confidence: medium** — three consecutive weekdays with a clean natural experiment, but one week only.

Aug 4 (SNP 440) $1,226 · Aug 5 (425) $1,293 · Aug 6 (420) $1,184. A 20-point spread in day quality produced a $109 spread in revenue — noise. Aug 8 (450) did $3,023 and Aug 1 (410) did $1,910, so weekends respond to *something*, but midweek looks capped by how many people are on the Cape, not by the sky.

This refines the 2026-08-08 weekday-term note. The right correction may not be a multiplier on the curve but a **cap**: expected = min(weather curve, weekday ceiling), where the ceiling is set by the week's visitor volume. Late July weekdays capped near $700; the Aug 3 week capped near $1,200.

**Why it matters:** the week of Aug 9 has three Exceptional weekday-ish days (Sun 450, Mon 460, Tue 460) that the curve values at ~$1,900 each. Under a ceiling model they land nearer $1,300–1,900 with Sunday the only one likely to clear, and the week comes in $2–3k under forecast. That changes the target conversation from "push a little" to "the weather cannot save this week."

**To test:** next week is the test and it arrives immediately. If Mon Aug 10 and Tue Aug 11 both land near $1,200–1,400 despite scoring 460 — the best weather of the period — the ceiling is real. If either clears $1,800, the ceiling is wrong and a smooth weekday multiplier fits better.

**What would kill it:** a weekday that tracks its score upward inside a single week, or a weekend day that lands at the weekday level on a high score.

---

### 2026-08-09 — Sunday behaves like a weekday, not a weekend day, for the revenue ceiling
**Confidence: low** — two data points, and both had mediocre scores, so weather and weekday are confounded.

Jul 26 (SNP 425) did $1,159 / 32 orders. Aug 2 (SNP 395) did $859 / 34 orders. Both sit inside or below the midweek $1,200 band, nowhere near the Saturday band ($1,910 at score 410, $3,092 at 450). If Sunday really is a weekday for these purposes, the week-ahead forecast is overstating three days next week rather than two, and the Sun–Tue block should be planned around ~$1,200 each, not ~$1,860.

**To test:** Sun Aug 9 is scored 450 — Exceptional, and the highest-quality Sunday in the record. If it lands near $1,200–1,400 the claim holds; if it clears $1,800 it dies and Sunday belongs with the weekend. That's a clean single-day test and it resolves tomorrow.

---

### 2026-08-08 — The Saturday-adjusted expectation ceiling may be set too high
**Confidence: low-medium** — two Saturdays, one curve revision, no day has approached the top of the range.

With the day-of-week factor added, a 450-score Saturday now expects $3,917. Aug 8 was the best day in the entire record — $3,091.95 on 100 orders, 62% above the previous Saturday — and still came in at 79%. Aug 1 (SNP 410, $1,910) would have been well under 60% of its adjusted number.

If the best day the store has ever produced can't clear 80% of expected, the top anchor is describing a day that doesn't exist rather than a day being missed. The risk is the same inversion error the curve was built to prevent, running the other way: genuinely exceptional days get logged as underperformance and the signal stops meaning anything.

**To test:** Aug 15 (455) and the two high-scored Sundays (Aug 9 at 465, Aug 16 at 470). If three or four more weekend days all land 75–85% of expected with no obvious fault, the anchor is wrong, not the days. **What would kill it:** any weekend day clearing 95%+ — which would mean $3,700+ is genuinely reachable and Aug 8 really did leave money on the floor.

---

### 2026-08-09 — Sunday is a weekend day for revenue purposes, not a weekday
**Confidence: medium-high** — one strong data point, but it inverts a hypothesis I'd been building, and cleanly.

I'd been leaning toward "Sunday behaves like a weekday" on the strength of Aug 2 (SNP 395, $859) and Jul 26 (SNP 425, $1,159), both sitting in the midweek band. Aug 9 at SNP 450 did **$3,153 on 77 orders** — above Aug 8's Saturday at the same score.

The reconciliation is that Sundays appear **score-elastic** in a way midweek days are not. Aug 4/5/6 spanned 420–440 and produced $1,226 / $1,293 / $1,184 — a 20-point score spread moving revenue $109. Sundays spanned 395→450 and moved $859→$3,153. If that's right, weekends convert good weather into revenue and weekdays are capped by how many people are on the Cape at all.

**To test:** Aug 16 (Sun, 445) is the immediate check — it should land near $3,000, not near $900. A Sunday at 445 doing $1,000 kills this.

**Why it matters:** it changes where a promo or event is worth running. If Sundays respond to conditions and weekdays don't, spend the effort on weekend days that are already good, not on trying to rescue midweek.

### 2026-08-09 — Same-day session counts are systematically undercounted and fill in later
**Confidence: high** — direct observation of the same date reported twice.

Aug 8 read as **17 sessions** on the Aug 9 run and I flagged it as a probable tracking break against a record in-store day. On the Aug 10 run the same date reads **146**. Aug 9 now reads 18 on the same trailing position.

The trailing day in the sessions array is incomplete at read time, not broken. **Never comment on the most recent day's session count**; judge traffic on the prior day and back. This also means any week-over-week session comparison including the trailing day is understated by roughly one full day.

### 2026-08-09 — % of expected is not comparable across days of the week under the current curve
**Confidence: medium** — two adjacent days, near-identical scores, opposite verdicts.

Aug 8 (Sat, SNP 450, $3,092) scored **79% of expected**. Aug 9 (Sun, SNP 450, $3,153) scored **134% of expected**. Nearly the same revenue and the same day quality, but the day-of-week factor priced Saturday at $3,917 and Sunday at $2,356.

One of those two anchors is wrong — most likely the Saturday multiplier, since no day in the record has come near $3,917. Until the curve is refit, treat "% of expected" as a within-weekday measure only, and don't tell BJ a Saturday underperformed on that basis alone.

**What would settle it:** three or four more Saturdays. If they cluster at 75–85%, the Saturday factor is too high and should come down.
