"""Jellyfin HTTP client helper for webapp API routes."""

import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Try to load .env from repo root
_env_path = Path(__file__).parent.parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(dotenv_path=_env_path)
else:
    load_dotenv()


def _get_jellyfin_config():
    url = os.getenv("JELLYFIN_URL") or os.getenv("JELLYFIN_SERVER_URL", "http://localhost:8096")
    api_key = os.getenv("JELLYFIN_API_KEY") or os.getenv("JELLYFIN_TOKEN", "")
    return url.rstrip("/"), api_key


def get_client() -> httpx.AsyncClient:
    url, api_key = _get_jellyfin_config()
    headers = {"X-Emby-Token": api_key, "Accept": "application/json"}
    return httpx.AsyncClient(base_url=url, headers=headers, timeout=30, follow_redirects=True)


def get_base_url() -> str:
    url, _ = _get_jellyfin_config()
    return url


def get_api_key() -> str:
    _, api_key = _get_jellyfin_config()
    return api_key
