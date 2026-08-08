# Sandy Neck Task Dashboard — Agent Notes

## Shopify Authentication (IMPORTANT)

**Shopify Admin custom app creation is deprecated.** The "Develop apps" option inside Shopify Admin (Settings → Apps and sales channels) no longer works for creating new custom apps.

All custom Shopify apps must be created and managed via the **Shopify Developer Dashboard** at [dev.shopify.com](https://dev.shopify.com).

### How to get a store access token from a Developer Dashboard app

The Developer Dashboard app has a **Client ID** and **Client Secret** (not a direct access token). To get a permanent store-specific access token (`shpat_...`):

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

### ShopifyQL over the Admin GraphQL API — current response shape

The `shopifyqlQuery` field's shape is **not** what older examples show. Getting it wrong makes the
whole GraphQL document invalid, so the query is rejected before executing — which reads like a
permissions or plan problem and is not one.

```graphql
query RunShopifyQL($q: String!) {
  shopifyqlQuery(query: $q) {
    parseErrors                       # scalar (JSON), NOT [{ code message }]
    tableData {
      rows                            # JSON, NOT `unformattedData`
      columns { name dataType }
    }
  }
}
```

`tableData.rows` comes back **already keyed by column name** — `{"day": "2026-08-07", "orders": "57"}` —
so there is no need to zip against `columns`. Numeric values arrive as strings; cast them.

Verified working on the live store 2026-08-08 with `read_analytics` + `read_reports`. Shopify Basic
plan is sufficient. If ShopifyQL appears to fail, check the query shape **before** suspecting scopes.

### Shopify CLI

Not relevant to this agent. `shopify app config link` and friends manage a Shopify **app** project
(`shopify.app.toml`, extensions, embedded UI). The analytics agent is a headless script that
authenticates with an Admin API token — the CLI plays no part in it and cannot run unattended in
GitHub Actions. It would only matter if the SNP 500 widget is later built as a real app or theme
extension.

### MCP vs. scheduled agent

The session-bound Shopify MCP tools (`run-analytics-query`, etc.) work for interactive use only — they cannot be used in scheduled GitHub Actions. The analytics agent uses direct HTTP calls to the Shopify Admin GraphQL API with the `SHOPIFY_ACCESS_TOKEN` header.
