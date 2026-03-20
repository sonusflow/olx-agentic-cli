# OLX Partner API v2.0 — Quick Reference

## Base URL

```
https://www.olx.pl/api/partner
```

## Authentication

- **Type:** OAuth 2.0 (authorization_code grant)
- **Authorization URL:** `https://www.olx.pl/oauth/authorize/`
- **Token URL:** `https://www.olx.pl/api/open/oauth/token`
- **Scopes:** `v2 read write`
- **Required header:** `Version: 2.0`
- **Required header:** `User-Agent: OLX-CLI/1.0.0` (CloudFront blocks default httpx UA)

## Endpoints

### Adverts

| Method | Path | Description |
|--------|------|-------------|
| GET | `/adverts` | List user's adverts |
| GET | `/adverts/{id}` | Get advert details |
| POST | `/adverts` | Create advert |
| PUT | `/adverts/{id}` | Update advert |
| DELETE | `/adverts/{id}` | Delete advert |
| POST | `/adverts/{id}/commands` | Activate / deactivate |

### Messages

| Method | Path | Description |
|--------|------|-------------|
| GET | `/threads` | List threads |
| GET | `/threads/{id}` | Get thread metadata |
| GET | `/threads/{id}/messages` | List messages |
| POST | `/threads/{id}/messages` | Send message |
| POST | `/threads/{id}/commands` | Mark read / favourite |

### Categories

| Method | Path | Description |
|--------|------|-------------|
| GET | `/categories` | List categories |
| GET | `/categories/{id}` | Get category |
| GET | `/categories/{id}/attributes` | Category attributes |

### Users

| Method | Path | Description |
|--------|------|-------------|
| GET | `/users/me` | Current user |
| GET | `/users/{id}` | Public user info |
| GET | `/users/me/account-balance` | Account balance |

### Locations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/regions` | List regions |
| GET | `/cities` | List cities |
| GET | `/cities/{id}` | City details |
| GET | `/cities/{id}/districts` | City districts |

### Payments

| Method | Path | Description |
|--------|------|-------------|
| GET | `/adverts/{id}/paid-features` | Available features |
| POST | `/adverts/{id}/paid-features` | Apply feature |
| GET | `/packets` | List packets |
| GET | `/payments` | Payment history |

### Delivery

| Method | Path | Description |
|--------|------|-------------|
| GET | `/delivery/methods` | Delivery methods |
| GET | `/adverts/{id}/shipment` | Shipment info |
| POST | `/adverts/{id}/shipment` | Create shipment |

## Common Parameters

- `offset` — Pagination offset (default: 0)
- `limit` — Results per page (default varies, max 50)
- `sort_by` — Sort expression (e.g. `created_at:desc`)

## Error Responses

```json
{
  "error": {
    "code": 400,
    "message": "Validation failed",
    "details": [...]
  }
}
```

## Rate Limits

The API enforces per-client rate limits. On HTTP 429, back off and retry after the `Retry-After` header value.

## Important Notes

- The API is for **managing your own account only** — there is no search endpoint
- CloudFront (AWS) blocks requests with default library User-Agents; always set a custom one
- OAuth authorization codes are single-use and expire within seconds
- Access tokens expire after ~24 hours; use the refresh token to get new ones
