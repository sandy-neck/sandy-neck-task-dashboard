# SEO / AI legibility — catalogue enrichment

**Status:** In progress — initial pass shipped 2026-08-19, Routine now edits every 3 days
**Owner:** BJ
**Opened:** 2026-08-19
**Measurement window:** the real test is **June–August 2027**, not this autumn
**Intervention ID:** `SNP-AEO-2026-08-19`

| Key date | What |
|---|---|
| 2026-07-22 → 2026-08-18 | Suggested 28-day pre-intervention baseline window |
| 2026-08-19 / 2026-08-20 | Applied |
| 2026-09-02 | First read expected |
| 2026-11-12 | Full read expected |
| 2027-06-01 → 2027-08-31 | Seasonal read required — the real test |

Baseline snapshot at intervention: 1,016 active products, 448 modified in the initial window, 356
still untyped (the control cohort), 9 greenhead-tagged, 2 piping-plover-tagged.

---

## What shipped on 2026-08-19

Five segments, tracked separately because they work through different mechanisms and on different
timescales. Do not blend them.

| | Segment | Scale | Mechanism | Lag |
|---|---|---|---|---|
| **A** | Topic-authority shirts | 4 products | Factual explainers — species, range, season timing, why closures happen — written to be citable by an AI answering a research question. Names the Jersey Shore, Long Island, Sandy Hook, Fire Island, Cape Point. | Longest. Widest upside. |
| **B** | Descriptions | 60 written, 59 live | Brand-voice opener plus a Details block with real specs from vendor sites and live variant data. Two were factual corrections where copy contradicted the variants. | Medium |
| **C** | Structured data | 414 products | Specific `productType` plus 4–9 topical tags each, feeding JSON-LD. Invisible to humans; the mechanism is AI agent legibility. | Medium |
| **D** | URLs | 2 changes, both 301'd | Plover tee slug was `sandy-neck-lighthouse-coastal-tee`. | Short |
| **E** | Merchandising | 15 collections reordered by revenue, menu rename, skimboards split out, 6 archives | **Affects conversion, not acquisition.** | Immediate |

**Segment E is the one to be careful with: never attribute a traffic change to it.** It changes what
happens to people already on the site, not how many arrive.

---

## Why the measurement is hard, and how not to get it wrong

### 1. The seasonality trap — the big one

This landed **August 19 at a seasonal Cape business**. Three things are falling at once, none of them
because of SEO:

- The season itself
- **Greenhead search interest** — peaks late July / first week of August. Already passed.
- **Plover closure searches** — peak June–August. Passing now.

**Segment A will likely look flat or down through autumn even if it is working perfectly.** Reading
that as failure would be wrong.

How to measure instead:
- **Year-over-year same-week**, not week-over-week
- **Impressions and average position**, not sessions — position can improve while traffic falls
- Treat **June–August 2027** as the real test

### 2. There is a genuine control group, and it is shrinking

**356 active products** had no `productType` and no enrichment at ship time — same site, same domain
authority, same seasonality, no treatment. That is a real control group, which most SEO work never
gets.

Snapshot taken 2026-08-19 → `brain/reference/seo-control-group-2026-08-19.json`
Query: `status:active AND product_type:''`

It only shrinks from here: the Routine works **price-descending** and starts converting this cohort
within days. The snapshot is the baseline and cannot be recreated later.

### 3. This is not a step change

The Routine edits the catalogue **every 3 days** from here. That means there is no clean
before/after line — there is a continuous treatment.

**Log each digest email as its own dated micro-variance in `events.md`**, or later movement gets
misattributed to the initial pass.

---

## Metrics to track, by horizon

| Horizon | Metric | Segment | Expected direction |
|---|---|---|---|
| Week 0–2 | Crawl rate, pages crawled/day | All | Up (448 pages changed) |
| Week 0–4 | 301 redirect resolution on the 2 changed URLs | D | Temporary dip, then recovery |
| Week 2–6 | Search Console impressions, product pages | A, B, C | Up |
| Week 2–6 | Average position, non-brand queries | A, B | Improving |
| Week 6–12 | Organic sessions to `/products/*` | B, C | Up |
| Week 6–12 | Referrals from AI sources | A, C | Up from near-zero |
| Week 6–12 | Non-brand share of organic entrances | A | Up |
| Ongoing | Engagement rate / time on page, enriched vs. control | B | Enriched higher |
| Jun–Aug 2027 | Sessions to greenhead + plover pages | A | The real test |

AI referral sources to segment out specifically: chatgpt.com, perplexity.ai, claude.ai,
gemini.google.com, copilot.microsoft.com. These were likely near-zero pre-intervention, so even
small absolute numbers are signal.

Other confounders to log if they occur: paid spend changes, email/social pushes, inventory going
out of stock on enriched products, and the Routine's own ongoing edits.

---

## Predictions

Six falsifiable predictions were written at ship time so this can be *scored* rather than
rationalised after the fact:

1. **Segment D:** the 2 changed URLs dip in organic entrances within 2 weeks, recovering to at
   least baseline by week 6. If they don't recover by week 8, the redirects need checking.
2. **Segment A:** near-zero session movement through October 2026 (demand curve falling); Search
   Console impressions for non-brand informational queries rise measurably by week 6.
3. **Segment A, primary:** June–August 2027 sessions to the 4 shirt pages exceed June–August 2026
   by a margin larger than the sitewide YoY change.
4. **Segment B:** enriched product pages show higher engagement rate than the untyped control
   cohort within 8 weeks, controlling for price band.
5. **Segment C:** no measurable direct organic effect; effect appears in AI referral sources and
   shopping-feed surfacing, not classic organic.
6. **Sitewide:** total organic sessions decline through autumn on seasonality alone.

> **Sitewide organic sessions will decline through autumn on seasonality alone — and that is
> expected, not evidence of failure.**

---

## Known caveat on the first Routine run

The ~470 products already done were **not retroactively tagged**, so the first pass re-examines some
finished work. It is self-correcting and price-descending, so the top SKUs get a second look, but
**the first digest may be lighter than it looks** — some of its work is re-treading.

The untyped high-value items it will hit first are real gaps — also the matched-pair control set
for comparing enriched vs. still-untyped, normalized for price band:
Turtlebox Gen 2 ($399), Sowkt Water Mat ($465), Wadabuggy Beach ($465), Wadabuggy Beach Buggy
($385), Premium Beach Cabana ($325), ZAP Large Wedge Skimboard ($279), ZAP Core Skimboard 48"
($215), ZAP Medium Wedge ($215), The Wind Screen ($199.99), Dune High Beach Chair ($179.99), NRS
Wild River Tube ($174.95), GCI Slim Fold Table XL ($135), Sun Ninja 4 Person Tent ($119), Gully
Child Beach Chair ($104.99).

## Still open

- Homepage delivery section: Height → Medium
- Publish the 18 collection-template theme files

## Next action

Nothing until the digests start arriving. Log each one in `events.md` with its date. Resist
reading autumn traffic as a verdict. First read expected 2026-09-02; treat anything before that as
too early to mean anything.

## Log

- **2026-08-19** — Initial pass shipped: 4 topic-authority shirts, 60 descriptions (59 live), 414
  products with structured data, 2 URL changes (301'd), 15 collections reordered. Control group
  snapshotted at 356 untreated active products. Routine begins editing every 3 days.
- **2026-08-20** — Full intervention record logged (predictions, confounders, metrics-to-track
  table, key dates) — see sections above. No new catalogue changes; this is documentation of the
  8/19 pass, formalized so it can be scored on schedule.
