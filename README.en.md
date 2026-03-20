**[Polski](README.md)** | **[English](README.en.md)**

# olx-agentic-cli

> **Built for AI agents.** Give this repo to Claude Code, OpenClaw, or any LLM agent — it handles OLX setup, deployment, and daily operations autonomously. The human only needs to click "Authorize" once.

A Python CLI tool and AI agent skill for the [OLX Partner API v2.0](https://developer.olx.pl/api/doc). 30 commands covering every API endpoint. Designed for agentic deployment — the agent deploys the OAuth callback, configures credentials, and manages your OLX.pl marketplace autonomously after a one-time browser authorization.

## Why This Exists

Managing OLX listings manually is slow. This tool lets an AI agent handle it — post ads, reply to messages, promote listings, check payments — all from the terminal with structured JSON output that agents parse natively.

**What the agent can do autonomously (after one-time setup):**
- List, create, update, delete, activate, deactivate adverts
- Read and reply to message threads
- Look up categories, attributes, locations
- Apply paid promotions
- Check account balance and payment history
- Manage delivery and shipments

**What requires a human (one-time only):**
- Create a free Cloudflare account (2 min)
- Register at developer.olx.pl (5 min + approval wait)
- Click "Authorize" in the browser once

## Features

- **Agent-first design** — structured JSON output, CLI interface, SKILL.md for agent integration
- **Automated deployment** — `deploy.sh` deploys the OAuth callback via Cloudflare API (just curl, no npm)
- **OAuth 2.0** with automatic token refresh — authorize once, never think about it again
- **Full API coverage** — 30 commands across 7 endpoint groups
- **Cross-platform** — works with Claude Code, OpenClaw, or any tool-using LLM
- Adverts: list, get, create, update, delete, activate, deactivate
- Messages: threads, read, reply, mark-read, favourite
- Categories + attributes, locations (regions/cities/districts)
- Payments: paid features, promotion packets, history
- Delivery: methods, shipment info, create shipments

## Setup Guide

There are **5 steps** to get this working. Steps marked with **[USER]** require the user to do something in a browser. Steps marked with **[AGENT]** can be done by an AI agent or script.

> **Why these steps?** OLX requires a real HTTPS callback URL for OAuth (no localhost). A free Cloudflare Worker provides this — the agent can deploy it automatically if you provide an API token.

### Overview

```
Step 1  [USER]   Create a free Cloudflare account + API token
Step 2  [AGENT]  Deploy the callback page (one command)
Step 3  [USER]   Register as an OLX Partner at developer.olx.pl
Step 4  [AGENT]  Clone repo, install, configure CLI
Step 5  [USER]   Run `olx login` and authorize in browser
```

After Step 5, the agent can use all 30 CLI commands autonomously.

---

### Step 1: Create a Cloudflare Account + API Token

**Who:** User (one-time, 3 minutes)
**Skip if:** You already have a Cloudflare account with a Workers API token

1. Go to [dash.cloudflare.com/sign-up](https://dash.cloudflare.com/sign-up) — create a free account (no credit card)
2. Go to **My Profile > API Tokens** ([direct link](https://dash.cloudflare.com/profile/api-tokens))
3. Click **Create Token**
4. Use the **"Edit Cloudflare Workers"** template
5. Click **Continue to summary > Create Token**
6. **Copy the token** and your **Account ID** (visible on the right sidebar of any domain page, or at the top of the Workers dashboard)

Give these two values to the agent:
- **API Token** (starts with `cfat_...` or similar)
- **Account ID** (32-character hex string)

> **No Cloudflare?** See [Alternative Hosting Options](#alternative-hosting-options) at the bottom.

---

### Step 2: Deploy the Callback Page

**Who:** Agent (or user in terminal)
**Time:** 10 seconds
**Requires:** API token and Account ID from Step 1

```bash
cd callback
./deploy.sh <API_TOKEN> <ACCOUNT_ID>
```

That's it. The script:
1. Verifies the token
2. Deploys the callback Worker via Cloudflare API (no wrangler/npm needed)
3. Prints the callback URL (e.g. `https://olx-oauth-callback.yourname.workers.dev`)

Save this URL — it's needed for Step 3 and Step 4.

**Verify:** Open the URL in a browser — you should see a dark page saying "OLX OAuth Callback".

---

### Step 3: Register as an OLX Partner + Create Application

**Who:** User (one-time, 5 minutes + approval wait)

1. Go to [developer.olx.pl](https://developer.olx.pl) and register:

| Field (Polish) | What to enter |
|----------------|---------------|
| Nazwa firmy | Your company name |
| Cel tworzenia integracji | e.g. "Zarzadzanie ogloszeniami przez CLI" |
| Glowna kategoria dzialalnosci | Your main business category |
| Adres strony WWW firmy | Your website URL |
| NIP | Your Polish tax ID |
| Wlasciciel aplikacji | Your full name |
| Email do kontaktow biznesowych | Your business email |
| Email do kontaktow technicznych | Your technical email |
| Numer telefonu | Your phone with country code (+48...) |

2. Accept Terms of Service and Privacy Policy, submit, wait for approval

3. After approval, go to **"Dodaj aplikacje"** (Add application):

| Field | What to enter |
|-------|---------------|
| Nazwa aplikacji | Any name (e.g. "OLX CLI") |
| Adres strony WWW firmy | Your website URL |
| **URI wywolania zwrotnego** | **Your callback URL from Step 2** |
| Application description | e.g. "CLI tool for managing OLX listings" |

4. Save your **Client ID** and **Client Secret**

---

### Step 4: Install and Configure

**Who:** Agent (or user in terminal)
**Time:** 1 minute

```bash
git clone https://github.com/sonusflow/olx-agentic-cli.git
cd olx-agentic-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python cli.py setup
# Client ID:    <from Step 3>
# Client Secret: <from Step 3>
# Redirect URI:  <callback URL from Step 2>
```

---

### Step 5: Authenticate

**Who:** User (requires browser, one-time)
**Time:** 1 minute

```bash
python cli.py login
```

1. Browser opens to OLX authorization page
2. Authorize the app
3. Redirected to callback page — click **"Copy URL to Clipboard"**
4. Paste into terminal, press Enter

```
Login successful! Tokens saved.
```

**Verify:**
```bash
python cli.py status
# Authenticated: yes
# Token expires: <~24 hours from now>
```

---

### Done!

Tokens auto-refresh when they expire. The agent can now use all 30 commands without browser interaction.

---

### System Requirements

- Python 3.10+
- curl (for callback deploy script — no Node.js or npm needed)


## All Commands

### Auth
```
olx setup                                Configure credentials + redirect URI
olx login                                OAuth browser flow
olx logout                               Clear stored tokens
olx status                               Auth status & token expiry
```

### Adverts
```
olx adverts list [--offset N --limit N]  List your adverts
olx adverts get <id>                     Get advert details
olx adverts create --file ad.json        Create advert from JSON
olx adverts update <id> --file ad.json   Update advert from JSON
olx adverts delete <id>                  Delete advert (with confirmation)
olx adverts activate <id>               Activate a draft/deactivated advert
olx adverts deactivate <id>             Deactivate an active advert
```

### Messages
```
olx messages list [--offset N --limit N] List message threads
olx messages get <thread_id>             Read messages in a thread
olx messages thread <thread_id>          Get thread metadata
olx messages send <thread_id> "text"     Reply to a thread
olx messages mark-read <thread_id>       Mark thread as read
olx messages favourite <thread_id>       Add to favourites
olx messages favourite <id> --remove     Remove from favourites
```

### Categories
```
olx categories list [--parent N]         List categories
olx categories get <id>                  Get category details
olx categories attributes <id>          Required fields for a category
```

### User
```
olx user me                              Your profile
olx user get <id>                        Public user profile
olx user balance                         Account balance
```

### Locations
```
olx locations regions                    All 16 voivodeships
olx locations cities [--region N]        List cities
olx locations get-city <id>              City details
olx locations districts <city_id>        Districts of a city
```

### Payments & Promotions
```
olx payments features <advert_id>        Paid features for an advert
olx payments apply-feature <id> <type>   Apply promote/urgent/top_ad
olx payments packets                     Available promotion packets
olx payments history [--offset --limit]  Payment history
```

### Delivery
```
olx delivery methods                     Available delivery methods
olx delivery get-shipment <advert_id>    Shipment info for advert
olx delivery create-shipment <id> --file Create shipment from JSON
```

## Examples

### Create a new listing

```bash
# 1. Find the right category
python cli.py categories list --parent 0
python cli.py categories list --parent 99
python cli.py categories attributes 165

# 2. Find your location
python cli.py locations regions
python cli.py locations cities --region 2
python cli.py locations districts 17871
```

Create `ad.json`:

```json
{
  "title": "iPhone 14 Pro 256GB",
  "description": "Like new, includes box and charger. Battery health 96%.",
  "category_id": 165,
  "contact": { "name": "Jan", "phone": "+48500000000" },
  "location": { "city_id": 10609, "district_id": null },
  "images": [
    {"url": "https://example.com/photo1.jpg"},
    {"url": "https://example.com/photo2.jpg"}
  ],
  "price": { "value": 4200, "currency": "PLN", "negotiable": true },
  "attributes": {}
}
```

```bash
python cli.py adverts create --file ad.json
```

### Update a listing

```bash
# update.json: { "price": { "value": 3900, "currency": "PLN", "negotiable": true } }
python cli.py adverts update 12345 --file update.json
```

### Manage messages

```bash
python cli.py messages list --limit 5
python cli.py messages get 12345
python cli.py messages send 12345 "Still available! Can meet tomorrow."
python cli.py messages mark-read 12345
```

### Promote a listing

```bash
python cli.py payments features 12345
python cli.py payments apply-feature 12345 promote
```

## How the OAuth Flow Works

```
CLI runs "olx login"
       │
       ▼
Browser opens OLX auth page
       │
       ▼ (user authorizes)
OLX redirects to your Cloudflare Worker URL
  ?code=XXXXX&state=YYYYY
       │
       ▼
Callback page shows "Copy URL to Clipboard"
       │
       ▼ (user pastes into terminal)
CLI validates state (CSRF protection)
       │
       ▼
CLI exchanges code for tokens via OLX API
       │
       ▼
Tokens saved to ~/.olx-integration/tokens.json
(chmod 600, auto-refresh on expiry)
```

- The callback page is **purely static** — no data is stored, logged, or transmitted
- Authorization codes are **single-use** and expire in seconds
- Access tokens expire in ~24h and auto-refresh via refresh token

## Monitoring Messages

The OLX API does not support webhooks or push notifications. To monitor incoming messages, set up a cron job that polls for unread messages:

```bash
# Check every 5 minutes for new messages
*/5 * * * * cd /path/to/olx-agentic-cli && .venv/bin/python cli.py messages list 2>/dev/null | grep -q '"unread_count": [1-9]' && notify-send "OLX" "New message received" || true
```

Adapt the notification command to your setup (desktop notification, Slack webhook, email, etc).

## Alternative Hosting Options

If you can't use Cloudflare, you can host the callback page anywhere that serves static HTML over HTTPS:

### GitHub Pages (free)
1. Fork this repository
2. Go to **Settings > Pages** in your fork
3. Set source: branch `main`, folder `/callback/github-pages`
4. Your URL: `https://<username>.github.io/olx-agentic-cli/callback/github-pages/`

### Any static host
Upload `callback/index.html` to Vercel, Netlify, Render, S3+CloudFront, or any HTTPS-capable host. Use the resulting URL as your callback URI.

## Project Structure

```
cli.py            CLI entry point (Click) — 30 commands
config.py         Config management (~/.olx-integration/)
olx_api/          API client modules
  auth.py           OAuth 2.0 (authorization code + token refresh)
  client.py         Base HTTP client (httpx) with typed errors
  adverts.py        Adverts CRUD + activate/deactivate
  messages.py       Threads, messages, mark-read, favourites
  categories.py     Category tree + attributes
  users.py          User profile + balance
  locations.py      Regions, cities, districts
  payments.py       Paid features, packets, payment history
  delivery.py       Delivery methods + shipments
callback/         OAuth callback page (Cloudflare Worker / GitHub Pages / any host)
tests/            Test suite (pytest)
references/       API quick reference
SKILL.md          AI agent skill definition
```

## Testing

```bash
pip install pytest
pytest tests/ -v
```

## Security

- Credentials: `~/.olx-integration/config.json` (chmod 600)
- Tokens: `~/.olx-integration/tokens.json` (chmod 600)
- Config directory: chmod 700
- OAuth state validated (CSRF protection)
- No secrets in source code
- Callback page: static HTML, no server-side processing, no logging

## License

MIT — see [LICENSE](LICENSE).

## Author

**sonusflow** — [github.com/sonusflow](https://github.com/sonusflow)
