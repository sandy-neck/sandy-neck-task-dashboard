$clientId     = Read-Host "Paste your Client ID"
$clientSecret = Read-Host "Paste your Client Secret"

$authUrl = "https://sandy-neck-provisions-8044.myshopify.com/admin/oauth/authorize" +
           "?client_id=$clientId" +
           "&scope=read_analytics,read_customers,read_inventory,read_orders,read_products,read_reports" +
           "&redirect_uri=https://example.com"

Write-Host "`nOpening browser — click Install if prompted..." -ForegroundColor Cyan
Start-Process $authUrl

Write-Host "`nAfter the browser redirects to example.com, copy the FULL URL from the address bar."
$redirectUrl = Read-Host "Paste the full redirect URL here"

# Parse code from the redirect URL
$code = ($redirectUrl -split "code=")[1] -split "&" | Select-Object -First 1

if (-not $code) {
    Write-Host "ERROR: Could not find 'code=' in that URL. Make sure you copied the full address bar URL." -ForegroundColor Red
    exit 1
}

Write-Host "`nExchanging code for access token..." -ForegroundColor Cyan

$body = "{`"client_id`":`"$clientId`",`"client_secret`":`"$clientSecret`",`"code`":`"$code`"}"

try {
    $result = Invoke-RestMethod `
        -Method Post `
        -Uri "https://sandy-neck-provisions-8044.myshopify.com/admin/oauth/access_token" `
        -ContentType "application/json" `
        -Body $body

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "SUCCESS! Your permanent access token:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  $($result.access_token)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Add this to GitHub Secrets as: SHOPIFY_ACCESS_TOKEN" -ForegroundColor Green
    Write-Host "The token does not expire — you only need to do this once." -ForegroundColor Green
    Write-Host "========================================`n" -ForegroundColor Green
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "The authorization code may have expired. Run this script again to get a fresh one." -ForegroundColor Red
}
