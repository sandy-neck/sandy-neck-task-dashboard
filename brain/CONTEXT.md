# Sandy Neck Provisions — Business Context

This is the master context file. The daily analytics agent reads it before writing anything,
so it stops re-deriving things you already know and starts reasoning from where you actually are.

**Edit this file freely.** It is meant to be argued with. When the agent gets something wrong or
states the obvious, correct it here (or drop a note in `INBOX.md`) and the correction sticks.

Last substantive update: 2026-08-08

---

## The business

Coastal provisions shop in East Sandwich / Sandy Neck, Barnstable County, Cape Cod, MA.
Gear, food, apparel, and gifts — things people actually use, with a connection to the water.

- Owners: Sandy and BJ. Meghan works the floor and talks to customers.
- ~993 products in Shopify. Shopify Basic plan.
- Seasonal business. Peak is Memorial Day → Labor Day.
- Store contact: goodvibes@sandyneckprovisions.com

---

## Channels — and how to think about each

The single most important framing: **this is a physical retail business with an online presence,
not an e-commerce business with a storefront.** Analysis that treats them as one number is useless.

Measured over the 7 days ending 2026-08-07:

| Channel | Orders | Revenue | Share of revenue |
|---|---:|---:|---:|
| Point of Sale (in-store) | 217 | $7,719.99 | ~94% |
| Online Store | 4 | $325.40 | ~4% |
| TikTok | 26 | $179.71 | ~2% |
| Shop / Draft Orders | 2 | $25.00 | <1% |

### In-store

In-store outpacing online is **fully expected**, especially at summer peak. This is not a finding
and should never be reported as one. The interesting questions here are retail questions: what
moved, what's running out, what the weather was doing, what people came in for.

### Online store

Small — and that's a **problem we want to solve**, not a fact to accept. Two goals, not one:
1. More online traffic and orders in their own right.
2. Online as a funnel into the physical store. Someone who finds us online and drives over is a win
   the e-commerce numbers will never show.

Conversion-funnel metrics (cart abandonment, checkout completion) describe ~4% of the business.
Report them, but never let them lead.

### TikTok

Outperforms the web store on order count and it is **mostly one weird phenomenon: Sun Bum air
fresheners.** The algorithm pushes them relentlessly and we don't know why. The per-order return is
so small it's arguably not worth the effort — we keep it going for the visibility.

Other products that have had genuine spurts:
- Waboba catch toys
- Salty gem rings

**Do not report "TikTok is growing" as an insight without checking what's actually selling.**
If it's air fresheners again, that's the baseline, not news. A spurt in something *else* is news.

### Instagram

Active. Underused relative to intent.

### Offseason plan

As summer winds down, the intent is to **lean heavily into TikTok, the online store, and Instagram.**
Post-Labor Day analysis should shift weight accordingly — in-store will fall off naturally and that
is expected, not alarming.

---

## Annual target and season calendar

**Annual sales target: $190,000 for the year.** Sandy wants to stay abreast of how the business is
trending toward that number — not at year-end, but continuously.

**Pacing is not a straight line through the calendar.** This is a seasonal business; a fixed
percentage of the year elapsed says nothing about how much revenue should have landed. August alone
carries a large share of the year. The right question is always "how much of the year's revenue has
normally landed by this date, and are we ahead of or behind that" — never "we're 60% through the
year so we should be at 60% of target."

**Prior year sales are the reference guide for seasonality shape.** The pacing logic lives in
`agent/targets.py` — the target constant, the season phase calendar, and the curve logic are all
there and can be edited. The prior-year curve, once computed from real Shopify history, is cached at
`brain/reference/prior-year-seasonality.json` so it doesn't need to be re-derived from a full year of
orders on every run. **Until that cache exists, a documented estimated monthly curve is used instead**
(also in `agent/targets.py`), and the agent must say plainly when it is pacing against the estimate
rather than measured prior-year history.

### Season phases (as of 2026-08-08)

In Sandy's words: roughly two more weeks of peak, then early shoulder through mid-September (store
starts going down to weekends only), then late shoulder through Columbus Day weekend, then
"hopefully online/social sales to finish the year and an area for growth opportunity for sure."
Columbus Day 2026 is Monday October 12, which is why late shoulder runs through roughly that date.

| Phase | Dates | What it means |
|---|---|---|
| Deep off-season | Jan 1 – Apr 30 | Online and social only. Store effectively closed. |
| Spring ramp | May 1 – May 24 | Getting ready. Weekend traffic begins. |
| Peak | May 25 – Aug 22 | Memorial Day to late August. The year is won or lost here. |
| Early shoulder | Aug 23 – Sep 15 | Drops toward weekends only. Volume falls fast. |
| Late shoulder | Sep 16 – Oct 12 | Weekends through Columbus Day. Last of the foot traffic. |
| Off-season | Oct 13 – Dec 31 | Online, social and TikTok. The growth opportunity. |

### How to talk about pacing

Report where the year stands against the $190k target **adjusted for season position** — expected
revenue by this date, actual vs. that, projected year-end at the current pace. Never report pacing
as a naive percentage of the calendar year elapsed. And always flag clearly when the pacing is
running off the estimated fallback curve rather than real prior-year data, since the estimate is a
documented guess, not measured history.

---

## Product intelligence

Things that are true about specific products and would otherwise take months to re-learn.

### Ice
Near-perfect **beach-trip proxy.** People buying ice are almost always headed out. High frequency,
tiny ticket (~$6). 33 orders / $210 in the week ending 2026-08-07 — highest order count of anything.

Because it's high-count and low-dollar, a day heavy on ice **drags average basket down** without
anything being wrong. Always check ice mix before concluding baskets shrank.

Open question worth testing: what sits within arm's reach of the ice chest?

### Sun Bum air fresheners
See TikTok above. High volume, negligible margin contribution, kept for reach.

### Tire deflators (Auto Bots)
Sold to **oversand vehicle traffic** — Sandy Neck has an ORV beach, so demand tracks beach permits.
High dollar-per-transaction, low volume. $260 on 4 sales in the week ending 2026-08-07.

**Sourced from Alibaba (China). 30-day turnaround at best.** As of 2026-08-08 we should already have
reordered and did not — we are jammed up on these. This is the canonical example of why lead time
has to be part of the analysis, not an afterthought.

### Greenhead fly repellent (Green Head Guys)
Sharply seasonal. Greenhead fly season on the Cape runs roughly mid-July to early August, then
demand falls off a cliff. Top revenue item ($380 / 18 orders) in the week ending 2026-08-07.
Sell through the remaining window; do not reorder late in the season.

---

## Vendors and reorder logic

The point of tracking this: **knowing something sold well is useless if the reorder window already
closed.** A hot product with a 30-day lead time in mid-August is a different decision than the same
product in June.

| Vendor / source | Products | Lead time | Notes |
|---|---|---|---|
| Alibaba (China) | Auto Bots tire deflators | **30 days at best** | Currently behind on reorder |

<!-- Add vendors as they come up. Even a rough lead time is far better than none. -->

### The reorder question, framed properly

For any product running low, there are three distinct answers and the agent should say which one it
thinks applies:

1. **Reorder now** — sells year-round, or the season has enough runway left to clear the lead time.
2. **Let it sell out, restock next season** — seasonal item, lead time exceeds remaining season.
   Selling out is the *goal*, not a failure.
3. **Don't restock** — didn't earn its shelf space.

Calendar math matters: with Labor Day as the practical end of peak, a 30-day lead time ordered in
mid-August lands as the season ends. That's usually answer #2.

---

## Weather and tides

**This is not a nice-to-have. It is the main confounder in daily comparisons.**

A summer Friday is not a unit of measurement. A hot, muggy, get-me-to-the-beach Friday should
substantially outperform a cool or rainy one, and comparing them without that context produces
confidently wrong conclusions.

Worked example — **2026-08-07**: hot and muggy, a classic beach day. The store did $1,468.65, which
beat the recent daily average by ~25%. The agent called that a strong day. Sandy's read: given the
conditions it **slightly underperformed** what it should have done. Same number, opposite conclusion.
The weather is what makes the difference.

What to build intuition on over time:
- Beach-day weather (hot, sunny, low wind) → ice, drinks, beach gear, sunscreen, ORV traffic
- Rain → foot traffic collapses; apparel and gifts hold up better than beach consumables
- Tides — Sandy Neck's flats are dramatic. Low tide mid-day likely shifts beach behavior and
  therefore trip timing. **Unproven; worth watching before asserting.**

Rule: never call a day good or bad on revenue alone. Say what the weather was and judge against
comparable conditions.

### What a day should do — the expectation curve

Day quality feeds the analysis through the **SNP 500** (see `projects/snp-500.md`), a 1–500 score of
how good a Sandy Neck beach day it was. That score is turned into an expected in-store revenue, and
**the day gets judged on actual vs. expected, not on the raw number.**

Sandy's anchors, stated plainly:

> *"If it is a rainy Tuesday then I am happy to surpass 500, whereas a great beach Friday like
> yesterday I would hope to be at 2000."*

| SNP 500 | Kind of day | Expected in-store revenue |
|---:|---|---:|
| 150 | Rainy, poor beach weather | $500 |
| 480 | Near-perfect beach day | $2,000 |

Linear between, flat outside — there's a floor of people who come regardless of weather, and a
ceiling where the store hits its own capacity.

**This is a gut baseline, not a fitted model,** and the agent should talk about it that way: "well
short of what a day like that should do," never "12.4% below forecast." Every daily log records
expected vs. actual, so after a season there's real data to replace the guess. Anchors live in
`agent/expectations.py` and can be changed freely.

Worked example — **2026-08-07** scored **480** (near-perfect). Expected ≈ $2,000. Actual $1,468.65 —
**73%, a gap of −$531.** The original email called that day "strong, +25% vs average." It was a miss.
That inversion is the entire reason this section exists.

---

## How people find us

We know less here than we should, and the anecdotes suggest real opportunity.

**The "swim suits near me" story (week of 2026-08-03):** a customer told Meghan she found us by
googling *"swim suits near me."* Not our name — a generic product-plus-proximity search. That means
local discovery search is bringing in people who had never heard of us, and we have no idea how
much of that traffic we're winning or missing.

Implication: local SEO and possibly cheap paid search on product-category-plus-location terms
("swim suits near me", "propane east sandwich", "beach chairs cape cod") may be a high-leverage,
low-cost lever. Worth instrumenting before spending.

**Ask the floor.** Meghan asking "how did you find us?" produced more insight than the analytics
stack did. Anecdotes like this belong in `INBOX.md` — they're data.

### Maps data availability
- **Google Business Profile** — has a real API. Maps views, direction requests, and the search terms
  that surfaced the listing. Worth wiring up; the search-terms data speaks directly to the above.
- **Apple Maps** — Apple Business Connect has **no public analytics API.** Direction requests and
  place-card views are visible in the dashboard at businessconnect.apple.com but cannot be
  automated. Check manually; note anything notable in `INBOX.md`.

---

## Open questions

Things the agent should not guess at. Answer these here and they stop being open.

### SNP 500 — tracked as a project
A framework Sandy built for in-store analysis (the name plays on the S&P 500). Developed primarily
in ChatGPT, **not yet transferred here and not active.** It was meant to be ready for the 2026
season and wasn't.

See `projects/snp-500.md`. Until the definition lands there, **the agent must not invent or
approximate the criteria** — a guessed framework applied to real inventory decisions is worse than
no framework at all.

### Others
- Which tide stage actually correlates with beach traffic (if any)?
- What is the real margin picture per channel? TikTok's "not worth the effort" is a judgment we
  can't currently verify against numbers.
- Vendor lead times for everything other than the Alibaba items.

---

## Standing instructions for the agent

1. **Two independent analyses.** In-store and online get judged on their own terms. Never blend.
2. **Never report the expected as a finding.** In-store > online at summer peak is table stakes.
3. **Weather-adjust every day-over-day claim.** Conditions first, then the number.
4. **Lead time before reorder advice.** Say which of the three reorder answers applies and why.
5. **Check what's actually selling on TikTok** before characterizing the channel.
6. **Be honest about small numbers.** 4 online orders is not a trend, and neither is a 50% swing on
   a base of 2.
7. **Say when you don't know.** A flagged unknown is more useful than a confident guess.
8. **Keep year-to-date pace against the $190k target in view**, adjusted for season position — and
   say whether that pacing is based on real prior-year history or the estimated fallback curve.
