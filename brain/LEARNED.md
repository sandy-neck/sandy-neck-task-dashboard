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

---

### 2026-08-25 — Confirmed: in the shoulder, SNP 500 no longer predicts in-store revenue; visitor population is the binding constraint
**Confidence: high on the fact, medium on the mechanism.** Upgraded from medium-high (2026-08-24) on a second clean instance.

Two consecutive days with sound scorer inputs — Mon Aug 24 (SNP 495, 12.5 hrs sun, 0.0 precip) and Tue Aug 25 (SNP 480, 11.3 hrs sun, 0.0 precip) — produced $721/22 and $410/17, the two **lowest** results in the season's entire 465–495 band:

| Day | SNP | Revenue | Orders |
|---|---:|---:|---:|
| Aug 11 | 465 | $1,273 | 38 |
| Aug 12 | 465 | $806 | 14 |
| Aug 20 | 465 | $757 | 25 |
| Aug 23 | 465 | $922 | 24 |
| Aug 24 | 495 | $721 | 22 |
| Aug 25 | 480 | $410 | 17 |

The two highest scores in the band are the two worst outcomes. Unlike Aug 21/22/23, neither day is contaminated by the sun-hours blind spot in the scorer — the scores are correct and revenue still didn't follow. Same-weekday comparison says the same thing: Tue Aug 18 (SNP 425) $573 → Tue Aug 25 (SNP 480) $410, −28% on a substantially better day, which is exactly the observed ~30% weekly decay arriving regardless of conditions.

**Mechanism (inferred, not measured):** perfect beach weather only converts if there are people on the Cape. Post-Aug-15 the visitor population is falling ~30%/week and has become the binding constraint. Caveat worth holding: I am explaining the revenue decay with a population decline that I only infer *from* the revenue decay. That's circular. It needs a non-revenue measure.

**Three consequences, all operational:**
1. The expectation curve needs a **phase/population term**. Weather + weekday is insufficient after mid-August. Aug 24/25 are valid data points for that fit; Aug 21/22/23 must be excluded (scorer bug).
2. **Never pass the week-ahead tool's number through unadjusted in the shoulder.** It forecast $12.2k for Aug 27–Sep 2 off six Great/Exceptional days. Realistic on decay: $5–6k. It is scoring the sky in a period when the sky doesn't matter.
3. Judge shoulder days against **same weekday, prior week** and the weekday band. Reporting SNP-vs-expected produces a meaningless string of 35–50% misses.

**What would confirm the mechanism:** Sandy Neck gatehouse permit counts or Barnstable occupancy data tracking the ~30%/week decline independently of sales. **What would kill the whole thing:** any remaining August day clearing ~$1,500 on score alone — which would mean Aug 24 and 25 were just two bad weekdays. Five more Great/Exceptional days forecast through Aug 31 will settle it.

---

### 2026-08-26 — In the shoulder, order count falls but average basket rises; the decay is footfall, not demand
**Confidence: low-medium** — one clean same-weekday instance, plausible mechanism, easily explained by a single large item.

Wed Aug 19: $871 / 23 orders / AOV $37.56. Wed Aug 26: $966 / 21 orders / AOV $45.60. Revenue **up 11%** on **two fewer orders** — the first same-weekday increase since the start of August, in a stretch where every other same-weekday comparison ran −17% to −28%.

The composition supports it: a $134.99 Anchor Works beach umbrella (new to the 7-day board) plus GCI Big Surf chairs at $98 each. Late-August buyers are fewer but are buying hard goods at full price, where peak-season days were high-count and consumable-heavy (ice, drinks).

If true, two things follow. (1) The pure "−30% a week" projection understates the shoulder floor, because basket growth partially offsets footfall loss — year-end may land above the $166k projection. (2) Discounting beach hardware to clear it before Labor Day would be leaving money on the table; it's still moving at full price.

**What would confirm it:** AOV continuing to rise against falling order counts through Aug 28–31, and hard goods staying on the 7-day board. **What would kill it:** AOV reverting to the ~$32–37 trailing band this weekend, which would mean Aug 26 was one umbrella and nothing more.

---

### 2026-08-27 — Shoulder-season day-to-day revenue swings are single-item lumpiness, not demand signal
**Confidence: medium-high** — four consecutive days with an identifiable big-ticket cause, and it cleanly kills the opposite hypothesis I logged yesterday.

Aug 24 AOV $32.17 · Aug 25 $24.14 · Aug 26 $45.60 · Aug 27 $23.50, on order counts of 22/17/21/18. Aug 26 contained the $134.99 Anchor Works umbrella plus GCI Big Surf chairs; Aug 27 contained no hard good at all. At ~20 orders a day, one $100–135 item is 15–20% of gross sales, which is larger than the entire weather effect appears to be at this point in the season (Aug 24 scored 495 and did $721; Aug 26 scored 480 and did $966).

This supersedes the 2026-08-26 entry ("order count falls but AOV rises; the decay is footfall not demand"). That entry named its own kill condition — AOV reverting to the $32–37 band — and Aug 27 went straight through it to $23.50. Basket is not trending up; it's oscillating with hard-goods incidence.

**What follows:** (1) before commenting on any AOV move in the shoulder, check the hard-goods lines first — this is the shoulder analogue of the peak-season ice-mix rule. (2) Don't build a year-end projection off basket growth. (3) Beach hardware is still clearing at full price, so the correct Labor Day play is placement, not discount.

**What would kill this:** a run of days where AOV moves substantially with no change in big-ticket composition — that would point back at genuine customer-mix change.

---

### 2026-08-28 — In the shoulder, the expectation curve fails on weekdays and roughly holds on weekends
**Confidence: medium** — clean separation across ten scored days, obvious mechanism, but only three weekend days in the sample.

Actual as % of expected, Aug 20–28, split by weekday:

| Mon–Thu | | Fri–Sat | |
|---|---:|---|---:|
| Aug 20 (465) | 41% | Aug 22 Sat (445) | ~93% |
| Aug 24 (495) | 48% | Aug 28 Fri (425) | **85%** |
| Aug 25 (480) | 37% | Aug 21 Fri (400, rain) | 22% |
| Aug 26 (480) | 65% | | |
| Aug 27 (445) | 29% | | |

Excluding the rained-out Aug 21, weekend days run 85–93% of expected while Mon–Thu run 29–65%. Aug 28 is the strongest case: a *lower* score (425) than four of the five weekday misses, and it nearly hit its number on 34 orders — the highest count since Aug 15.

This refines the Aug 25 note ("stop reporting SNP-vs-expected in the shoulder"). The ratio isn't uniformly dead — it's dead Mon–Thu and still informative Fri–Sat. Mechanism is the one from Aug 8: the curve's weekday factor was fitted on peak-season data, when midweek still had visitor volume. In the shoulder the weekday/weekend gap widens, so a factor calibrated in July under-corrects badly in late August.

**Practical consequence:** the operational number to track is the midweek mean vs the Fri/Sat pair, not the daily total. Aug 24–27 averaged $639; Aug 28 did $1,496. That ratio, not revenue level, is what tells BJ when to go weekends-only.

**What would confirm it:** Sat Aug 29 and Sun Aug 30 landing above ~75% of expected while Sep 1–3 stay under 50%. **What would kill it:** a weekend day coming in at 40% of expected on clean conditions, which would mean Aug 22 and Aug 28 were just two good days.

---

### 2026-08-29 — Cooling evenings open a firewood/bonfire category in the shoulder, and its complements are unstocked
**Confidence: medium** — one week of firewood data, but 9 separate orders and a clear mechanism.

Bundle of Firewood entered the 7-day board at $119 / 17 units / **9 orders** in the week ending Aug 29, alongside three cool-weather apparel lines (Coastal Varsity Crewneck, Sweatshirt Poncho, Jeep Duck Fuzzy Lounge Pants). Over the same stretch the SNP 500 headline cited the "sunset and bonfire window" as a positive on Aug 27, 28 and 29 as feels-like temperature fell from 88.8°F to 76.5°F.

The complements are all showing sold out: Jet-Puffed Marshmallows (6 sold), Honey Maid Grahams (5), Hershey's Milk Chocolate (19). Firewood sells at ~$7; a s'mores add-on is roughly the same again per basket at what should be ordinary grocery margin and near-zero lead time.

This is the shoulder-season analogue of the ice question from peak. Ice was the beach-trip proxy in July; **firewood may be the evening proxy in September–October**, and the same "what sits within arm's reach" question applies to the wood stack.

**What would confirm it:** firewood holding or growing on the board through Labor Day and into the late shoulder, with the three s'mores SKUs converting once restocked and placed adjacent. **What would kill it:** firewood proving to be an August-camping artifact that dies with the campground season, or the s'mores items sitting unsold beside the wood — which would mean firewood buyers are locals with their own supplies, not impulse baskets.

---

### 2026-08-30 — In the shoulder, daily revenue is driven by hard-goods incidence, not footfall
**Confidence: medium-high** — three clean instances now, clear arithmetic mechanism, but all within one 10-day window.

Aug 28–30 ran 34 → 46 → 26 orders against $1,496 → $1,685 → $576. Order count fell 43% on Sunday; revenue fell 66%. AOV went $40.28 → $34.84 → $22.17. Aug 28 and 29 both carried beach hardware (GCI Big Surf, Anchor Works umbrella, firewood volume); Aug 30 carried none of the big-ticket lines.

Same pattern earlier: Aug 26 $966 on 21 orders (umbrella + chairs) vs Aug 27 $458 on 18 orders (neither). Aug 30 vs Sun Aug 23: *more* orders (26 vs 24), 37% less revenue.

Mechanism is just arithmetic — at 18–26 orders a day, one $135 item is 15–20% of gross, and two or three are the difference between a $600 day and a $1,500 day. In July at 50+ orders/day this averaged out; it doesn't now.

**Practical consequence:** stop reading a soft revenue day as falling demand without checking the hard-goods lines first. And the reverse — placement of high-ticket items becomes a disproportionate revenue lever in the shoulder, because a single extra chair sale is worth ~10 consumable baskets.

**What would confirm it:** a day in September with below-band order count but two or more hard-goods sales landing above $1,000. **What would kill it:** a run of days where revenue tracks order count cleanly regardless of what's on the top-seller board.

---

### 2026-08-31 — Soft revenue days split into two mechanisms, distinguishable by order count vs AOV
**Confidence: medium** — four instances across one 10-day window, but the arithmetic is clean and the two cases are unambiguous.

Type A: order count holds or rises, AOV collapses → hard-goods incidence (Aug 27 $458/18/AOV $23.51; Aug 30 $576/26/AOV $22.17 with *more* orders than the comparable Sunday). Type B: order count collapses, AOV holds or rises → operational or weather event (Aug 31 $242/6/AOV $40.33, 4 POS transactions).

These have opposite implications. Type A is a merchandising/placement problem and demand is fine. Type B is not a demand signal at all until you know whether the doors were open. Reading Aug 31 as "demand fell off a cliff" would be wrong; reading Aug 30 as "nobody came in" would also be wrong.

**What would confirm it:** further shoulder days sorting cleanly into one bucket or the other, and Type B days correlating with either a logged closure/short day or a genuine washout. **What would kill it:** a day with both order count and AOV down together on normal hours and normal weather, which would mean actual demand decay and that the two-mechanism split is just noise on small numbers.

---

### 2026-09-01 — Website sessions are the tell for whether a zero-sales day is a closure or an outage
**Confidence: medium** — one clean instance, but the logic is sound and cheap to apply.

Sep 1 recorded $0 across POS, online store and TikTok. Web traffic that day was normal (49 sessions, baseline ~60) with 2 cart adds and 1 reaching checkout, so the storefront and analytics were both alive. That rules out a whole-platform failure and leaves closed doors (plus ordinary zero online conversion) or a POS-specific sync problem.

Corollary: the 7-day top-seller board was byte-identical to the previous day's read, which is what a genuine zero-sales day produces and is *not* what a broken sales query produces.

**What would confirm it:** BJ confirming a closure on a day that fits this signature, or a future outage where sessions also flatline and the product board shifts inconsistently. **What would kill it:** a case where sessions look normal, the board is static, and sales data later backfills — meaning the sync lag is invisible to both checks.

---

### 2026-09-02 — The weekends-only shoulder transition mimics a data outage, and the expectation curve must be gated on trading days
**Confidence: medium-high** — four consecutive days of the signature, clean mechanism, but still unconfirmed by BJ.

Aug 31 → Sep 3 ran 6 · 0 · 5 · 4 orders immediately after a 34/46 Fri/Sat, in conditions scoring 395–410 with no precipitation. Weather cannot produce that shape. CONTEXT already predicts it: Early shoulder "drops toward weekends only." The transition appears to have landed around Aug 31.

Why it matters: a conditions-only expectation curve prices a closed Wednesday at $1,255 and reports 10% of expected. Three of those in a row reads as business collapse when it's a scheduling decision. The same error inflates the week-ahead total — $12,500 expected next week assumes seven trading days when perhaps four are open, which makes the "week should comfortably beat target" verdict meaningless.

**The rule to carry:** once order count sits at or below ~6 for two consecutive non-weekend days in Great conditions, assume reduced hours, suppress expected-vs-actual on those weekdays, and recompute `required` against open days only.

**What would confirm it:** BJ confirming the schedule, or Fri–Sun Sep 4–6 returning to 25–45 orders while Mon–Thu stay under 6. **What would kill it:** a weekday in the next fortnight returning 20+ orders unprompted, which would mean the doors were open all along and demand genuinely fell off a cliff.

---

### 2026-09-03 — Zero POS rows alongside live online orders is the definitive closed-store signature
**Confidence: high** — clean instance, unambiguous mechanism, and it upgrades the weaker Sep 1 sessions-only test.

Sep 3 returned no Point of Sale row at all while TikTok took 3 orders and the web store took 1 (with a completed checkout). Sales infrastructure was demonstrably alive on the same date, so a reporting or sync failure would have had to be POS-specific *and* silent — far less likely than the store simply being shut. The Sep 1 test (normal web sessions + zero sales everywhere) could only rule out a total platform failure; this one rules out a sales-pipeline failure too, because orders on other channels flowed through the same reporting path on the same day.

**The rule:** POS absent + any other channel transacting → treat as closed, suppress expected-vs-actual entirely, and do not report the ratio.

**What would confirm it:** BJ confirming the schedule, or Fri–Sun Sep 4–7 returning 25–45 orders with POS present while Mon–Thu keep showing POS-absent days. **What would kill it:** a later backfill putting POS orders onto Sep 3, which would mean POS-specific sync lag is real and invisible to both checks.

---

### 2026-09-04 — Order count down with AOV up is a footfall/hours signal, not a demand-quality one
**Confidence: medium** — one clean like-for-like pair, but the mechanism is well separated from the two other soft-day signatures already logged.

Fri Sep 4 (SNP 425, overcast, feels 80.6°F) did $1,233 on 26 orders / AOV $45.65. Fri Aug 28 (SNP 425, overcast, feels 88.8°F) did $1,496 on 34 orders / AOV $40.28. Same score, same weekday, same sky band — 24% fewer orders but a 13% larger basket. If demand quality had softened, basket would fall with count; it rose instead. So the customers who came bought normally and there were simply fewer of them, or the doors were open fewer hours.

This completes a three-signature set for reading soft days: count near zero + normal AOV = closed; count normal + AOV collapse = product-mix/ice incidence; count down + AOV up = footfall or reduced hours.

**What would confirm it:** hourly order distribution showing Sep 4's orders compressed into a shorter window (hours) or spread normally but thinner (footfall). **What would kill it:** finding a large-ticket outlier inflating Sep 4's AOV, which would make the basket rise an artifact of one sale rather than a real shift.

### 2026-09-04 — A holiday weekend does not reliably backfill shoulder-season footfall
**Confidence: low** — single observation, and hours are an unexcluded confound.

The Friday of Labor Day weekend came in below the ordinary Friday a week earlier in identical scored conditions. The prior assumption was that a holiday weekend carries a premium over an adjacent normal weekend. On the Cape the holiday may mark the *end* of the visitor population rather than a peak of it — people leave for the school year rather than arrive for the long weekend.

**What would confirm it:** Sep 5–7 also landing at or below Aug 28–30 despite better scores (Sep 7 forecasts 455 against Aug 30's 405). **What would kill it:** a strong Sep 5/6/7, which would make Sep 4 a one-day anomaly or purely an hours artifact.

---

### 2026-09-05 — Cool, windy shoulder days shift the mix from beach consumables into apparel
**Confidence: medium** — one day, but with unusual breadth (8 separate orders on one SKU) and a clear mechanism.

Sep 5: 69.8°F, 17.2 mph wind, overcast, SNP 400 — the mildest scored day in the recent band. The SNP Coastal Varsity Crewneck went $368 / 8 units / **8 distinct orders**, straight to the top of the board from nowhere, and day AOV hit $56.39 (previous month high $45.65). Beach consumables didn't lead. CONTEXT already notes rain favours apparel over consumables; this extends it to *cold-but-dry*, which the SNP 500 still scores as a "Great" beach day.

If true, the expectation curve is mis-specified for autumn: a mild, windy, dry day scores well on beach criteria but drives a *different basket* — fewer, larger, apparel-weighted tickets — which can beat expectation rather than miss it.

**What would confirm it:** the next cool (<72°F) dry Saturday also topping the board with sweatshirts/hoodies and AOV above $50. **What would kill it:** the crewneck being a one-off (new product launch, a display change, or a group purchase), or warm shoulder days selling the same volume of apparel.

### 2026-09-05 — Retract: holiday weekends DO backfill shoulder footfall
**Confidence: high on the retraction** — the 2026-09-04 claim was built on a single Friday and is contradicted directly.

Sep 4 (Fri, SNP 425) did $1,233 / 26 orders and I hypothesised the Labor Day weekend was marking the end of the visitor population rather than a peak. Sep 5 (Sat, SNP 400 — a *worse* day) did $4,593 / 79 orders, the largest single day of the season and ~50% above peak-summer Saturdays. The holiday weekend delivered emphatically.

Sep 4 is best explained as reduced hours or a one-day dip. **Lesson to carry: do not promote a directional claim about season shape off one day, especially when hours are an unexcluded confound.**

---

### 2026-09-06 — Shoulder-season Sundays cap out around $500–$600 regardless of a good SNP score
**Confidence: medium-high** — two clean like-for-like Sundays in near-identical conditions, obvious mechanism.

Sun Aug 30 (SNP 405, overcast) $576.33 / 26 orders / AOV $22.17. Sun Sep 06 (SNP 400, overcast) $468.52 / 23 orders / AOV $19.93. Both scored "Great," both landed at ~20–25% of a Sunday-adjusted expectation north of $2,200. Sep 6 was the Sunday of Labor Day weekend and still didn't move — the day after the season's largest single day ($4,593).

Mechanism: Cape day-trippers and weekenders travel home Sunday. Saturday is the visitor-volume peak; Sunday is a departure day, so it behaves like a weekday on footfall and like a weekday-plus on small tickets.

Implication: the expectation curve's Sunday day-of-week factor is materially too high for the shoulder, and scoring shoulder Sundays against it will keep manufacturing false misses of $1,500+.

**What would confirm it:** Sun Sep 13 (forecast SNP 455) landing $500–$800 against an expected above $2,500. **What would kill it:** Sep 13 clearing $1,500, which would make Aug 30/Sep 6 a weather-mildness artifact (both were cool, 67–81°F, 17mph) rather than a day-of-week effect.

---

### 2026-09-07 — On holiday weekends the soft day is Sunday and the Monday holds; on ordinary weekends Sunday is the soft day and Monday is dead
**Confidence: medium-high** — one clean holiday instance, but the contrast is large in both directions and the mechanism is unambiguous.

Labor Day weekend: Fri $1,233/26 · Sat $4,593/79 · **Sun $469/23** · **Mon $950/33**. Sunday scored SNP 400, Monday 475, but the gap is far larger than the score difference warrants. Compare an ordinary shoulder Monday — Mon Aug 31, SNP 410, $242 on 6 orders. Labor Day Monday ran ~4x that on 5.5x the orders.

Mechanism: a Monday public holiday moves the drive-home from Sunday to Monday afternoon. Sunday becomes a stay-put day (low footfall, small tickets — AOV $19.93), Monday becomes a last-trip-before-leaving day (higher footfall, mid tickets — AOV $28.80).

**Why it matters:** Columbus Day, Monday Oct 12, closes the late shoulder. If this holds, the Monday is worth staffing and stocking properly and the Sunday is not — the opposite of the ordinary-weekend rule. Also means the expectation curve needs a holiday flag rather than just a day-of-week factor; without one it will hold a dead ordinary Monday and a live holiday Monday to the same number.

**What would confirm it:** Columbus Day Mon Oct 12 clearly out-earning Sun Oct 11 on both orders and revenue. **What would kill it:** Oct 12 collapsing to ordinary-Monday levels, which would make Sep 7 a Labor-Day-specific artifact (last day of summer, not a generic holiday effect) rather than a rule about Monday holidays.

---

### 2026-09-08 — Once the visitors leave, SNP score stops predicting revenue at all
**Confidence: medium** — three clean reads at the top of the score range, but confounded with the schedule change.

The three highest-scoring days of the shoulder produced: Aug 26 (SNP 480, Wed, open) $966 · Sep 7 (SNP 475, Mon, holiday, open) $950 · Sep 8 (SNP 495, Tue, closed) $6. Meanwhile Sep 5 scored the *lowest* of the recent band (400) and did $4,593 — the season's largest day.

The read: after Labor Day the binding constraint is how many people are on the Cape, not what the sky is doing. Weather quality reallocates *what* the remaining people buy (cool day → apparel, per Sep 5) but can't manufacture footfall that has physically driven home. The expectation curve is weather-in, revenue-out, so it will keep producing $1,700–$2,000 expecteds for the entire Exceptional run Sep 10–16 and keep manufacturing $1,200+ "misses."

**What would confirm it:** the Sep 11–15 run — five days scored 410–475 — landing in the $500–$1,500 band on open days rather than anywhere near the $1,700–$1,980 expecteds. **What would kill it:** Sat Sep 12 (465) clearing $3,000, which would mean weather does still convert on weekends and only midweek is footfall-bound.

**Implication if true:** the curve needs a season-phase multiplier, not just day-of-week and holiday flags. From Sep 16 the honest framing is to stop scoring store days against SNP-derived expectations entirely and judge them against the observed shoulder bands instead (weekday $120–$250, Fri $1,200–$1,500, Sat $1,700–$4,600, Sun $470–$580).

---

### 2026-09-09 — Weekly session totals are distorted by single in-store spike days; quote the median, not the % change
**Confidence: medium** — one clean case, but the mechanism is obvious and the failure mode is severe.

Sessions ran 459 last 7 days vs 385 prior, which reads as +19.2%. The daily series is [54,65,104,69,64,51,52]. The 104 is Sep 5 — the $4,593 in-store Saturday, the season's largest day. Every other day in both weeks sits in the 42–69 band. Median daily is ~60 both weeks. The "growth" is one spike.

This matters because it compounds an earlier finding: session spikes track in-store spikes, which suggests sessions partly measure intent-to-visit rather than e-commerce demand. So a big retail day mechanically inflates the weekly session count, and reporting the week-over-week percentage would credit online growth for what is actually a foot-traffic event.

**Rule:** for a traffic base this small, report the median daily session count and only call a change real when the whole band shifts, not when one day carries it. **What would kill it:** several weeks where the % change and the median move together, meaning the spikes are incidental rather than structural.

---

### 2026-09-10 — Session spikes do NOT reliably track in-store spikes; the coupling has broken
**Confidence: low** — one contradicting case against one supporting case.

On 2026-09-09 I recorded that weekly session totals get inflated by single in-store spike days (Sep 5: 104 sessions alongside the $4,593 Saturday), and inferred sessions partly measure intent-to-visit. Sep 10 produced **92 sessions with the store closed and zero POS activity** — the second-highest day in the 15-day series, with no footfall event attached.

So either (a) the Sep 5 correlation was coincidence, (b) there are two distinct spike mechanisms and only one is footfall-linked, or (c) some portion of these sessions is non-human and I have no bot filtering to check.

**What would confirm a source shift:** Sep 11–13 sessions staying in the 80–100 band regardless of whether the store trades. **What would kill it:** Sep 11 reverting to ~60 and the next spike landing on a big Saturday again.

**Practical rule until resolved:** do not attribute a session spike to anything without a named cause. Ask BJ/Meghan what was posted before inferring a mechanism — a single floor answer settles this faster than weeks of session data.

---

### 2026-09-11 — Check gross vs net every day; a single reversal can inflate the headline several-fold
**Confidence: high** — arithmetic, not inference.

Sep 11 reported gross $565.46 across 4 orders. Net sales were $81.98. The difference is exactly $483.48, the value of a single Shopify-Mobile order that was reversed. Reported on gross, the day looks like a thin-but-real Friday at 32% of expectation. On net it is $82 — indistinguishable from a closed day, and the POS count (1) confirms closed.

I have been reading `gross_sales` from the daily totals without checking `net_sales` alongside it. At shoulder-season volumes one refunded ticket can be most of the day.

**Rule:** compare gross to net on every daily read. Where they diverge by more than a few percent, lead with net and name the reversal. **What would kill it:** nothing — this is definitional. What's worth watching is how often it happens; if reversals are frequent, that's its own operational question.

### 2026-09-11 — The session/footfall coupling is dead; two consecutive spikes landed on closed days
**Confidence: medium** — two clean contradicting cases now, against one supporting case.

Sep 9 I hypothesised sessions partly measure intent-to-visit, because Sep 5's 104-session spike sat on the $4,593 Saturday. Sep 10 produced 92 sessions with the store closed. Sep 11 produced **123 sessions** — the highest in the series — also with the store closed and one POS order. Baseline is ~60/day.

Two consecutive decoupled spikes is no longer explicable as coincidence. Something else is driving traffic. The 2 completed checkouts on Sep 11 (frozen bait, ice — the first multi-order online day recorded) argue that at least part of it is human, since bots don't convert.

**Candidate causes, unranked:** a social post, an SEO/AI-legibility Routine edit landing, or unfiltered bot traffic. I cannot distinguish these with the connectors available.

**What would confirm a genuine source shift:** the 80–125 band holding through Sep 12–15 regardless of trading, plus continued cart adds. **What would kill it:** reversion to ~60 within two days, marking this as a two-day anomaly. **Fastest resolution:** ask the floor what was posted — one answer beats weeks of session data.

---

### 2026-09-12 — The shoulder-season decline hits basket size as hard as it hits footfall
**Confidence: medium** — one clean Saturday-to-Saturday comparison plus one corroborating Sunday, with the product mix supporting the mechanism.

Sat Sep 5 (SNP 400): 79 orders, AOV $56.39. Sat Sep 12 (SNP 430, slightly better day): 24 orders, AOV $17.35. Orders fell 70% and basket fell 69% — roughly equally. Sun Sep 6 showed the same shape (23 orders, AOV $19.94) and I misread it at the time as simply a quiet day.

The mechanism is visible in the product board: beach hardware is exiting (GCI Big Surf $294/3u → $196/2u → $98/1u across three reads; Fluzzle Tube and Wave Zone gone entirely) while the only line with meaningful order count is Coffee On Tap at $66.50 across 9 orders. Post-season visitors are buying consumables and the occasional small giftable, not equipment. Equipment is a "we're here for the summer" purchase and that population has left.

**Why it matters:** every `required` dollar figure for the rest of the season has to be read as a ticket count. Sat Sep 19 requires ~$920, which at a $17 basket is ~50 transactions — far above anything the shoulder has produced. It reframes the lever from "get more people in" to "get anything above $20 into the basket," which is a merchandising question, not a traffic question.

**What would confirm:** Sat Sep 19 (SNP 445 forecast) coming in with AOV in the $15–25 band. **What would kill it:** Sep 19 AOV back above $35, which would mark Sep 12 as an anomalous day rather than the new shape.

---

### 2026-09-13 — The elevated web-session band is a real source shift, not a footfall echo
**Confidence: medium-high on the fact, zero on the cause.**

Four consecutive days in the 80–125 range (92, 123, 82, 79) against a ~60/day baseline that held all month. Those four days span a closed Friday, an open Saturday, and a closed rain-washout Sunday — so the band survives complete variation in whether the store traded. This kills the Sep 9 "sessions partly measure intent-to-visit" hypothesis outright, and it's now too long to be a two-day anomaly.

The online orders in the window — frozen bait (2 orders, 4 units) and a 5lb bag of ice — argue at least part of it is human, and human in a specifically *local* way. Nobody ships frozen bait.

**What would confirm a named source:** BJ or Meghan identifying a post or listing change in the Sep 10–11 window. **What would kill the "real" reading:** reversion to ~60 by Sep 16–17 with no further cart adds. **Fastest resolution remains asking the floor** — I have now spent four days of session data on a question one sentence would answer, which is itself a lesson: escalate unresolved attribution questions to the humans early rather than accumulating evidence.

### 2026-09-13 — The expectation curve overprices heavy-rain days at shoulder volumes
**Confidence: medium** — two heavy-rain days now, both SNP 275, both at 3–8% of expected.

Sep 3 (275, heavy rain, open) → $115.95 against ~$1,400 expected. Sep 13 (275, 1.2" rain, zero sun, closed) → $50.97 against $1,468. BJ's anchor is $500 for a rainy day at SNP 150, and the curve interpolates 275 up to ~$1,468 — but a genuine Cape washout in September has produced roughly $120 at best, not $1,400.

The likely error is that 275 is scoring "marginal *beach* day" while the revenue reality is "nobody leaves the house." Rain looks like a step function, not a linear input: once precipitation clears some threshold (~0.5"?) the day collapses to a floor regardless of score.

**What would confirm:** a third heavy-rain day, open for trading, landing under $200 against a four-figure expectation. **What this implies if true:** precipitation should cap expected revenue directly rather than feed the composite score. Worth raising when the curve is next touched — logging here rather than emailing, since BJ knows a rainy day is bad and doesn't need telling.

---

### 2026-09-14 — The Sep 10–13 session band was a discrete event, not a level shift
**Confidence: medium-high** — the decay is now unambiguous.

Series: 92, 123, 82, 79, 42. Four elevated days then a clean return to the ~50–65 baseline that held all month. It survived a closed Friday, an open Saturday and a rained-out Sunday, so it was never a footfall echo — but it also did not persist, so it was not a new acquisition level either. Cause was never identified and almost certainly never will be now.

**The generalisable lesson is process, not traffic:** I spent five consecutive daily runs accumulating evidence on an attribution question that one message to BJ or Meghan would have answered while the event was live. Unresolved attribution questions should be escalated to the humans on day two, not day five. By day five the answer has no operational value.

**What would revise this:** a second unexplained multi-day band appearing without a named cause, which would suggest a recurring mechanism (a platform surface, a recurring post schedule) worth hunting properly rather than asking about.

---

### 2026-09-15 — The 7-day session comparison will invert next week as the Sep 10–13 band exits the window
**Confidence: high** — pure arithmetic, not a hypothesis.

Sessions read +14.9% (516 vs 449) today despite the last two days running 42 and 46, because the window still contains 92/123/82/79. Once those roll out (by ~Sep 20) the same stable ~50/day baseline will print as a double-digit *decline*.

**Why it matters:** the traffic line is mandatory every single day, so this artifact is guaranteed to surface. Report the median, name the window effect explicitly when it hits, and do not let it be read as an autumn collapse or as a verdict on the SEO work. The generalisable rule: at these volumes any 7-day-over-7-day percentage is dominated by whichever single spike day happens to sit inside the window — quote medians, treat spikes as discrete events, and pre-warn when a known spike is about to exit.

---

### 2026-09-16 — A session count 20x+ above baseline with zero cart activity is almost certainly non-human, and should be escalated same-day rather than analysed
**Confidence: low on the cause, high on the process** — one observation, cause unresolved at time of writing.

Sep 17 partial logged 1,173 sessions against a ~50/day baseline that had held for the whole month, with no orders and no cart adds attached. The Sep 10–13 band (92/123/82/79) was a 2x move and took five runs to (not) explain; this is 23x. Magnitude alone shifts the prior heavily toward something mechanical — a crawler wave, a scraper, or a bot net — because real human interest at that multiple would normally drag *some* cart activity with it, even at this site's poor conversion.

The process rule is the part worth keeping regardless of how this resolves: ask BJ or Meghan on day one, while the event is live and they might still know what caused it. An attribution answer arriving on day five has no operational value.

**What would confirm non-human:** sessions stay enormous while cart adds stay at zero, and the spike collapses within 1–2 days. **What would kill it:** cart adds or orders rise proportionally, or BJ names a post/mention.

**Why it matters:** these spikes will recur, the daily traffic line is mandatory, and a bot wave inside a 7-day window will wreck every session comparison for a week. Tag the cause early or the trend line becomes unreadable.

---

### 2026-09-17 — The Sep 17 session spike was non-human: 24x traffic, falling cart adds, full collapse within one day
**Confidence: high on non-human, medium on the specific cause** — the signature is about as clean as this data can produce.

Sessions went 49 → 1,191 → 15 across three days against a ~50/day baseline that had held all month. Over the same window 7-day cart adds *fell* from 4 to 2. Human interest at 24x volume drags some cart activity with it even at this site's near-zero conversion rate; this dragged negative. Collapse inside a single day rules out anything sustained like press or a viral post.

Likely trigger: the SEO Routine edits the catalogue every 3 days, and a large re-crawl of ~993 products would produce exactly this shape. Unproven — Search Console isn't connected, which is the thing that would settle it.

**The generalisable rules:**
1. **Signature for a bot wave:** sessions up >10x, cart adds flat or down, duration 1–2 days. When all three hold, call it mechanical and move on — do not spend runs hunting a marketing cause.
2. **A spike this size wrecks the 7-day session comparison for exactly 7 days.** Pre-warn on day one, quote the median throughout, and name the window contents whenever a percentage is unavoidable. Three different comparisons in ten days printed +11.8%, +14.9% and +224.3% off an essentially flat ~50/day baseline.
3. **Escalate on day one anyway, but don't repeat the ask.** Escalating was right; the data happened to answer before BJ did. Two runs to resolution versus five for the Sep 10–13 band.

**What would revise this:** a recurring 3-day-cadence spike pattern matching the Routine schedule would upgrade the cause from medium to high, and would mean these are now a permanent feature of the traffic series that needs filtering at source rather than narrating monthly.

---

### 2026-09-18 — When there is no revenue to analyse, the forecast window is the story
**Confidence: medium** — reasoned from structure and one applied instance, not yet validated against outcomes.

Three consecutive zero days produced an email with a genuine, actionable point: today (Sat Sep 19, SNP 400/Great) is the last Great-rated day in a seven-day forecast that then runs 275 / 330 / 330 / 330 / 330 / 260 / **240 with rain on Saturday the 26th**. With only three or four trading weekends left before Columbus Day, one washout Saturday removes a meaningful fraction of the remaining season's revenue — so the good weekend immediately before it is worth pushing.

The generalisable rule: **in late shoulder and off-season, the SNP 500 forecast is more informative than the sales data**, because the sales data is mostly zeros and the forecast tells you which of the few remaining open days actually carries weight. Flip the email from backward-looking (what the day did vs. expected) to forward-looking (which upcoming day is scarce) once the store goes below ~3 trading days a week.

**What would confirm:** Sep 26 comes in materially below Sep 19 despite both being Saturdays, and the gap tracks the score gap (400 vs 240) rather than the calendar. **What would kill it:** weekend revenue in late shoulder turns out to be weather-insensitive — driven by a fixed base of locals and last-of-season visitors who come regardless — in which case the forecast has no predictive value here and the lever doesn't exist.

**Corollary on scarcity:** the value of a single good day rises as the number of remaining trading days falls. A 400-score Saturday in July is one of ten; in late September it may be one of three. The expectation curve does not capture this, and a promo or push is worth more on the scarce day than the identical day in peak.

---

### 2026-09-19 — Cold days shift in-store mix from consumables to apparel and raise the basket
**Confidence: medium** — one clean weekday-matched pair with a large effect and an obvious mechanism, but n=1.

Sat Sep 12 (SNP 430, warmer): 24 orders / $449 / AOV $17.35. Sat Sep 19 (SNP 330, 63.7°F, feels 59.2°F, 19mph wind): 17 orders / $545 / **AOV $32.06**. Fewer orders, 85% higher basket, 21% more revenue.

The mix is the evidence, not just the average. Five of the eight top in-store lines on Sep 19 were warm apparel (hoodie $58, sweatshirt $50, sweatpants $49, rope hat $44, kids fleece $35). Ice and drinks — the highest-order-count items all summer — were absent from the top eight entirely.

Mechanism: cold thins the door but converts whoever comes into apparel buyers, and an apparel ticket is 5–8x an ice ticket. The two effects partly cancel, which is why a low SNP score can produce a *higher* revenue day than a higher-scored one in shoulder season.

**Why it matters:** the SNP 500 curve treats cool weather purely as a negative. In late shoulder that may be wrong in direction, not just magnitude — and it implies a cheap merchandising lever (front the fleece when the forecast turns cold) that costs nothing to pull.

**What would confirm:** Sat Sep 26 (275/Marginal, rain) comes in with a basket at or above $32 on low order count. **What would kill it:** Sep 26 collapses on both basket and total, meaning rain and cold behave differently and Sep 19 was just a good apparel day. Also killed if the next warm open day posts an equally high basket — that would make Sep 12's $17 AOV the anomaly rather than the baseline.
