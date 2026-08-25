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

---

### 2026-08-08 — The online store's proven sellers are Jeep apparel and off-season clothing, not beach goods
**Confidence: low-medium** — consistent across the week's small order count, plausible mechanism, but 5 orders is not a sample.

Top online-store sellers for the week ending 2026-08-07: Jeep Sun Dog long sleeve ($42.81), Jeep Duck Duck long sleeve ($42.81), Jeep Logo Pom Hat ($35.68), Jeep Beach Sunset Hat ($35), plus an SNP Lighthouse cropped sweatshirt ($49) and the online-exclusive Plovers tee ($34). Surfer Dudes at $99.96 was a single 4-unit order. Almost nothing beach-consumable, and two items (pom hat, cropped sweatshirt) are actively wrong for August on Cape Cod.

Reading: the web audience is not the person driving to Sandy Neck. It looks more like a Jeep/beach-culture apparel buyer who may never come to the store, and who is not shopping on weather. If that holds, it explains why the online funnel doesn't respond to beach days, and it points the post-Labor Day push at apparel and Jeep-community content rather than at gear.

**To test:** pull the online product mix across a rain week and a heat week. If the mix is stable regardless of weather while in-store swings hard, the two audiences are genuinely separate. Also check whether the Jeep orders ship out of state.

**What would kill it:** a run of online orders for ice-adjacent or beach-gear items, or evidence the Jeep buyers are local pickup.

---

---

### 2026-08-07 — Within a given week, weekday in-store revenue is a flat ceiling, not a function of weather quality
**Confidence: medium** — three consecutive weekdays with a clean natural experiment, but one week only.

Aug 4 (SNP 440) $1,226 · Aug 5 (425) $1,293 · Aug 6 (420) $1,184. A 20-point spread in day quality produced a $109 spread in revenue — noise. Aug 8 (450) did $3,023 and Aug 1 (410) did $1,910, so weekends respond to *something*, but midweek looks capped by how many people are on the Cape, not by the sky.

This refines the 2026-08-08 weekday-term note. The right correction may not be a multiplier on the curve but a **cap**: expected = min(weather curve, weekday ceiling), where the ceiling is set by the week's visitor volume. Late July weekdays capped near $700; the Aug 3 week capped near $1,200.

**Why it matters:** the week of Aug 9 has three Exceptional weekday-ish days (Sun 450, Mon 460, Tue 460) that the curve values at ~$1,900 each. Under a ceiling model they land nearer $1,300–1,900 with Sunday the only one likely to clear, and the week comes in $2–3k under forecast. That changes the target conversation from "push a little" to "the weather cannot save this week."

**To test:** next week is the test and it arrives immediately. If Mon Aug 10 and Tue Aug 11 both land near $1,200–1,400 despite scoring 460 — the best weather of the period — the ceiling is real. If either clears $1,800, the ceiling is wrong and a smooth weekday multiplier fits better.

**What would kill it:** a weekday that tracks its score upward inside a single week, or a weekend day that lands at the weekday level on a high score.

---

---

### 2026-08-09 — Sunday behaves like a weekday, not a weekend day, for the revenue ceiling
**Confidence: low** — two data points, and both had mediocre scores, so weather and weekday are confounded.

Jul 26 (SNP 425) did $1,159 / 32 orders. Aug 2 (SNP 395) did $859 / 34 orders. Both sit inside or below the midweek $1,200 band, nowhere near the Saturday band ($1,910 at score 410, $3,092 at 450). If Sunday really is a weekday for these purposes, the week-ahead forecast is overstating three days next week rather than two, and the Sun–Tue block should be planned around ~$1,200 each, not ~$1,860.

**To test:** Sun Aug 9 is scored 450 — Exceptional, and the highest-quality Sunday in the record. If it lands near $1,200–1,400 the claim holds; if it clears $1,800 it dies and Sunday belongs with the weekend. That's a clean single-day test and it resolves tomorrow.

---

---

### 2026-08-08 — The midweek revenue ceiling is a basket-size ceiling, not a footfall ceiling
**Confidence: medium** — clean within-week contrast with a clear mechanism, but one week and no ice-split yet.

Across Aug 4–7 (SNP 440/425/420/445) revenue sat in a $1,184–$1,469 band while order count ranged 22 → 31 → 25 → 57. Aug 7 had 2.6x Aug 4's transactions for 20% more revenue; AOV $25.68 vs $55.06. Aug 1 (Sat, 410) did 66 orders and Aug 7 nearly matched it on count, but not on dollars.

So the constraint on a good midweek day is not how many people come through the door — Friday proved the door can do near-Saturday volume — it's what each one spends. The likely mechanism is composition: hot beach days pull a high-frequency, low-ticket, ice-and-go customer, and that customer dilutes the average faster than they add to the total. Which means the lever on those days is attachment at the point of the cheap purchase, not more traffic.

**To test:** split each day's AOV into ice-containing and non-ice tickets across Aug 4 (low count), Aug 7 (high count) and Aug 8 (100 orders). If the non-ice basket is stable across all three and only the ice share moves, this is composition and the attachment play is right. If the non-ice basket itself falls on high-footfall days, something else is happening — queue length, staff attention, stockouts — and the fix is operational instead.

**What would kill it:** a high-order-count day that also posts a high AOV, or finding the ice tickets already carry a second item.

---

---

### 2026-08-08 — The Saturday-adjusted expectation ceiling may be set too high
**Confidence: low-medium** — two Saturdays, one curve revision, no day has approached the top of the range.

With the day-of-week factor added, a 450-score Saturday now expects $3,917. Aug 8 was the best day in the entire record — $3,091.95 on 100 orders, 62% above the previous Saturday — and still came in at 79%. Aug 1 (SNP 410, $1,910) would have been well under 60% of its adjusted number.

If the best day the store has ever produced can't clear 80% of expected, the top anchor is describing a day that doesn't exist rather than a day being missed. The risk is the same inversion error the curve was built to prevent, running the other way: genuinely exceptional days get logged as underperformance and the signal stops meaning anything.

**To test:** Aug 15 (455) and the two high-scored Sundays (Aug 9 at 465, Aug 16 at 470). If three or four more weekend days all land 75–85% of expected with no obvious fault, the anchor is wrong, not the days. **What would kill it:** any weekend day clearing 95%+ — which would mean $3,700+ is genuinely reachable and Aug 8 really did leave money on the floor.

---

---

### 2026-08-09 — Sunday is a weekend day for revenue purposes, not a weekday
**Confidence: medium-high** — one strong data point, but it inverts a hypothesis I'd been building, and cleanly.

I'd been leaning toward "Sunday behaves like a weekday" on the strength of Aug 2 (SNP 395, $859) and Jul 26 (SNP 425, $1,159), both sitting in the midweek band. Aug 9 at SNP 450 did **$3,153 on 77 orders** — above Aug 8's Saturday at the same score.

The reconciliation is that Sundays appear **score-elastic** in a way midweek days are not. Aug 4/5/6 spanned 420–440 and produced $1,226 / $1,293 / $1,184 — a 20-point score spread moving revenue $109. Sundays spanned 395→450 and moved $859→$3,153. If that's right, weekends convert good weather into revenue and weekdays are capped by how many people are on the Cape at all.

**To test:** Aug 16 (Sun, 445) is the immediate check — it should land near $3,000, not near $900. A Sunday at 445 doing $1,000 kills this.

**Why it matters:** it changes where a promo or event is worth running. If Sundays respond to conditions and weekdays don't, spend the effort on weekend days that are already good, not on trying to rescue midweek.

---

### 2026-08-09 — Same-day session counts are systematically undercounted and fill in later
**Confidence: high** — direct observation of the same date reported twice.

Aug 8 read as **17 sessions** on the Aug 9 run and I flagged it as a probable tracking break against a record in-store day. On the Aug 10 run the same date reads **146**. Aug 9 now reads 18 on the same trailing position.

The trailing day in the sessions array is incomplete at read time, not broken. **Never comment on the most recent day's session count**; judge traffic on the prior day and back. This also means any week-over-week session comparison including the trailing day is understated by roughly one full day.

---

### 2026-08-09 — % of expected is not comparable across days of the week under the current curve
**Confidence: medium** — two adjacent days, near-identical scores, opposite verdicts.

Aug 8 (Sat, SNP 450, $3,092) scored **79% of expected**. Aug 9 (Sun, SNP 450, $3,153) scored **134% of expected**. Nearly the same revenue and the same day quality, but the day-of-week factor priced Saturday at $3,917 and Sunday at $2,356.

One of those two anchors is wrong — most likely the Saturday multiplier, since no day in the record has come near $3,917. Until the curve is refit, treat "% of expected" as a within-weekday measure only, and don't tell BJ a Saturday underperformed on that basis alone.

**What would settle it:** three or four more Saturdays. If they cluster at 75–85%, the Saturday factor is too high and should come down.

---

---

### 2026-08-10 — Midweek in-store revenue is flat against day quality across the entire top of the SNP 500 range
**Confidence: high (upgraded from medium)** — two independent weeks, and the second one tested a 65-point spread in day quality.

Aug 10 scored 485 — the highest day quality in the whole record, no limiting factors, near-ideal afternoon low tide — and did $1,260.46 on 25 orders. Aug 4 (440) $1,226, Aug 5 (425) $1,293, Aug 6 (420) $1,184. Four Mon–Thu days spanning 420–485 landed inside a $109 range. The previous week's version of this finding covered a 20-point spread and could be dismissed as noise; a 65-point spread producing the same flat line cannot.

Meanwhile weekends at similar scores went $3,092 (Sat 450) and $3,153 (Sun 450) — 2.5x the weekday level. So the store clearly *can* do more; midweek is not capacity-limited at the register, it is limited by how many people are on the Cape.

**What this changes:**
1. The expectation curve's weather term should be treated as near-zero for Mon–Thu. A midweek day at 87% of a weather-derived expectation is the ceiling being hit, not a miss. Stop writing midweek gaps as shortfalls.
2. Forward forecasting for midweek should use the weekday cluster level (~$1,300 in a strong vacation week, ~$700 in a weak one), not the score. This week's expected total of $12,432 contains roughly $2.5k of phantom revenue for that reason.
3. The only midweek lever left is something that changes who is at the store, not something that responds to weather — i.e. events, or capturing more of the people already on the beach.

**What would kill it:** a Mon–Thu day clearing $1,800+ without an event or a holiday. That has not happened in 12 weeks of data.

**Still unknown:** whether the cluster level itself is predictable week to week (it moved $700 → $1,300 between late July and early August), and whether an event can break it. The second question has now gone untested twice — Aug 10 was the ideal slot and no class ran.

---

---

### 2026-08-11 — Peak-season weekday in-store revenue is a hard flat ceiling around $1,250, independent of day quality
**Confidence: high** — five weekday points across two separate weeks, 65-point SNP spread, $109 revenue spread.

Aug 4 (440) $1,226 · Aug 5 (425) $1,293 · Aug 6 (420) $1,184 · Aug 10 (485) $1,260 · Aug 11 (475) $1,273. Two of those (Aug 10, 11) are the two highest-scored days in the entire record and neither beat a 420-score Thursday by more than $90.

Mechanism: midweek in-store demand is set by how many people are on the Cape, not by the weather. Weekends are genuinely score-elastic (Aug 8 @450 → $3,092, Aug 9 @450 → $3,153, Aug 2 @395 → $859), so this is a weekday-specific ceiling, not a store-capacity ceiling.

**Practical consequences, both of which change decisions:**
1. Stop calling midweek days misses or wins on % of expected. A 475-score Tuesday doing $1,273 is the ceiling, not performance.
2. Any forward forecast that prices midweek Exceptional days at $1,700–$2,000 overstates the week by ~$500 per weekday. For the week of Aug 13–19 that's ~$2k of phantom revenue, turning a stated $207 shortfall into ~$2.5k. Gaps must be closed on weekend days or not at all.

**What would kill it:** a Mon–Thu day clearing $1,600+ during peak. Worth watching whether an event (a morning class) can break it — that's the only untested lever, and Aug 10 was meant to be that test but no class ran.

**Scope limit:** peak season only, 420–485 band. Says nothing about shoulder-season weekdays or about marginal-weather weekdays (Aug 3 @275 did $297, so the floor drops away well below the ceiling).

---

---

### 2026-08-12 — The midweek "flat ceiling" is a ceiling, not a floor: order count can collapse on a top-quality day
**Confidence: medium** — one clean counter-example against five supporting days, cause unidentified.

Mon–Thu peak days at SNP 420–485 had produced $1,226 / $1,293 / $1,184 / $1,260 / $1,273 — a $109 band across a 65-point score spread. I had begun treating ~$1,250 as a dependable midweek number and using it to discount the week-ahead forecast. Aug 12 (SNP 465) did $805.91 on **14 orders**, roughly half the transaction count of comparable days, while AOV hit a record $56.93.

The direction of the AOV move is the informative part. If visitor volume simply thinned, the mix should have stayed ice-heavy and low-ticket; instead the ticket went up, which is the signature of fewer *hours* rather than fewer *people* — only committed buyers in the door.

**What this changes:** midweek forecasting should use ~$1,250 as an upper bound with meaningful downside, not a point estimate. It also means an unexplained low-order day is worth asking about immediately, because the operational explanation and the demand explanation have opposite implications for the last nine days of peak.

**To confirm or kill:** BJ's answer on Wednesday's hours. If hours were normal and Thu Aug 13 (425) also comes in under 20 orders, midweek footfall is genuinely falling as peak ends and the ceiling model needs a late-August decay term. If hours were short, this is a scratch and the five-day band stands.

---

---

### 2026-08-13 — The midweek revenue "ceiling" is a ceiling only; a floor can drop out with no weather cause
**Confidence: medium** — two consecutive days, clear mechanism candidate, but cause unconfirmed.

Aug 4–11 established Mon–Thu doing $1,250 ± $50 across a 65-point SNP spread (high confidence, held across two weeks). Aug 12 (SNP 465) did $806 and Aug 13 (SNP 420) did $922 — $330–450 below the bottom of that band, on days that scored inside or above it.

The break is entirely in transaction count: 14 and 19 orders, versus 22–38 for every other August weekday. AOV moved the *opposite* way — $56.93 and $46.42, the two highest in the record.

That divergence is diagnostic. A genuine drop in visitors should preserve the mix (ice at ~$6 a ticket is the highest-frequency line) and therefore hold AOV roughly flat or lower. Losing the cheap tickets while keeping the hard-goods buyers is what you'd see if the store were open fewer hours, or open only across the productive part of the day.

**So the correct formulation is: weather sets a midweek ceiling of ~$1,250 that better weather cannot exceed, but operational factors can take a day well below it, and weather explains none of the downside.**

**To confirm or kill:** BJ's answer on Wed/Thu hours. If hours were normal, this is a demand break nine days from the end of peak and the whole late-August read changes. If hours were short, log the hours alongside SNP going forward — open-hours is a missing input to the expectation curve and probably a bigger term than the weather.

---

---

### 2026-08-14 — The mid-August order-count trough was operational, not demand
**Confidence: medium-high** — a clean rebound on a lower-quality day.

Aug 12 (SNP 465) 14 orders, Aug 13 (420) 19 orders — both far under the 22–38 weekday band. Aug 14 (435, *lower* score than Aug 12) did 41 orders, the highest weekday count of the month. Demand does not collapse for two days and rebound 3x on a worse day; hours, staffing or a one-off closure does.

Supporting detail: AOV moved *inverse* to order count across the trough ($56.93, $46.42, then $34.10 on the rebound). Fewer transactions with bigger baskets is the signature of a store open fewer hours serving committed buyers, not of thinner crowds — thinner crowds would preserve the ice-heavy low-ticket mix and pull AOV down, not up.

**What would kill it:** BJ confirming the store was open normal hours on Aug 12–13, which would make it a genuine two-day demand hole and mean the mid-August rebound is luck rather than mechanism.

---

### 2026-08-14 — TikTok reach is collapsing monotonically ahead of the off-season plan that depends on it
**Confidence: high on the trend, unknown on the cause.**

Eight consecutive weekly declines in TikTok revenue: $185.70 → $127.79 → $103.83 → $89.85 → $71.88 → $41.93 → $29.95 → $17.97. Down 90%. Every single order across the whole run is Sun Bum air fresheners — the mix has never diversified, so this is one product's algorithmic distribution decaying, not a channel broadening or narrowing.

The dollars were never the point; the channel is held for reach. But the documented off-season plan (post-Labor Day: lean heavily into TikTok, online store, Instagram) assumes reach exists. On this curve it will be near zero by mid-September, which is precisely when it is needed.

**What would confirm:** TikTok views/follower data, which is not currently wired in — that would separate "algorithm stopped pushing" from "product fatigue." **What would kill it:** a spurt in a non-air-freshener product (Waboba and salty gem rings are the historical candidates), which would show the account still has distribution and the decline is product-specific.

---

---

### 2026-08-15 — At matched SNP 500, a weekend day does roughly $750–1,100 more in-store than a weekday
**Confidence: medium-high** — first clean matched-score weekend/weekday comparison, plus consistent supporting spread across the month.

Aug 15 (Sat, SNP 420) $2,037.60 / 55 orders vs Aug 13 (Thu, SNP 420) $921.87 / 19 orders and Aug 6 (Thu, SNP 420) $1,184.00 / 25 orders. Identical score, same week, same phase — a $854–1,116 gap. This is the direct evidence the earlier weekday-multiplier note (2026-08-08) was missing, because it no longer relies on unscored Saturdays.

Related and separable: weekends appear to *respond* to score while weekdays do not. Aug 8 (450) $3,092 vs Aug 15 (420) $2,038 — a 30-point gap producing ~$1,050 — against Mon–Thu Aug 4–13 sitting in a $806–1,293 band across scores 420–485.

**What would confirm:** two or three more matched-score weekend/weekday pairs holding the same gap. **What would kill it:** a high-scored Saturday landing inside the weekday band, or the Aug 8 figure turning out to be event-driven rather than weather-driven (which would shrink the weekend response coefficient without touching the level difference).

---

### 2026-08-15 — TikTok has declined monotonically to zero over nine weeks
**Confidence: high on the fact.** $185.70 → $127.79 → $103.83 → $89.85 → $71.88 → $41.93 → $29.95 → $17.97 → $0. Nine consecutive weekly declines, no reversals.

Every one of those orders was Sun Bum air fresheners, so what died is a single algorithmic push, not a channel with a diversified base. Cause unknown — could be the algorithm moving on, could be posting cadence falling off during peak season. That distinction matters a lot, because the off-season plan (CONTEXT.md) explicitly leans on TikTok reach.

**To test:** compare posting frequency June vs August. If cadence collapsed, this is fixable and self-inflicted. If cadence held and reach still died, the product-level push is gone and the off-season plan needs a different anchor.

---

---

### 2026-08-16 — Sunday may be a Cape changeover day that underperforms Saturday, independent of weather
**Confidence: low** — n=2 and the two Sundays are wildly split; a plausible mechanism but no real evidence yet.

Aug 16 (SNP 415) did $788 / 19 orders — below every matched-score day this month including weekdays, and below Sat Aug 15 (SNP 420) by $1,250 on 36 fewer orders. That breaks the weekend premium that had held on every weekend day in the record. Aug 9 (SNP 450, $3,153 / 77) was the opposite, but it sat mid-run of the strongest weekend on file.

Mechanism: Cape rental weeks turn over Saturday–Sunday. Departing renters are packing and driving, arriving renters aren't on the sand until Monday. If real, Sunday should look like a weekday in transaction count while Saturday carries the weekend premium.

Confounded here by the ice collapse (weekly ice orders 54 → 39 → 24), which points at falling visitor volume generally, and by an unanswered question about Sunday store hours. Either could account for the whole gap.

**To test:** bucket % -of-expected by Sat vs Sun at matched SNP scores. Only Aug 22/23 remain in peak, so this may have to wait for the shoulder or next season. **What would kill it:** a Sunday clearing the matched-score weekday set by the usual $750+, or BJ confirming reduced Sunday hours.

---

---

### 2026-08-17 — Ice order count is a leading indicator of visitor volume, and it turned down ~3 weeks before the calendar phase change
**Confidence: medium-high** — seven consecutive weeks of data, clean monotonic decline, and the confound (the Aug 12/13 low-transaction days) has now been ruled out by a second mid-20s week.

Weekly ice orders: 62 → 61 → 59 → 54 → 39 → 24 → 25. A −60% move across six weeks on days that have mostly continued to score 410–485 on the SNP 500. Ice is a near-pure beach-trip proxy (tiny ticket, high frequency, nobody buys it who isn't going out), so weather-controlled decline in ice orders is close to a direct measurement of how many people are on the Cape.

Over the same window, total daily order counts fell from the 25–57 band to a 14–25 band on weekdays, while AOV held or rose. Revenue fell less than footfall because baskets got bigger — which means revenue alone masks the turn by two or three weeks.

**Why it matters:** the phase table says Early shoulder starts Aug 23. Ice says it started around Aug 5–10. If ice leads reliably, it is the earliest signal available for when to cut hours, stop reordering consumables and shift to weekend-only — decisions that otherwise get made on the calendar or on a revenue drop that arrives late.

**To test:** track weekly ice orders through the shoulder and into next season's ramp. If ice rises 2–3 weeks ahead of the June revenue climb the same way it fell ahead of the August decline, it's a genuine leading indicator in both directions. Compare against an independent footfall measure (beach permits, ORV counts) if one can be obtained.

**What would kill it:** a supply-side explanation — a freezer outage, a price change, a competitor selling ice closer to the gate, or ice simply being out of stock on the low days. I have not checked stock levels against these weeks and should. Also killed if ice recovers to 50+ orders in a week while total footfall stays flat.

---

---

### 2026-08-18 — The expectation curve over-predicts systematically once visitor volume turns, independent of weather score
**Confidence: medium** — six consecutive days of the same directional error, clean mechanism, but one season and one turn.

Last six scored days, actual as % of expected: Aug 13 (420) ~?, Aug 14 (435) ~?, Aug 15 (420) 56%, Aug 16 (415) 37%, Aug 17 (410) 64%, Aug 18 (425) 53%. Every one materially under, across weekdays and weekends, across scores 410–435. Earlier in August the same curve was producing 67–80% on comparable scores, and in late July it produced a 36% outlier that I flagged as unexplained.

The curve knows the sky and the weekday. It does not know how many people are on the Cape. As the season turns, the population term falls while the weather term stays high — Cape weather in late August is often better than July — so the curve keeps pricing days at peak-season levels while the actual customer base drains. That produces exactly this pattern: a widening, one-directional gap that correlates with date rather than score.

Corroborating independent signal: ice weekly orders 62 → 61 → 59 → 54 → 39 → 24 → 25 → 24 across the same window, on days still scoring 410+. Ice is the beach-trip proxy and it is not weather-driven right now.

**Why it matters:** if true, every "% of expected" figure from roughly Aug 13 onward is measuring the season turning, not the store underperforming. Emails that lead with "53% of expected" are quietly telling BJ he had a bad day when he had a normal shoulder day. That's the same inversion error the whole expectation framework exists to prevent, running in the opposite direction.

**To test:** plot % -of-expected against date for all scored days since Aug 1 and check whether the trend is monotonic with date independent of score. If it is, the fix is a season-position multiplier in `agent/expectations.py` — but do not change the curve without BJ, and log any change in CONTEXT's curve-change table.

**What would kill it:** a Great-rated day in the next week clearing 90%+ of expected. Thu Aug 20 (460) and Fri Aug 21 (465) are the immediate tests — if either lands near $1,900 the curve is fine and the last week was something else.

---

### 2026-08-18 — Peak demand steps down around mid-August, roughly a week before the phase calendar says
**Confidence: medium** — four consecutive weather-matched days, plus an independent footfall proxy, but only one season of data.

Aug 15–19 ran $2,038 (Sat), $788, $789, $475, $773 on SNP scores of 410–425. Eight days earlier the same score band produced $1,260 (Aug 10, score 485), $1,273 (Aug 11, 475), $922 (Aug 13, 420). Realised revenue against the expectation curve fell from ~70–80% to ~50–55% with no change in weather quality.

Ice confirms it independently and it's the better signal because it's a pure trip proxy: 26 orders / 57 units in the 7 days to Aug 18, against 56 orders / 133 units in the week to Aug 7. Order count more than halved. AOV held ($31.68 vs $25.68) — so this is fewer people, not thinner baskets. That distinguishes it from the midweek basket-ceiling effect logged Aug 8, which was the opposite shape.

The context file puts early shoulder at Aug 23. The data says the transition began around Aug 15–16.

**What would confirm it:** the week of Aug 24 has four Exceptional-rated days (455, 450, 465, 460 area). If those land at $700–1,000 rather than the $1,800–1,900 the curve expects, the step-down is real and the phase boundary needs moving. **What would kill it:** any of those days clearing $1,500, which would make this week a one-off — bad tides, a local event elsewhere, or noise.

**Why it matters:** it changes staffing, hours, and the shoulder-season ordering window by a full week, and it means the expectation curve needs a season-position term, not just weather and weekday. Until then, every late-August day will read as a miss when it may be at the realistic ceiling.

---

### 2026-08-19 — The mid-August footfall drop is a step to a new level, not a continuing slide
**Confidence: medium** — three weeks of a flat footfall proxy, one season of data.

Ice order count (the cleanest trip proxy) ran 62 → 61 → 59 → 54 → 39 → 24 → 25 → 26 across weekly buckets. The fall happened between roughly Aug 5 and Aug 13; the last three weeks are flat at 24–26. Revenue behaves the same way: weekday in-store has sat at $475–$922 for six consecutive days on scores spanning 410–465, and Aug 19 ($871, score 420) beat Aug 12 ($806, score 465).

I spent four days reporting this as a decline. It isn't one any more — it's a plateau roughly half the early-August level. That changes the framing on everything downstream: a $800 weekday is now *normal*, not a miss, and the expectation curve's weather term has near-zero explanatory power inside this band.

**What would confirm it:** ice holding at 24–28 orders/week through the Aug 24 week, and the Aug 24–26 Exceptional block landing $700–1,000 rather than the ~$1,800 the curve expects. **What would kill it:** a second leg down — ice into the teens — or any Exceptional day clearing $1,500, which would mean weather still moves the number and the last fortnight was something else.

**Why it matters:** if it's a plateau, the shoulder-season revenue base is predictable and can be planned against. If it's a slide, every forward projection including the $70k-to-target figure is too optimistic.

---

### 2026-08-20 — Inside the late-August plateau, SNP 500 has no predictive power on in-store revenue
**Confidence: medium-high** — five consecutive days spanning 55 score points with zero rank correlation, plus a clean falsification test.

Aug 16–20: scores 415/410/425/420/465 → revenue $788/$789/$573/$871/$757. The highest-scoring day of the five produced the second-lowest revenue. Aug 20 (465, Exceptional) also came in below Aug 13 (420) and Aug 19 (420), and at 46% of expected — the worst realised ratio recorded.

This was a real test rather than more of the same. The plateau claim logged Aug 19 predicted that an Exceptional day would land in the $700–1,000 band; Aug 20 was that day and landed at $757. A $1,500+ result would have killed the hypothesis and didn't.

Reading: once footfall drops to the shoulder level, the store is serving a residual base whose size is set by how many people are on the Cape, not by whether it's a nice day. The weather term matters when there's a large marginal population deciding whether to go to the beach; it stops mattering when that population has gone home.

**What would confirm:** Aug 24–28 carries five Great/Exceptional days (425–475). If they land $700–1,000, this holds and the expectation curve needs a season-position multiplier applied from mid-August. **What would kill it:** any of them clearing $1,500.

**Consequence if true:** stop weather-adjusting daily in-store comparisons after ~Aug 15 and compare against the band instead; and treat every "the week ahead should comfortably beat target" verdict from the forecast tool as wrong by roughly a factor of two until the curve is fixed.

---

### 2026-08-21 — The SNP 500 under-weights precipitation and can rate a rainy, sunless day as "Great"
**Confidence: high on the fact, medium on the scope.**

Aug 21: 0.13 in of rain, 0.0 hours of sun, 69.3°F, 18.7 mph wind — scored **400 / Great**, expected revenue $1,636. The listed positives were `day_extension` and `access`; the only limiting factor flagged was `wind`. Precipitation and sun hours appear either absent from the model or heavily outweighed by the sunset/bonfire and access terms.

Actual was $359.31, 22% of expected — the worst ratio in the record, and almost certainly an artefact of the score rather than a store failure. Judged against BJ's own rainy-day anchor (~$500) the day is merely soft.

**Why it matters beyond one day:** I am accumulating an expected-vs-actual record intended to eventually replace the gut curve with a fitted one. Mis-scored days injected into that record will bias the fit toward "the store always underperforms." Aug 21 should be tagged as excluded.

**What would confirm:** any future day with measurable precip and <2 sun hours scoring above ~350. **What would kill it:** the scorer turning out to have a precip term that simply didn't trigger at 0.13 in, in which case the fix is a threshold change rather than a missing feature.

**Action:** check `agent/` for the precip and sun-hours inputs to the SNP scorer; cap any day with measurable precip and near-zero sun below the Great band regardless of tide, access or sunset factors.

---

### 2026-08-22 — Rain cuts footfall but raises basket; wet days are apparel-and-hard-goods days
**Confidence: medium** — two consecutive rain days plus a consistent mechanism, but weekend/weekday is confounded with the outcome.

Aug 21 (Fri, 0.13 in rain, 0.0 sun): $359.31 / 14 orders / AOV $25.67.
Aug 22 (Sat, 0.185 in rain, 0.0 sun): $1,642.29 / 30 orders / AOV $50.44 — against a dry trailing AOV of ~$35 and a dry Saturday (Aug 15) at $36.16.

The wet Saturday's basket was ~40% above the dry-Saturday basket despite far fewer tickets. The 7-day board that day contained zero consumables — a bodyboard, two ponchos, three hat lines, propane, burnout sweats. CONTEXT already says "rain → apparel and gifts hold up better than beach consumables"; the new part is that the *basket goes up*, not merely holds, because ice (~$6) drops out of the mix and durable goods replace it.

Reading: rain removes the beach-trip population (ice, low ticket, high frequency) and leaves a smaller browsing population that buys higher-ticket keepables. Revenue per visitor rises; visitor count falls further.

**What would confirm:** any further rain day with measurable precip showing AOV above the dry trailing average and a consumables-free top-sellers board. **What would kill it:** a rain day with AOV at or below dry baseline, which would mean Aug 22 was just one hard-goods sale flattering a 30-order day.

**Action if it holds:** on a forecast wet weekend day, front apparel, ponchos, hats, bodyboards and chairs rather than the beach consumables display. This is a lever the business can actually pull, unlike the weather itself.

### 2026-08-22 — The SNP precipitation blind spot is systematic, not a one-off
**Confidence: high.** Second consecutive occurrence.

Aug 21: 0.13 in rain, 0.0 sun → 400 / Great, only `wind` flagged as limiting.
Aug 22: 0.185 in rain, 0.0 sun → 445 / Great, **no limiting factors at all**, positives `tide`, `day_extension`, `wind`.

Precipitation and sun hours are either absent from the model or swamped by the tide / sunset-window terms. Both days must be excluded from the expected-vs-actual record or the eventual fitted curve will be biased toward "the store always underperforms" — Aug 22 in particular would enter the record as a 39% miss when it was one of the better weather-adjusted days of the month.

**Fix:** cap any day with measurable precipitation and <2 sun hours below the Great band regardless of tide, access or sunset factors. Confirmed as a pattern; no longer needs more evidence, needs a code change.

---

### 2026-08-23 — The SNP blind spot is sky-condition generally, not precipitation specifically
**Confidence: high** — third occurrence in four days, and this one had zero precipitation.

Aug 21 (0.13 in rain, 0.0 sun) → 400/Great. Aug 22 (0.185 in rain, 0.0 sun) → 445/Great, no limiting factors. Aug 23 (**0.0 in precip**, fog, **1.8 hrs sun**) → 465/Exceptional, no limiting factors, positives tide/wind/day_extension.

Aug 23 kills the narrower "precip isn't weighted" reading: there was no precipitation. The model is scoring the *geometry* of the day — tide stage, wind, sunset window, day length — and barely scoring whether the sun was visible at all. Fog is the clean case, because every geometric input was genuinely favourable and the day still wasn't a beach day.

**Fix:** the gate should be sun hours, not precipitation. Cap any day with <2 hrs sun below the Great band regardless of tide, wind, access or day-extension terms. Precip becomes a secondary penalty on top.

**What would confirm:** a day with good sun hours and poor tide/wind scoring low — i.e. the model behaving correctly when sun is present. **What would kill it:** finding sun hours already in the scorer with a sensible weight, which would make this a data-feed problem instead.

Consequence for the record: Aug 21, 22 and 23 must all be excluded from expected-vs-actual history, or the fitted curve inherits a bias toward "the store always underperforms."

---

### 2026-08-24 — In the shoulder, weather stops predicting in-store revenue; visitor population takes over
**Confidence: medium-high** — one clean natural experiment, strong mechanism, needs a second instance.

Aug 24 scored 495 (top of the season) on genuinely clean inputs: 12.5 hrs sun, 0.0 precip, 83.4°F, ideal afternoon low tide, no limiting factors. It produced **$720.92 / 22 orders**. Mon Aug 17 scored 410 on a dry overcast day and produced **$789.30 / 22 orders**. Same weekday, same order count, 85 SNP points apart, and the *worse* day earned more.

Every other high-score miss this month (Aug 21, 22, 23) was contaminated by the sun-hours blind spot in the scorer. Aug 24 has no such excuse — the score is right and the revenue still didn't follow. That makes this the first clean evidence that the weather→revenue link has broken rather than the model being wrong.

Mechanism is obvious and that's a point in its favour: perfect beach weather only converts if there are people on the Cape to convert. Post-Aug-15 the visitor population is falling ~30% a week, and it has become the binding constraint. The sky can no longer add customers who aren't here.

**Consequences:**
1. The expectation curve needs a **phase/population term**, not just weather and weekday. Without it, every remaining Exceptional day this season logs as a 35–50% miss and the fitted curve inherits a permanent "the store always underperforms" bias.
2. **Never pass the week-ahead tool's number through unadjusted in the shoulder.** It is forecasting $13.3k off seven Exceptional days; the realistic figure is $7–8k. The tool is scoring the sky in a period when the sky doesn't matter.
3. Judge shoulder days against the **same weekday, prior week** and the weekday band, not against SNP-derived expectation.

**What would confirm:** the rest of this week — six more Exceptional/Great days forecast. If they land in the $550–900 weekday band regardless of score spread (445 to 485), that's decisive. **What would kill it:** any of them clearing $1,500 on score alone, which would mean Aug 24 was just a bad Monday.
