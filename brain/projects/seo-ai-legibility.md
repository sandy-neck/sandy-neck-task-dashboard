# SEO / AI legibility — catalogue enrichment

**Status:** In progress — initial pass shipped 2026-08-19, Routine now edits every 3 days
**Owner:** BJ
**Opened:** 2026-08-19
**Measurement window:** the real test is **June–August 2027**, not this autumn

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

## Predictions

Six falsifiable predictions were written at ship time so this can be *scored* rather than
rationalised after the fact. The most important:

> **Sitewide organic sessions will decline through autumn on seasonality alone — and that is
> expected, not evidence of failure.**

<!-- The other five predictions live in §6 of the source document and have not been transferred here
     yet. Paste them in; unscored predictions are just opinions with better grammar. -->

---

## Known caveat on the first Routine run

The ~470 products already done were **not retroactively tagged**, so the first pass re-examines some
finished work. It is self-correcting and price-descending, so the top SKUs get a second look, but
**the first digest may be lighter than it looks** — some of its work is re-treading.

The untyped high-value items it will hit first are real gaps:
- Turtlebox — $399
- Sowkt Water Mat — $465
- Wadabuggy — $465
- The whole ZAP skimboard line

## Still open

- Homepage delivery section: Height → Medium
- Publish the 18 collection-template theme files

## Next action

**BJ:** paste the remaining five predictions into the section above so they can be scored.

Then: nothing until the digests start arriving. Log each one in `events.md` with its date. Resist
reading autumn traffic as a verdict.

## Log

- **2026-08-19** — Initial pass shipped: 4 topic-authority shirts, 60 descriptions (59 live), 414
  products with structured data, 2 URL changes (301'd), 15 collections reordered. Control group
  snapshotted at 356 untreated active products. Routine begins editing every 3 days.
