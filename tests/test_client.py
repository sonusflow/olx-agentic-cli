"""Basic tests for OLX CLI components."""

from __future__ import annotations

import json
import os
import stat
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ------------------------------------------------------------------
# Config tests
# ------------------------------------------------------------------

class TestConfig:
    """Test config read/write and file permissions."""

    def test_save_and_load_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("config.CONFIG_FILE", tmp_path / "config.json")

        from config import save_config, load_config

        save_config({"client_id": "test_id", "client_secret": "test_secret"})
        cfg = load_config()
        assert cfg["client_id"] == "test_id"
        assert cfg["client_secret"] == "test_secret"

    def test_config_file_permissions(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("config.CONFIG_FILE", tmp_path / "config.json")

        from config import save_config

        save_config({"client_id": "x"})
        mode = os.stat(tmp_path / "config.json").st_mode
        # Owner read+write only
        assert mode & 0o777 == 0o600

    def test_load_missing_config(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_FILE", tmp_path / "nonexistent.json")

        from config import load_config

        assert load_config() == {}

    def test_save_and_load_tokens(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("config.TOKENS_FILE", tmp_path / "tokens.json")

        from config import save_tokens, load_tokens

        data = {"access_token": "tok", "refresh_token": "ref", "expires_at": 9999999999}
        save_tokens(data)
        loaded = load_tokens()
        assert loaded["access_token"] == "tok"


# ------------------------------------------------------------------
# TokenManager tests
# ------------------------------------------------------------------

class TestTokenManager:
    """Test token manager logic."""

    def test_is_expired(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("config.CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("config.TOKENS_FILE", tmp_path / "tokens.json")

        from config import save_config, save_tokens

        save_config({"client_id": "id", "client_secret": "secret"})
        save_tokens({"access_token": "tok", "refresh_token": "ref", "expires_at": 0})

        from olx_api.auth import TokenManager

        tm = TokenManager()
        assert tm.is_expired is True

    def test_is_not_expired(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("config.CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("config.TOKENS_FILE", tmp_path / "tokens.json")

        from config import save_config, save_tokens

        save_config({"client_id": "id", "client_secret": "secret"})
        save_tokens({"access_token": "tok", "refresh_token": "ref", "expires_at": time.time() + 3600})

        from olx_api.auth import TokenManager

        tm = TokenManager()
        assert tm.is_expired is False

    def test_not_authenticated(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("config.CONFIG_DIR", tmp_path)
        monkeypatch.setattr("config.CONFIG_FILE", tmp_path / "config.json")
        monkeypatch.setattr("config.TOKENS_FILE", tmp_path / "tokens.json")

        from config import save_config

        save_config({"client_id": "id", "client_secret": "secret"})

        from olx_api.auth import TokenManager

        tm = TokenManager()
        assert tm.is_authenticated is False


# ------------------------------------------------------------------
# OLXClient error handling
# ------------------------------------------------------------------

class TestOLXClientErrors:
    """Test that the client raises correct exception types."""

    def test_auth_error(self) -> None:
        from olx_api.client import OLXAuthError, OLXClient

        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 401
        resp.text = "Unauthorized"
        resp.json.return_value = {"error": {"message": "Invalid token"}}

        with pytest.raises(OLXAuthError):
            OLXClient._raise_for_status(resp)

    def test_not_found_error(self) -> None:
        from olx_api.client import OLXNotFoundError, OLXClient

        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 404
        resp.text = "Not Found"
        resp.json.return_value = {"error": {"message": "Advert not found"}}

        with pytest.raises(OLXNotFoundError):
            OLXClient._raise_for_status(resp)

    def test_rate_limit_error(self) -> None:
        from olx_api.client import OLXRateLimitError, OLXClient

        resp = MagicMock()
        resp.is_success = False
        resp.status_code = 429
        resp.text = "Too Many Requests"
        resp.json.return_value = {"error": {"message": "Rate limited"}}

        with pytest.raises(OLXRateLimitError):
            OLXClient._raise_for_status(resp)

    def test_success_no_error(self) -> None:
        from olx_api.client import OLXClient

        resp = MagicMock()
        resp.is_success = True
        # Should not raise
        OLXClient._raise_for_status(resp)
