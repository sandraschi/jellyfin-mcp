"""Unit tests for JellyfinConfig."""

import os
from unittest.mock import patch

import pytest

from jellyfin_mcp.config import JellyfinConfig


class TestJellyfinConfig:
    def test_validate_server_url_adds_http_scheme(self):
        config = JellyfinConfig(server_url="localhost:8096", api_key="key")
        assert config.server_url == "http://localhost:8096"

    def test_validate_server_url_strips_trailing_slash(self):
        config = JellyfinConfig(server_url="http://localhost:8096/", api_key="key")
        assert config.server_url == "http://localhost:8096"

    def test_validate_api_key_required(self):
        with pytest.raises(ValueError, match="JELLYFIN_API_KEY"):
            JellyfinConfig(server_url="http://localhost:8096", api_key="")

    def test_validate_timeout_bounds(self):
        config = JellyfinConfig(server_url="http://localhost:8096", api_key="key", timeout=1)
        assert config.timeout == 5
        config = JellyfinConfig(server_url="http://localhost:8096", api_key="key", timeout=999)
        assert config.timeout == 300

    def test_base_url_alias(self, mock_config: JellyfinConfig):
        assert mock_config.base_url == mock_config.server_url

    @patch("jellyfin_mcp.config.load_dotenv")
    @patch.dict(
        os.environ,
        {
            "JELLYFIN_URL": "http://jellyfin.local:8096",
            "JELLYFIN_API_KEY": "env-key",
            "JELLYFIN_TIMEOUT": "45",
            "JELLYFIN_WS_ENABLED": "false",
        },
        clear=True,
    )
    def test_load_config_from_env(self, _mock_dotenv):
        config = JellyfinConfig.load_config()
        assert config.server_url == "http://jellyfin.local:8096"
        assert config.api_key == "env-key"
        assert config.timeout == 45
        assert config.ws_enabled is False
