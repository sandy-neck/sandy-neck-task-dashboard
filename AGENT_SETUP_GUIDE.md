# Sandy Neck Analytics Agent — Setup Guide

Work through these in order. Steps 1–4 get you a working daily email. Steps 5–7 add the optional data sources over time.

---

## Step 1 — Shopify Access Token
**Time: ~10 min**

This lets the agent read your store data (orders, revenue, products, conversion, inventory).

> **Note:** The old "Develop apps" option inside Shopify Admin is deprecated — Shopify now requires custom apps to be created via the **Shopify Partners / Developer Dashboard** at [partners.shopify.com](https://partners.shopify.com). Your existing app there (with a Client ID and Client Secret) is exactly what you need.

**You already have the app — you just need to get the store access token from it.**

**Step A — Open the OAuth authorization URL in your browser**

While logged into your Shopify Admin, paste this URL into your browser, replacing `YOUR_CLIENT_ID`:

```
https://sandy-neck-provisions-8044.myshopify.com/admin/oauth/authorize?client_id=YOUR_CLIENT_ID&scope=read_analytics,read_customers,read_inventory,read_orders,read_products,read_reports&redirect_uri=https://example.com
```

Click **Install** when the Shopify prompt appears. You'll be redirected to a URL like:
`https://example.com/?code=SOME_CODE&shop=sandy-neck-provisions-8044.myshopify.com&...`

Copy the `code` value out of that URL.

**Step B — Exchange the code for a permanent token**

In your terminal, run this (fill in Client ID, Client Secret, and the code from Step A):

```bash
curl -s -X POST \
  "https://sandy-neck-provisions-8044.myshopify.com/admin/oauth/access_token" \
  -H "Content-Type: application/json" \
  -d '{"client_id":"YOUR_CLIENT_ID","client_secret":"YOUR_CLIENT_SECRET","code":"CODE_FROM_STEP_A"}'
```

The response looks like: `{"access_token":"shpat_xxxx...","scope":"read_orders,..."}`

That `access_token` is your permanent store credential.

**If you need to create a new Partners Dashboard app:**
1. [partners.shopify.com](https://partners.shopify.com) → **Apps → Create app → Create app manually**
2. Name: `Analytics Agent` → **Create**
3. Under **Configuration**, set redirect URI to `https://example.com` and enable the scopes above
4. Then follow Steps A and B

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `SHOPIFY_SHOP_DOMAIN` | `sandy-neck-provisions-8044.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | the `access_token` from Step B (`shpat_...`) |

---

## Step 2 — Anthropic API Key
**Time: ~3 min**

This is what powers the analysis and email writing.

1. Go to **console.anthropic.com** → sign in
2. Left sidebar → **API Keys** → **Create Key**
3. Name it `Sandy Neck Analytics` → create → copy the key (starts with `sk-ant-`)

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | the key you just copied |

---

## Step 3 — Email Sending
**Time: ~5–10 min**

The email will be **sent to** `goodvibes@sandyneckprovisions.com`.
The email will be **sent from** the account you configure here.

**Recommended: send from `goodvibes@sandyneckprovisions.com` directly** — it reads like an internal note.
This works if your email is Google Workspace (Gmail-based). If it's not, use Option B.

### Option A — Google Workspace / Gmail (recommended)

1. Sign into the Google account for `goodvibes@sandyneckprovisions.com`
2. Go to **myaccount.google.com → Security**
3. Confirm **2-Step Verification** is turned on (required — turn it on if not)
4. In the Security page search bar, type `App passwords` → click the result
5. Under "App name" enter `Sandy Neck Analytics` → **Create**
6. Google shows a 16-character password (e.g. `abcd efgh ijkl mnop`) — copy it (no spaces when you paste it)

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | `goodvibes@sandyneckprovisions.com` |
| `SMTP_PASSWORD` | the 16-character App Password (no spaces) |

### Option B — Non-Gmail email host

Create a free Gmail account (e.g. `sandyneck.analytics@gmail.com`), then follow Option A steps with that account. Add one extra secret so the From name is clear:

| Secret name | Value |
|---|---|
| `REPORT_SENDER_NAME` | `Alex (Sandy Neck Analytics)` |

---

## Step 4 — First Test Run
**Do this once Steps 1–3 are complete.**

1. Go to your GitHub repo → **Actions** tab (top nav)
2. Left sidebar: click **Daily Analytics Report**
3. Top-right: click **Run workflow** → **Run workflow** (green button)
4. The run takes about 60–90 seconds — watch it or check back
5. Check `goodvibes@sandyneckprovisions.com` for the email

If the run fails: click the failed run → click the job name → read the log. It will say exactly which step failed and why.

---

## Step 5 — Klaviyo
**Time: ~3 min | Add any time after Step 4**

1. Log into Klaviyo → **Settings** (top-right gear icon) → **API Keys**
2. Click **Create Private API Key**
3. Name: `Analytics Agent` | Scope: **Read-only** → **Create**
4. Copy the key

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `KLAVIYO_PRIVATE_KEY` | the key you just copied |

---

## Step 6 — Google Business Profile + Search Console
**Time: ~45 min | Do when you have a focused block**

This adds the "how people find you on Maps" section and surfaces Google Ads keyword opportunities (e.g. "cape cod seafood delivery" — 620 impressions/week, only 4.5% CTR — that's a cheap ad).

### Part A: Create a Google Cloud service account

1. Go to **console.cloud.google.com**
2. Top nav: click the project dropdown → **New Project** → name it `Sandy Neck Analytics` → **Create**
3. Make sure the new project is selected, then go to **APIs & Services → Library**
4. Search for and enable each of these (click → **Enable**):
   - `Business Profile Performance API`
   - `Google Search Console API`
5. **APIs & Services → Credentials → Create Credentials → Service account**
6. Name: `sandy-neck-analytics` → **Create and continue** → skip the optional steps → **Done**
7. Click the service account row → **Keys** tab → **Add Key → Create new key → JSON → Create**
8. A `.json` file downloads — open it in a text editor and copy the entire contents

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | paste the entire JSON file contents |
| `SEARCH_CONSOLE_SITE_URL` | `https://sandyneckprovisions.com/` |

### Part B: Grant Search Console access

1. Go to **search.google.com/search-console**
2. Select your property → **Settings** (gear icon, bottom-left) → **Users and permissions**
3. **Add User** → paste the `client_email` from your JSON file
   (looks like `sandy-neck-analytics@sandy-neck-analytics.iam.gserviceaccount.com`)
4. Permission level: **Full** → **Add**

### Part C: Grant Business Profile access

1. Go to **business.google.com** → find your Sandy Neck Provisions listing
2. Click the three-dot menu → **Business Profile settings** → **Managers**
3. **Add** → paste the same service account email → Role: **Manager** → **Invite**

### Part D: Find your location ID

You need this to pull Maps data. Run this once from a terminal where you have gcloud installed,
or reach out and I can help you get it:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://mybusinessbusinessinformation.googleapis.com/v1/accounts/YOUR_ACCOUNT_ID/locations"
```

The response includes a `name` field like `accounts/123456/locations/789012` — that's your location ID.

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `GOOGLE_BUSINESS_LOCATION` | `accounts/XXXXX/locations/YYYYY` |

---

## Step 7 — Social Media APIs
**Add over time — these require developer app review (1–2 weeks each)**

Start with Instagram/Facebook since one developer app covers both platforms.
YouTube is the fastest (no review needed, just an API key).

### YouTube (~5 min, no review required)

1. Go to **console.cloud.google.com** → use the same project from Step 6 (or create a new one)
2. **APIs & Services → Library** → search `YouTube Data API v3` → **Enable**
3. **Credentials → Create Credentials → API Key** → copy it
4. Find your Channel ID: **YouTube Studio → Settings → Channel → Advanced settings**

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `YOUTUBE_API_KEY` | the API key |
| `YOUTUBE_CHANNEL_ID` | your channel ID (starts with `UC...`) |

---

### Instagram + Facebook (~1 week for app review)

Both platforms are connected through a single Meta developer app.
Your Instagram account must be set to **Business or Creator** and linked to your Facebook Page.

1. Go to **developers.facebook.com** → **My Apps → Create App**
2. Use case: **Other** → **Business** → Next
3. Name: `Sandy Neck Analytics` → **Create app**
4. From the app dashboard, add these products (click **Set Up** next to each):
   - **Instagram Graph API**
   - **Facebook Login for Business**
5. Go to **App Review → Permissions and Features** → request:
   - `pages_read_engagement`
   - `instagram_basic`
   - `instagram_manage_insights`
   - `pages_show_list`
6. Complete the App Review submission (requires a brief description of use case — "internal analytics for our own business page")
7. Once approved, generate a **long-lived Page access token** via the Graph API Explorer
8. Find your Instagram Business Account ID and Facebook Page ID from your Page settings

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `INSTAGRAM_ACCESS_TOKEN` | long-lived Page access token |
| `INSTAGRAM_ACCOUNT_ID` | Instagram Business Account ID |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | same long-lived token |
| `FACEBOOK_PAGE_ID` | Facebook Page ID |

---

### TikTok (~1–2 weeks for app review)

1. Go to **developers.tiktok.com** → **Manage apps → Create app**
2. Category: **Content tools** → fill in app details
3. Under **Products**, add **Login Kit** and **Content Posting API**
4. Request scopes: `user.info.basic`, `video.list`, `user.info.stats`
5. Submit for review
6. Once approved, complete the OAuth flow to get your access token

**Add to GitHub Secrets:**
| Secret name | Value |
|---|---|
| `TIKTOK_ACCESS_TOKEN` | your OAuth access token |

---

## Where to add all these secrets

**GitHub → your repo → Settings → Secrets and variables → Actions → New repository secret**

Each secret is just a name + value pair. The agent reads them automatically when it runs.

---

## Schedule

The agent runs automatically at **7:00 AM ET every day**. You can also trigger it manually anytime from the Actions tab.

---

## Apple Maps

Apple Maps Connect does not have a public API. You can view direction requests, place card views, and engagement manually at **businessconnect.apple.com** — but it cannot be automated.
