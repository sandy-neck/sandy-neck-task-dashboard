# Sandy Neck Task Dashboard — Agent Notes

## Shopify Authentication (IMPORTANT)

**Shopify Admin custom app creation is deprecated.** The "Develop apps" option inside Shopify Admin (Settings → Apps and sales channels) no longer works for creating new custom apps.

All custom Shopify apps must be created and managed via the **Shopify Partners / Developer Dashboard** at [partners.shopify.com](https://partners.shopify.com).

### How to get a store access token from a Partners Dashboard app

The Partners Dashboard app has a **Client ID** and **Client Secret** (not a direct access token). To get a permanent store-specific access token (`shpat_...`):

1. **Authorize:** open this URL in a browser while logged into Shopify Admin:
   ```
   https://STORE.myshopify.com/admin/oauth/authorize?client_id=CLIENT_ID&scope=SCOPES&redirect_uri=https://example.com
   ```
   Click Install → copy the `code` from the redirect URL.

2. **Exchange:** run:
   ```bash
   curl -s -X POST "https://STORE.myshopify.com/admin/oauth/access_token" \
     -H "Content-Type: application/json" \
     -d '{"client_id":"CLIENT_ID","client_secret":"CLIENT_SECRET","code":"CODE"}'
   ```
   The response `access_token` field is the permanent store token.

### Sandy Neck store details

- Shop domain: `sandy-neck-provisions-8044.myshopify.com`
- Required scopes: `read_analytics,read_customers,read_inventory,read_orders,read_products,read_reports`
- ShopifyQL API version: `2025-04`
- ShopifyQL confirmed working syntax: `TIMESERIES day` (not `GRANULARITY day`), `SINCE -7d UNTIL today`

### MCP vs. scheduled agent

The session-bound Shopify MCP tools (`run-analytics-query`, etc.) work for interactive use only — they cannot be used in scheduled GitHub Actions. The analytics agent uses direct HTTP calls to the Shopify Admin GraphQL API with the `SHOPIFY_ACCESS_TOKEN` header.
