"""
jellyfin-mcp Configuration Management.

Handles configuration from environment variables for Jellyfin server connection settings.
"""

import json
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


def setup_logging(level: str = "INFO", format_string: str | None = None) -> None:
    """Configure logging for the entire application."""
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(format_string)
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)


class JellyfinConfig(BaseModel):
    """Configuration for Jellyfin server connection."""

    server_url: str = Field(default="http://localhost:8096", description="Jellyfin server URL")
    api_key: str = Field(description="Jellyfin API key")
    username: str | None = Field(default=None, description="Jellyfin username (fallback auth)")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    ws_enabled: bool = Field(default=True, description="Enable WebSocket event bridge")

    @field_validator("server_url")
    @classmethod
    def validate_server_url(cls, v):
        if not v.startswith(("http://", "https://")):
            return f"http://{v}"
        return v.rstrip("/")

    @field_validator("api_key")
    @classmethod
    def validate_api_key(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("JELLYFIN_API_KEY is required")
        return v.strip()

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, v):
        return max(5, min(300, v))

    @classmethod
    def load_config(cls, config_file: str | None = None) -> "JellyfinConfig":
        """Load configuration from environment variables and optional JSON file."""
        possible_env_paths = [
            Path(__file__).parent.parent.parent / ".env",
            Path.cwd() / ".env",
            Path(__file__).parent / ".env",
        ]

        env_loaded = False
        for env_path in possible_env_paths:
            if env_path.exists():
                load_dotenv(dotenv_path=env_path)
                env_loaded = True
                break

        if not env_loaded:
            load_dotenv()

        config_data = {}

        if config_file:
            config_path = Path(config_file)
            if config_path.exists():
                try:
                    with open(config_path, encoding="utf-8") as f:
                        file_data = json.load(f)
                        config_data.update(file_data)
                except (OSError, json.JSONDecodeError) as e:
                    sys.stderr.write(f"Warning: Could not load config file {config_file}: {e}\n")

        env_mappings = {
            "JELLYFIN_URL": "server_url",
            "JELLYFIN_SERVER_URL": "server_url",
            "JELLYFIN_API_KEY": "api_key",
            "JELLYFIN_TOKEN": "api_key",
            "JELLYFIN_USERNAME": "username",
            "JELLYFIN_TIMEOUT": "timeout",
            "JELLYFIN_WS_ENABLED": "ws_enabled",
        }

        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if config_key == "timeout":
                    try:
                        config_data[config_key] = int(env_value)
                    except ValueError:
                        sys.stderr.write(f"Warning: Invalid integer for {env_var}: {env_value}\n")
                elif config_key == "ws_enabled":
                    config_data[config_key] = env_value.lower() in ("1", "true", "yes")
                else:
                    config_data[config_key] = env_value

        return cls(**config_data)

    @property
    def base_url(self) -> str:
        return self.server_url


def get_settings() -> JellyfinConfig:
    """Get the application settings."""
    return JellyfinConfig.load_config()
