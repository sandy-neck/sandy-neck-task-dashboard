# Sandy Neck Provisions — Analytics Agent Setup Guide

The daily analytics agent runs at **7 AM ET every day** via GitHub Actions.
It emails a report to sandy@sandyneckprovisions.com covering Shopify store performance,
Klaviyo email marketing, social media, and Google local presence (Maps + Search Console).

All optional data sources run in "sample data" mode until real credentials are added.
The Shopify and email secrets are the only ones required to start.

---

## How to Add a Secret

**GitHub → Repository → Settings → Secrets and variables → Actions → New repository secret**

---

## Required Secrets

### 1. Shopify

| Secret | Value |
|--------|-------|
| `SHOPIFY_SHOP_DOMAIN` | `sandy-neck-provisions-8044.myshopify.com` |
| `SHOPIFY_ACCESS_TOKEN` | Admin API access token — see below |

**Getting the access token:**
1. Shopify Admin → **Settings → Apps and sales channels → Develop apps**
2. Create app → name it "Analytics Agent"
3. **Configure Admin API scopes** — enable:
   - `read_orders` · `read_products` · `read_customers`
   - `read_inventory` · `read_analytics` · `read_reports`
4. **Install app** → copy the Admin API access token (shown once — save it)

> **Note on architecture:** The in-session Shopify MCP tools (`run-analytics-query`, etc.) are great
> for interactive analysis right now. The scheduled agent uses the same Shopify Admin API and
> identical ShopifyQL syntax — just authenticated directly rather than via a session-bound MCP server.

---

### 2. Anthropic

| Secret | Value |
|--------|-------|
| `ANTHROPIC_API_KEY` | From https://console.anthropic.com → API Keys |

---

### 3. Email (Gmail)

| Secret | Value |
|--------|-------|
| `SMTP_HOST` | `smtp.gmail.com` |
| `SMTP_PORT` | `587` |
| `SMTP_USERNAME` | Your sending Gmail address |
| `SMTP_PASSWORD` | Gmail **App Password** — see below |
| `REPORT_RECIPIENT` | `sandy@sandyneckprovisions.com` |

**Creating a Gmail App Password:**
1. Google Account → Security → 2-Step Verification (must be on)
2. Search "App passwords" → Create → name it "Sandy Neck Analytics"
3. Copy the 16-character code — that's your `SMTP_PASSWORD`

> **Alternative (SendGrid):** `SMTP_HOST=smtp.sendgrid.net`, `SMTP_PORT=587`,
> `SMTP_USERNAME=apikey`, `SMTP_PASSWORD=<sendgrid-api-key>`. Free up to 100 emails/day.

---

## Optional Secrets (sample data shown until configured)

### Klaviyo

| Secret | Value |
|--------|-------|
| `KLAVIYO_PRIVATE_KEY` | Klaviyo → Settings → API Keys → Create Private API Key |

---

### Instagram + Facebook

Both platforms use a single Meta developer app via the Graph API.

| Secret | Value |
|--------|-------|
| `INSTAGRAM_ACCESS_TOKEN` | Long-lived Page access token (see steps below) |
| `INSTAGRAM_ACCOUNT_ID` | Your Instagram Business Account ID |
| `FACEBOOK_PAGE_ACCESS_TOKEN` | Same long-lived token |
| `FACEBOOK_PAGE_ID` | Your Facebook Page ID |

**Setup (allow ~1 week for app review):**
1. https://developers.facebook.com → Create App → **Business type**
2. Add products: **Instagram Graph API** + **Pages API**
3. Request permissions via App Review:
   `pages_read_engagement`, `instagram_basic`, `instagram_manage_insights`, `pages_show_list`
4. Generate a **long-lived Page access token** via the Graph API Explorer
5. Your Instagram account must be a **Business or Creator account** linked to your Facebook Page

---

### TikTok

| Secret | Value |
|--------|-------|
| `TIKTOK_ACCESS_TOKEN` | OAuth token from TikTok developer app |

**Setup (allow 1-2 weeks for app review):**
1. https://developers.tiktok.com → Create app → **Content/Display type**
2. Request scopes: `user.info.basic`, `video.list`, `user.info.stats`
3. Complete OAuth flow to get your access token

---

### YouTube

| Secret | Value |
|--------|-------|
| `YOUTUBE_API_KEY` | Google Cloud Console → APIs → YouTube Data API v3 → Credentials |
| `YOUTUBE_CHANNEL_ID` | YouTube Studio → Settings → Channel → Advanced settings |

**Setup:**
1. https://console.cloud.google.com → New project → Enable **YouTube Data API v3**
2. Create an **API key** (no OAuth needed for public channel data)

---

### Google Business Profile + Search Console

This powers the "How people find Sandy Neck" section: Maps views, direction requests,
search keywords (including discovery terms like "propane east sandwich"), and organic
search CTR opportunities for SEO and Google Ads.

| Secret | Value |
|--------|-------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full JSON content of a Google service account key |
| `GOOGLE_BUSINESS_LOCATION` | e.g. `accounts/123456789/locations/987654321` |
| `SEARCH_CONSOLE_SITE_URL` | `https://sandyneckprovisions.com/` |

**Setup steps:**

1. **Google Cloud Console** (https://console.cloud.google.com):
   - Create a new project or use an existing one
   - Enable these APIs:
     - **Business Profile Performance API**
     - **Google Search Console API**
   - Create a **Service Account** → generate a JSON key → save the full JSON

2. **Grant Search Console access:**
   - Go to https://search.google.com/search-console
   - Settings → Users and permissions → Add user → paste the service account email
   - Permission level: **Full**

3. **Grant Business Profile access:**
   - Go to https://business.google.com
   - Settings → Managers → Add → paste the service account email
   - Role: **Manager**

4. **Find your location name:**
   - Call the Business Profile API to list locations:
     ```bash
     curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
       "https://mybusinessbusinessinformation.googleapis.com/v1/accounts/YOUR_ACCOUNT_ID/locations"
     ```
   - Copy the full `name` field (e.g. `accounts/123456/locations/789012`)

5. **Store the JSON key as a GitHub secret:**
   - Copy the entire contents of the downloaded JSON key file
   - Add as `GOOGLE_SERVICE_ACCOUNT_JSON`

**Apple Maps Connect:** Apple does not offer a programmatic API for Maps analytics.
You can view stats manually at https://businessconnect.apple.com — direction requests,
place card views, and engagement are available in the dashboard but cannot be automated.

---

## Running Manually

**Via GitHub UI:**
GitHub → Actions → "Daily Analytics Report" → "Run workflow"

**Via CLI:**
```bash
gh workflow run daily-analytics.yml
```

---

## Testing Locally

```bash
cd agent
pip install -r ../agent_requirements.txt

# Required
export SHOPIFY_SHOP_DOMAIN="sandy-neck-provisions-8044.myshopify.com"
export SHOPIFY_ACCESS_TOKEN="shpat_..."
export ANTHROPIC_API_KEY="sk-ant-..."
export SMTP_USERNAME="you@gmail.com"
export SMTP_PASSWORD="xxxx xxxx xxxx xxxx"
export REPORT_RECIPIENT="sandy@sandyneckprovisions.com"

# Optional sources — run in stub mode for testing
export SOCIAL_STUB_MODE=true
export KLAVIYO_STUB_MODE=true
export GOOGLE_STUB_MODE=true

python daily_analytics.py
```

---

## What's in the Report

| Section | Source | Available now? |
|---------|--------|---------------|
| Revenue, orders, AOV | Shopify (ShopifyQL) | ✅ after Shopify secret |
| Conversion funnel | Shopify (ShopifyQL) | ✅ after Shopify secret |
| Traffic attribution by source | Shopify (ShopifyQL) | ✅ after Shopify secret |
| Top products (7d) | Shopify (ShopifyQL) | ✅ after Shopify secret |
| Low inventory alerts | Shopify (GraphQL) | ✅ after Shopify secret |
| New vs. returning customers | Shopify (ShopifyQL) | ✅ after Shopify secret |
| AI insights + recommendations | Claude (Anthropic API) | ✅ after Anthropic secret |
| Email campaign performance | Klaviyo API | 🟡 sample until `KLAVIYO_PRIVATE_KEY` |
| Instagram performance | Meta Graph API | 🟡 sample until Meta secrets |
| Facebook performance | Meta Graph API | 🟡 sample until Meta secrets |
| TikTok performance | TikTok API | 🟡 sample until `TIKTOK_ACCESS_TOKEN` |
| YouTube performance | YouTube Data API | 🟡 sample until YouTube secrets |
| Maps views & direction requests | Google Business Profile API | 🟡 sample until Google secrets |
| Organic search queries & CTR | Google Search Console API | 🟡 sample until Google secrets |
| SEO & Google Ads opportunities | Synthesized by Claude | 🟡 sample until Google secrets |

**Sample data** sections are clearly labeled in the email. They use realistic placeholder
values so you can see the full report format from day one.
