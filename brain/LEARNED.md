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

Allie ran a pilates class in the sand area at 8am. Sandy's read: small direct sales, but it "set the
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
