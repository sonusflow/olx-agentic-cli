---
name: olx-integration
description: Manage OLX.pl marketplace listings — post ads, reply to messages, check stats, and manage your OLX account. Use when the user mentions OLX, classified ads on OLX, or wants to manage their OLX listings.
version: 2.0.0
metadata:
  openclaw:
    requires:
      env:
        - OLX_CLIENT_ID
        - OLX_CLIENT_SECRET
      bins:
        - python3
    primaryEnv: OLX_CLIENT_ID
    emoji: "🛒"
    homepage: https://github.com/sonusflow/olx-agentic-cli
---

# OLX Integration Skill

Manage your OLX.pl marketplace account from the command line or through an AI agent. This skill wraps the OLX Partner API v2.0 and provides 30 commands covering all API endpoints.

## Onboarding

### Prerequisites

1. A registered OLX Partner API application at <https://developer.olx.pl>
2. Python 3.10+ with `pip`
3. A callback URL for OAuth (see README.md for setup)

### Installation

```bash
git clone https://github.com/sonusflow/olx-agentic-cli.git
cd olx-agentic-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Platform-specific setup

**Claude Code:**
```bash
# Run interactive setup
python cli.py setup
# Enter: Client ID, Client Secret, Redirect URI

# Authenticate
python cli.py login
```

**OpenClaw:**
The skill expects `OLX_CLIENT_ID` and `OLX_CLIENT_SECRET` as environment variables. OpenClaw will prompt for these automatically when the skill is first invoked if `primaryEnv` (`OLX_CLIENT_ID`) is not set.

### First-time login

```bash
# Setup credentials and redirect URI
python cli.py setup

# Authenticate via OAuth browser flow
python cli.py login
# Browser opens → authorize → copy callback URL → paste into terminal

# For local development (localhost callback)
python cli.py login --local
```

## Available Commands

### Auth
| Command | Description |
|---|---|
| `olx setup` | Configure client_id, client_secret, redirect_uri |
| `olx login` | OAuth browser flow (production callback) |
| `olx login --local` | OAuth with local callback server (dev) |
| `olx logout` | Clear stored tokens |
| `olx status` | Auth status, redirect URI, token expiry |

### Adverts
| Command | Description |
|---|---|
| `olx adverts list [--offset N --limit N]` | List your adverts |
| `olx adverts get <id>` | Get advert details |
| `olx adverts create --file ad.json` | Create advert from JSON |
| `olx adverts update <id> --file ad.json` | Update advert from JSON |
| `olx adverts delete <id>` | Delete advert (with confirmation) |
| `olx adverts activate <id>` | Activate draft/deactivated advert |
| `olx adverts deactivate <id>` | Deactivate active advert |

### Messages
| Command | Description |
|---|---|
| `olx messages list [--offset N --limit N]` | List message threads |
| `olx messages get <thread_id>` | Read messages in a thread |
| `olx messages thread <thread_id>` | Get thread metadata |
| `olx messages send <thread_id> "text"` | Reply to a thread |
| `olx messages mark-read <thread_id>` | Mark thread as read |
| `olx messages favourite <thread_id>` | Add to favourites (--remove to undo) |

### Categories
| Command | Description |
|---|---|
| `olx categories list [--parent N]` | List categories |
| `olx categories get <id>` | Get category details |
| `olx categories attributes <id>` | Required fields for a category |

### User
| Command | Description |
|---|---|
| `olx user me` | Your profile |
| `olx user get <id>` | Public user profile |
| `olx user balance` | Account balance |

### Locations
| Command | Description |
|---|---|
| `olx locations regions` | All 16 voivodeships |
| `olx locations cities [--region N]` | List cities |
| `olx locations get-city <id>` | City details |
| `olx locations districts <city_id>` | Districts of a city |

### Payments
| Command | Description |
|---|---|
| `olx payments features <advert_id>` | Paid features for an advert |
| `olx payments apply-feature <id> <type>` | Apply promote/urgent/top_ad |
| `olx payments packets` | Available promotion packets |
| `olx payments history [--offset --limit]` | Payment history |

### Delivery
| Command | Description |
|---|---|
| `olx delivery methods` | Available delivery methods |
| `olx delivery get-shipment <advert_id>` | Shipment info for advert |
| `olx delivery create-shipment <id> --file` | Create shipment from JSON |

All commands output JSON for easy piping and parsing.

## Common Workflows

### List your active ads

```bash
python cli.py adverts list --limit 20
```

### Post a new ad

```bash
# 1. Find the right category
python cli.py categories list --parent 0
python cli.py categories list --parent 99
python cli.py categories attributes 165

# 2. Create ad.json (see README for full example)

# 3. Post it
python cli.py adverts create --file ad.json
```

### Update a listing

```bash
# Create update.json with only the fields to change
python cli.py adverts update 12345 --file update.json
```

### Reply to messages

```bash
python cli.py messages list
python cli.py messages get 12345
python cli.py messages send 12345 "Still available!"
python cli.py messages mark-read 12345
```

### Find a location ID

```bash
python cli.py locations regions
python cli.py locations cities --region 2
python cli.py locations districts 17871
```

### Promote a listing

```bash
python cli.py payments features 12345
python cli.py payments apply-feature 12345 promote
```

### Check account

```bash
python cli.py status
python cli.py user me
python cli.py user balance
```

## Error Handling

- **"Not logged in"** — Run `olx login` to authenticate.
- **"client_id not configured"** — Run `olx setup` to enter your API credentials.
- **HTTP 401/403** — Token expired or invalid. Auto-refresh handles most cases; if it fails, run `olx login` again.
- **HTTP 429** — Rate limited. Wait and retry.
- **HTTP 404** — Resource not found.

## Token Refresh

Tokens refresh automatically when they expire (~24h). If automatic refresh fails:

```bash
olx logout
olx login
```

Tokens are stored in `~/.olx-integration/tokens.json` with restricted permissions (chmod 600).

## Monitoring Messages

The OLX API does not support webhooks or push notifications. The only way to detect new messages is by polling. If the user wants to be notified about incoming messages, **ask if they'd like to set up a cron job** to check periodically:

```bash
# Example: check for unread messages every 5 minutes
*/5 * * * * cd /path/to/olx-agentic-cli && .venv/bin/python cli.py messages list 2>/dev/null | grep -q '"unread_count": [1-9]' && echo "New OLX message" | notify-send "OLX" || true
```

The agent should offer to configure this for the user, adapting the notification method to their environment (desktop notification, Slack webhook, email, etc).

## Agent Integration Notes

When used by an AI agent (Claude Code or OpenClaw):

1. Always check `olx status` before running commands to verify auth state.
2. Use `--limit` and `--offset` for pagination when listing resources.
3. Parse JSON output programmatically — all commands return structured JSON.
4. For creating adverts, first check `olx categories list` and `olx categories attributes` to find the correct `category_id` and required fields.
5. Use `olx locations` commands to look up `city_id` and `district_id` values.
6. Handle errors gracefully — if auth fails, guide the user through `olx login`.
7. The OLX API has **no webhooks** — if the user needs message monitoring, offer to set up a cron job that polls `olx messages list` for unread messages.
