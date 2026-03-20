"""OAuth 2.0 authentication for the OLX Partner API."""

from __future__ import annotations

import json
import secrets
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

import httpx

from config import CONFIG_DIR, DEFAULT_REDIRECT_URI, load_config, load_tokens, save_tokens


# OLX OAuth endpoints (outside /api/partner)
AUTHORIZE_URL = "https://www.olx.pl/oauth/authorize/"
TOKEN_URL = "https://www.olx.pl/api/open/oauth/token"
OAUTH_SCOPE = "v2 read write"
OAUTH_SCOPE_URL = "v2+read+write"  # URL-encoded form for authorize URL
_TOKEN_HEADERS = {"User-Agent": "OLX-CLI/1.0.0"}


class AuthError(Exception):
    """Raised when authentication fails."""
    pass


class _CallbackHandler(BaseHTTPRequestHandler):
    """Tiny HTTP handler that captures the OAuth callback."""

    authorization_code: Optional[str] = None
    received_state: Optional[str] = None
    error: Optional[str] = None

    def do_GET(self) -> None:  # noqa: N802
        qs = parse_qs(urlparse(self.path).query)
        if "error" in qs:
            _CallbackHandler.error = qs["error"][0]
        else:
            _CallbackHandler.authorization_code = qs.get("code", [None])[0]
            _CallbackHandler.received_state = qs.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        body = (
            "<html><body><h2>Authorization complete!</h2>"
            "<p>You can close this tab and return to the terminal.</p>"
            "</body></html>"
        )
        self.wfile.write(body.encode())

    def log_message(self, fmt: str, *args: Any) -> None:
        """Suppress default stderr logging."""
        pass


class TokenManager:
    """Manages OAuth tokens: loading, refreshing, and persisting."""

    def __init__(self) -> None:
        self._config = load_config()
        self._tokens = load_tokens()

    @property
    def client_id(self) -> str:
        cid = self._config.get("client_id", "")
        if not cid:
            raise AuthError("client_id not configured. Run `olx setup` first.")
        return cid

    @property
    def client_secret(self) -> str:
        cs = self._config.get("client_secret", "")
        if not cs:
            raise AuthError("client_secret not configured. Run `olx setup` first.")
        return cs

    @property
    def access_token(self) -> Optional[str]:
        return self._tokens.get("access_token")

    @property
    def refresh_token(self) -> Optional[str]:
        return self._tokens.get("refresh_token")

    @property
    def expires_at(self) -> float:
        return self._tokens.get("expires_at", 0.0)

    @property
    def is_expired(self) -> bool:
        return time.time() >= self.expires_at - 60  # 60 s safety margin

    @property
    def is_authenticated(self) -> bool:
        return bool(self.access_token)

    # ------------------------------------------------------------------
    # Token persistence
    # ------------------------------------------------------------------

    def _persist(self, data: dict[str, Any]) -> None:
        self._tokens = data
        save_tokens(data)

    # ------------------------------------------------------------------
    # OAuth flows
    # ------------------------------------------------------------------

    @property
    def redirect_uri(self) -> str:
        """Return the configured redirect URI, defaulting to production."""
        return self._config.get("redirect_uri", DEFAULT_REDIRECT_URI)

    def authorize_interactive(self, local: bool = False) -> None:
        """Run the authorization_code flow.

        Args:
            local: If True, use a local callback server (dev mode).
                   If False (default), use the registered redirect URI
                   and prompt the user to paste the callback URL.
        """
        if local:
            self._authorize_local()
        else:
            self._authorize_redirect()

    def _authorize_redirect(self) -> None:
        """Production flow: use registered redirect URI, user pastes code."""
        state = secrets.token_urlsafe(32)
        redirect_uri = self.redirect_uri

        url = (
            f"{AUTHORIZE_URL}?client_id={self.client_id}"
            f"&response_type=code&state={state}"
            f"&scope={OAUTH_SCOPE_URL}"
            f"&redirect_uri={redirect_uri}"
        )

        print(f"\nOpening browser for OLX authorization...\n{url}\n")
        webbrowser.open(url)

        print("After authorizing, you will be redirected to:")
        print(f"  {redirect_uri}")
        print("\nPaste the full callback URL from your browser's address bar:")
        raw = input("> ").strip()

        # Parse the callback URL to extract code and validate state
        if raw.startswith("http"):
            qs = parse_qs(urlparse(raw).query)
            if "error" in qs:
                raise AuthError(f"OAuth error: {qs['error'][0]}")
            code = qs.get("code", [None])[0]
            received_state = qs.get("state", [None])[0]
            if not code:
                raise AuthError("No authorization code found in the URL.")
            if not received_state:
                raise AuthError("No state parameter in callback URL — cannot verify authenticity.")
            if received_state != state:
                raise AuthError("OAuth state mismatch — possible CSRF attack.")
        else:
            raise AuthError(
                "Expected a full callback URL (starting with http) for state validation. "
                "Please paste the complete URL from your browser's address bar."
            )

        if not code:
            raise AuthError("No authorization code provided.")
        self._exchange_code(code, redirect_uri)

    def _authorize_local(self) -> None:
        """Dev flow: local callback server on localhost."""
        state = secrets.token_urlsafe(32)

        server = HTTPServer(("127.0.0.1", 0), _CallbackHandler)
        port = server.server_address[1]
        redirect_uri = f"http://localhost:{port}/callback"

        url = (
            f"{AUTHORIZE_URL}?client_id={self.client_id}"
            f"&response_type=code&state={state}"
            f"&scope={OAUTH_SCOPE_URL}"
            f"&redirect_uri={redirect_uri}"
        )

        _CallbackHandler.authorization_code = None
        _CallbackHandler.received_state = None
        _CallbackHandler.error = None

        print(f"\nOpening browser for OLX authorization...\n{url}\n")
        webbrowser.open(url)

        thread = Thread(target=server.handle_request)
        thread.start()
        thread.join(timeout=120)
        server.server_close()

        if _CallbackHandler.error:
            raise AuthError(f"OAuth error: {_CallbackHandler.error}")
        if not _CallbackHandler.authorization_code:
            raise AuthError("No authorization code received (timeout?).")
        if _CallbackHandler.received_state != state:
            raise AuthError("OAuth state mismatch — possible CSRF attack.")

        self._exchange_code(_CallbackHandler.authorization_code, redirect_uri)

    def _exchange_code(self, code: str, redirect_uri: str) -> None:
        """Exchange an authorization code for access + refresh tokens."""
        resp = httpx.post(
            TOKEN_URL,
            headers=_TOKEN_HEADERS,
            data={
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri,
                "scope": OAUTH_SCOPE,
            },
        )
        if not resp.is_success:
            raise AuthError(f"Token exchange failed ({resp.status_code}): {resp.text}")
        self._store_token_response(resp.json())

    def refresh(self) -> None:
        """Use the refresh_token to obtain a new access_token."""
        if not self.refresh_token:
            raise AuthError("No refresh token available. Run `olx login`.")

        resp = httpx.post(
            TOKEN_URL,
            headers=_TOKEN_HEADERS,
            data={
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "refresh_token": self.refresh_token,
            },
        )
        if not resp.is_success:
            raise AuthError(f"Token refresh failed ({resp.status_code}): {resp.text}")
        self._store_token_response(resp.json())

    def _store_token_response(self, data: dict[str, Any]) -> None:
        expires_in = data.get("expires_in", 3600)
        self._persist({
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", self.refresh_token),
            "expires_at": time.time() + int(expires_in),
        })

    def get_valid_token(self) -> str:
        """Return a valid access token, refreshing if necessary."""
        if not self.is_authenticated:
            raise AuthError("Not logged in. Run `olx login` first.")
        if self.is_expired:
            self.refresh()
        return self.access_token  # type: ignore[return-value]

    def logout(self) -> None:
        """Clear stored tokens."""
        self._persist({})
