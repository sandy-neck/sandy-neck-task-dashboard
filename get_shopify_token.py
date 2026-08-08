"""
One-time helper to exchange a Shopify Developer Dashboard app's
Client ID + Secret for a permanent store access token.

Usage:
    python get_shopify_token.py
"""
import sys
import json
import webbrowser
import urllib.parse
import urllib.request

SHOP = "sandy-neck-provisions-8044.myshopify.com"
SCOPES = "read_analytics,read_customers,read_inventory,read_orders,read_products,read_reports"
REDIRECT_URI = "https://example.com"

def main():
    print("\nShopify Token Generator")
    print("=" * 40)
    client_id = input("Paste your Client ID: ").strip()
    client_secret = input("Paste your Client Secret: ").strip()

    auth_url = (
        f"https://{SHOP}/admin/oauth/authorize"
        f"?client_id={client_id}"
        f"&scope={SCOPES}"
        f"&redirect_uri={REDIRECT_URI}"
    )

    print(f"\nOpening browser to authorize the app...")
    print(f"(If the browser doesn't open, paste this URL manually:)")
    print(f"\n  {auth_url}\n")
    webbrowser.open(auth_url)

    print("After you click Install, your browser will redirect to example.com.")
    print("The page won't load properly — that's fine.")
    print("Copy the ENTIRE URL from your browser's address bar and paste it here.\n")

    redirect = input("Paste the full redirect URL: ").strip()

    parsed = urllib.parse.urlparse(redirect)
    params = urllib.parse.parse_qs(parsed.query)

    if "code" not in params:
        print("\nERROR: No 'code' found in that URL.")
        print("Make sure you copied the full URL including everything after the '?'")
        sys.exit(1)

    code = params["code"][0]
    print(f"\nGot authorization code. Exchanging for access token...")

    payload = json.dumps({
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
    }).encode()

    req = urllib.request.Request(
        f"https://{SHOP}/admin/oauth/access_token",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"\nERROR: Shopify returned {e.code}: {body}")
        sys.exit(1)

    token = result.get("access_token")
    if not token:
        print(f"\nERROR: No access_token in response: {result}")
        sys.exit(1)

    print("\n" + "=" * 40)
    print("SUCCESS! Your permanent access token:")
    print()
    print(f"  {token}")
    print()
    print("Add this to GitHub Secrets as:  SHOPIFY_ACCESS_TOKEN")
    print("You only need to do this once — the token doesn't expire.")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
