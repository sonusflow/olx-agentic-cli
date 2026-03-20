#!/usr/bin/env bash
# deploy.sh — Deploy the OLX OAuth callback page to Cloudflare Workers.
#
# Uses the Cloudflare API directly — no wrangler or Node.js needed. Just curl.
#
# Usage:
#   ./deploy.sh <CLOUDFLARE_API_TOKEN> <CLOUDFLARE_ACCOUNT_ID> [WORKER_NAME]
#
# Example:
#   ./deploy.sh cfat_abc123... 9d81c7f8... olx-callback
#
# Creates a Worker at: https://<WORKER_NAME>.<subdomain>.workers.dev

set -euo pipefail

API_TOKEN="${1:-}"
ACCOUNT_ID="${2:-}"
WORKER_NAME="${3:-olx-oauth-callback}"

if [ -z "$API_TOKEN" ] || [ -z "$ACCOUNT_ID" ]; then
    echo "Usage: ./deploy.sh <CLOUDFLARE_API_TOKEN> <CLOUDFLARE_ACCOUNT_ID> [WORKER_NAME]"
    echo ""
    echo "To get these values:"
    echo "  1. Account ID: dash.cloudflare.com > Workers & Pages > right sidebar"
    echo "  2. API Token:  dash.cloudflare.com > My Profile > API Tokens > Create Token"
    echo "     Use the 'Edit Cloudflare Workers' template"
    exit 1
fi

# --- Verify token ---
echo "Verifying API token..."
VERIFY=$(curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
    -H "Authorization: Bearer $API_TOKEN")

if ! echo "$VERIFY" | grep -q '"success":true'; then
    echo "Error: Invalid API token."
    echo "$VERIFY"
    exit 1
fi
echo "Token valid."

# --- Write worker script to temp file ---
TMPFILE=$(mktemp)
cat > "$TMPFILE" << 'JSEOF'
const HTML = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OLX Authorization — Callback</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box}
        body{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Roboto,sans-serif;background:#0a0a0a;color:#e0e0e0;min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px}
        .card{background:#1a1a1a;border:1px solid #333;border-radius:12px;padding:40px;max-width:560px;width:100%;text-align:center}
        .icon{font-size:48px;margin-bottom:16px}h1{font-size:22px;font-weight:600;margin-bottom:8px}
        .subtitle{color:#888;font-size:14px;margin-bottom:32px}
        .copy-btn{background:#4ade80;color:#000;border:none;border-radius:8px;padding:12px 24px;font-size:15px;font-weight:600;cursor:pointer;margin-top:16px;transition:background .15s}
        .copy-btn:hover{background:#22c55e}.copy-btn.copied{background:#666;color:#fff}
        .instruction{color:#888;font-size:13px;margin-top:24px;line-height:1.6}
        .error-box{background:#1c0a0a;border:1px solid #7f1d1d;border-radius:8px;padding:16px;margin:24px 0}
        .error-value{color:#f87171;font-weight:500}
        .url-box{background:#111;border:1px solid #333;border-radius:8px;padding:16px;margin:24px 0}
        .url-label{font-size:12px;color:#888;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
        .url-value{font-family:SF Mono,Fira Code,Consolas,monospace;font-size:11px;color:#94a3b8;word-break:break-all;line-height:1.5;user-select:all}
    </style>
</head>
<body>
    <div class="card" id="card"><noscript><p>JavaScript required. Copy the URL from your address bar.</p></noscript></div>
    <script>
        var p=new URLSearchParams(window.location.search),code=p.get("code"),error=p.get("error"),c=document.getElementById("card");
        function e(s){var d=document.createElement("div");d.textContent=s;return d.innerHTML}
        if(error)c.innerHTML="<div class=icon>&#10060;</div><h1>Authorization Failed</h1><div class=error-box><div class=error-value>"+e(error)+"</div></div><p class=instruction>Close this tab and try <code>olx login</code> again.</p>";
        else if(code)c.innerHTML="<div class=icon>&#9989;</div><h1>Authorization Complete</h1><p class=subtitle>Copy the URL below and paste it into your terminal</p><div class=url-box><div class=url-label>Callback URL</div><div class=url-value>"+e(window.location.href)+"</div></div><button class=copy-btn id=cb onclick=copyUrl()>Copy URL to Clipboard</button><p class=instruction>Paste into terminal where <code>olx login</code> is waiting, then Enter.</p>";
        else c.innerHTML="<div class=icon>&#10067;</div><h1>OLX OAuth Callback</h1><p class=subtitle>OAuth callback for the OLX CLI tool.</p><p class=instruction>Run <code>olx login</code> to start.</p>";
        function copyUrl(){navigator.clipboard.writeText(window.location.href).then(function(){var b=document.getElementById("cb");b.textContent="Copied!";b.classList.add("copied");setTimeout(function(){b.textContent="Copy URL to Clipboard";b.classList.remove("copied")},2e3)})}
    </script>
</body>
</html>`;

addEventListener("fetch", event => {
    event.respondWith(new Response(HTML, {
        headers: {"Content-Type": "text/html;charset=UTF-8", "Cache-Control": "no-store"}
    }));
});
JSEOF

# --- Deploy ---
echo "Deploying Worker '$WORKER_NAME'..."

RESULT=$(curl -s -X PUT \
    "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/$WORKER_NAME" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/javascript" \
    --data-binary @"$TMPFILE")

rm -f "$TMPFILE"

if echo "$RESULT" | grep -q '"success":true'; then
    # Enable workers.dev subdomain route
    curl -s -X POST \
        "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/scripts/$WORKER_NAME/subdomain" \
        -H "Authorization: Bearer $API_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"enabled": true}' > /dev/null 2>&1

    # Get the workers.dev subdomain
    SUBDOMAIN=$(curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCOUNT_ID/workers/subdomain" \
        -H "Authorization: Bearer $API_TOKEN" | grep -o '"subdomain":"[^"]*"' | cut -d'"' -f4)

    WORKER_URL="https://$WORKER_NAME.$SUBDOMAIN.workers.dev"

    echo ""
    echo "=========================================="
    echo "  Callback page deployed!"
    echo ""
    echo "  URL: $WORKER_URL"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "  1. Use this URL as 'URI wywolania zwrotnego' at developer.olx.pl"
    echo "  2. Use this URL as 'Redirect URI' when running: python cli.py setup"
else
    echo "Deploy failed:"
    echo "$RESULT"
    exit 1
fi
