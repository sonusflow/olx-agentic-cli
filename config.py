"""Configuration management for OLX CLI.

Stores credentials and tokens in ~/.olx-integration/ with restricted
file permissions (0600).
"""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".olx-integration"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKENS_FILE = CONFIG_DIR / "tokens.json"

# Default redirect URI — users should set their own via `olx setup`
DEFAULT_REDIRECT_URI = "http://localhost"


def _ensure_dir() -> None:
    """Create config directory with restricted permissions if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, stat.S_IRWXU)  # 700


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    _ensure_dir()
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 600


# ------------------------------------------------------------------
# Public helpers
# ------------------------------------------------------------------


def load_config() -> dict[str, Any]:
    """Load client credentials from config.json."""
    return _read_json(CONFIG_FILE)


def save_config(data: dict[str, Any]) -> None:
    """Persist client credentials to config.json."""
    _write_json(CONFIG_FILE, data)


def load_tokens() -> dict[str, Any]:
    """Load OAuth tokens from tokens.json."""
    return _read_json(TOKENS_FILE)


def save_tokens(data: dict[str, Any]) -> None:
    """Persist OAuth tokens to tokens.json."""
    _write_json(TOKENS_FILE, data)
