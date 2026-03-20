"""Base HTTP client for OLX Partner API v2.0."""

from __future__ import annotations

import time
from typing import Any, Optional

import httpx

from olx_api.auth import TokenManager


class OLXAPIError(Exception):
    """Base exception for OLX API errors."""

    def __init__(self, status_code: int, detail: str, response: Optional[httpx.Response] = None):
        self.status_code = status_code
        self.detail = detail
        self.response = response
        super().__init__(f"HTTP {status_code}: {detail}")


class OLXAuthError(OLXAPIError):
    """Authentication / authorization error (401/403)."""
    pass


class OLXNotFoundError(OLXAPIError):
    """Resource not found (404)."""
    pass


class OLXRateLimitError(OLXAPIError):
    """Rate limit exceeded (429)."""
    pass


class OLXClient:
    """Synchronous HTTP client for the OLX Partner API.

    Handles authentication headers, API versioning, automatic token
    refresh, and structured error handling.
    """

    BASE_URL = "https://www.olx.pl/api/partner"

    def __init__(self, token_manager: TokenManager, timeout: float = 30.0):
        self._tm = token_manager
        self._http = httpx.Client(
            base_url=self.BASE_URL,
            timeout=timeout,
            headers={
                "Version": "2.0",
                "Accept": "application/json",
                "User-Agent": "OLX-CLI/1.0.0",
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _auth_headers(self) -> dict[str, str]:
        """Return Authorization header, refreshing the token if needed."""
        token = self._tm.get_valid_token()
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def _raise_for_status(resp: httpx.Response) -> None:
        """Raise a typed OLX error for non-2xx responses."""
        if resp.is_success:
            return

        try:
            body = resp.json()
            detail = body.get("error", {}).get("message", resp.text)
        except Exception:
            detail = resp.text

        code = resp.status_code
        if code in (401, 403):
            raise OLXAuthError(code, detail, resp)
        if code == 404:
            raise OLXNotFoundError(code, detail, resp)
        if code == 429:
            raise OLXRateLimitError(code, detail, resp)
        raise OLXAPIError(code, detail, resp)

    # ------------------------------------------------------------------
    # Public HTTP verbs
    # ------------------------------------------------------------------

    def get(self, path: str, params: Optional[dict[str, Any]] = None) -> Any:
        """Send a GET request and return parsed JSON."""
        resp = self._http.get(path, params=params, headers=self._auth_headers())
        self._raise_for_status(resp)
        return resp.json()

    def post(self, path: str, json: Optional[dict[str, Any]] = None) -> Any:
        """Send a POST request and return parsed JSON."""
        resp = self._http.post(path, json=json, headers=self._auth_headers())
        self._raise_for_status(resp)
        if resp.status_code == 204:
            return None
        return resp.json()

    def put(self, path: str, json: Optional[dict[str, Any]] = None) -> Any:
        """Send a PUT request and return parsed JSON."""
        resp = self._http.put(path, json=json, headers=self._auth_headers())
        self._raise_for_status(resp)
        if resp.status_code == 204:
            return None
        return resp.json()

    def delete(self, path: str) -> None:
        """Send a DELETE request."""
        resp = self._http.delete(path, headers=self._auth_headers())
        self._raise_for_status(resp)

    def close(self) -> None:
        """Close the underlying HTTP transport."""
        self._http.close()

    def __enter__(self) -> "OLXClient":
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
