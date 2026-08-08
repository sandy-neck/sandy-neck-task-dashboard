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
