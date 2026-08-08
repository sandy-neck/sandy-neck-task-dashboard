# Local Discovery Setup — Google Business Profile + Search Console

This connects two data sources to the daily analytics agent so it can answer: **how are people finding us, and what are they actually searching for?**

The reason this matters: a customer recently told staff she found the store by googling "swim suits near me" — not the store's name, a generic category-and-proximity search. That kind of search is invisible in Shopify data. This setup surfaces it.

---

## What this gets you

**From Google Business Profile:** Maps views, direction requests, phone taps, website clicks — plus (this is the important one) the actual **search terms** people typed that surfaced your listing. This is the direct answer to the "swim suits near me" question: it tells you how many searches like that exist and what they say.

**From Google Search Console:** the organic search queries that bring people to sandyneckprovisions.com, plus impressions, click-through rate, and average position for each query. This tells you where you're ranking well and where you're getting impressions but no clicks — the cheap-paid-search opportunities.

Together, these tell you whether to double down on SEO for specific phrases, or run a small paid campaign against searches you're not winning organically.

---

## Part 1 — Google Business Profile

**Time: ~30–45 min of your own work, plus several days of waiting on Google — start this first.**

### Step 1 — Create a Google Cloud project
**Time: ~5 min**

1. Go to **console.cloud.google.com**
2. Top nav → project dropdown → **New Project** → name it something like `Sandy Neck Local Discovery` → **Create**
3. Make sure the new project is selected in the dropdown before continuing

### Step 2 — Request Business Profile API access (DO THIS FIRST — it's slow)
**Time: ~10 min to submit, then a wait of several days**

> **This is the gotcha that trips people up.** Unlike most Google APIs, the Business Profile APIs are **access-restricted** — you can't just click "Enable" in the API Library. Google requires you to submit a **Business Profile API access request form** first, and an approval that is **not instant**. It commonly takes several days to come through.
>
> Submit this request today, before doing anything else in this guide, so the wait runs in the background while you handle Search Console and other work.

1. Search for "Business Profile API access request" from within Google's developer documentation for Business Profile — Google moves this form around, so search for it rather than relying on a bookmark
2. Fill out the form (it will ask for basic info about your business and how you intend to use the API — "internal analytics for our own business listing" is accurate and sufficient)
3. Submit and wait for the approval email

Once approved, the specific API you need to enable (back in **APIs & Services → Library** in your Cloud project) is the **Business Profile Performance API** — this is what provides the search-terms and views/actions data. You'll also use the related **My Business Business Information API** briefly in Step 5 below, just to look up your location ID.

### Step 3 — Create a service account and download the key
**Time: ~5 min — can be done while waiting on Step 2's approval**

1. In your Cloud project: **APIs & Services → Credentials → Create Credentials → Service account**
2. Name it something like `sandy-neck-local-discovery` → **Create and continue** → skip the optional role/access steps → **Done**
3. Click into the service account row → **Keys** tab → **Add Key → Create new key → JSON → Create**
4. A `.json` file downloads to your computer — keep it somewhere safe, you'll need its full contents in Part 3

### Step 4 — Grant the service account access to your listing
**Time: ~5 min — do this once Step 2 is approved**

The service account is its own "user" — it needs to be added to your listing just like a person would be.

1. Open the downloaded JSON key file in a text editor and find the `client_email` field. It looks something like `sandy-neck-local-discovery@your-project-id.iam.gserviceaccount.com` — copy it
2. Go to **business.google.com** → open the Sandy Neck Provisions listing
3. Find **Business Profile settings → Managers** (may also show as a people/settings icon depending on the current layout)
4. **Add** (or "Add manager") → paste the service account's email → Role: **Manager** → confirm/invite

### Step 5 — Find your location ID
**Time: ~5–10 min, once the service account is approved and has access**

The agent needs a location ID in the format `accounts/{accountId}/locations/{locationId}`.

1. This is retrieved by calling the **My Business Business Information API**'s `accounts.locations.list` endpoint, authenticated as your service account
2. If you're comfortable with a terminal, you can run this yourself; if not, once the service account is set up and approved, ask Claude to help you make this call — it just needs the service account credentials and will walk you through it
3. The response includes a `name` field shaped like `accounts/123456789/locations/987654321` — that whole string is your location ID

---

## Part 2 — Google Search Console

**Time: ~10 min total. This part is NOT access-restricted — you can do it today, right now, while Part 1 is waiting on approval.**

### Step 1 — Enable the API
**Time: ~2 min**

1. In the same Cloud project from Part 1 (**console.cloud.google.com**) → **APIs & Services → Library**
2. Search for `Google Search Console API` → **Enable**

### Step 2 — Grant the service account access
**Time: ~5 min**

1. Go to **search.google.com/search-console**
2. Select the sandyneckprovisions.com property from the property picker
3. **Settings** → **Users and permissions**
4. **Add user** → paste the service account's `client_email` (same one from the JSON key file, Part 1 Step 4)
5. Permission level: **Full** → **Add**

**Prerequisite to check:** the site property must already be a *verified* property in Search Console. If sandyneckprovisions.com isn't showing up as verified when you go to add the user, that verification needs to happen first — it's a separate, one-time process tied to proving domain ownership.

---

## Part 3 — Add the secrets to GitHub

**Time: ~5 min**

Go to **GitHub → your repo → Settings → Secrets and variables → Actions → New repository secret** and add each of these:

| Secret name | Value |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | The **entire contents** of the downloaded JSON key file, pasted as-is (open the file, select all, copy, paste — don't retype or reformat it) |
| `GOOGLE_BUSINESS_LOCATION` | The `accounts/{accountId}/locations/{locationId}` string from Part 1, Step 5 |
| `SEARCH_CONSOLE_SITE_URL` | `https://sandyneckprovisions.com/` |

The agent runs in **sample-data mode** until `GOOGLE_SERVICE_ACCOUNT_JSON` is set — it'll show placeholder numbers so you can see the report format. Once that secret is added, it switches to live data automatically on the next run. No code changes needed.

---

## Part 4 — Apple Maps

Being direct about this one: **Apple Business Connect has no public analytics API.** There is no automation path here — this isn't a limitation we can engineer around, it's just not offered.

What you can do instead:

- **Check manually, occasionally.** Sign in at **businessconnect.apple.com** to see place card views, direction requests, and search/engagement stats for the listing. There's no need to do this daily — a periodic glance (monthly, or whenever you think of it) is enough.
- **When you see something worth noting**, add a line to `brain/INBOX.md` — that's how the daily agent picks up manual observations and folds them into its analysis alongside the automated data.
- **The genuinely useful thing you can do there:** make sure the listing's categories, photos, and hours are accurate and complete. That's what determines whether Sandy Neck Provisions surfaces at all for category searches like "swim suits near me" on Apple Maps — it's a lever you control directly, no API needed.

---

## Which to do first

1. **Right now:** submit the Business Profile API access request (Part 1, Step 2). It's the long pole — get the clock started.
2. **Today, while that's pending:** do all of Part 2 (Search Console) — it's unrestricted and takes about 10 minutes.
3. **Also today, while waiting:** create the Cloud project and service account (Part 1, Steps 1 and 3) so they're ready the moment approval comes through.
4. **Once approved:** finish Part 1 (grant Manager access, find the location ID) and add all three secrets from Part 3.
5. **Ongoing:** treat Apple Maps (Part 4) as a recurring manual check, not a setup task — there's nothing to "finish" there beyond keeping the listing accurate.
