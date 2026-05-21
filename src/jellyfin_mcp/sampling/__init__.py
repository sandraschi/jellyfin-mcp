"""Sampling configuration and handler for jellyfin-mcp."""

import os

import httpx
from fastmcp import Context


class JellyfinSamplingConfig:
    """Configuration for LLM sampling."""

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434/v1",
        model: str = "llama3.2",
        api_key: str | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key

    @classmethod
    def from_env(cls) -> "JellyfinSamplingConfig":
        return cls(
            base_url=os.getenv("JELLYFIN_SAMPLING_BASE_URL", os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")),
            model=os.getenv("JELLYFIN_SAMPLING_MODEL", os.getenv("LLM_MODEL", "llama3.2")),
            api_key=os.getenv("JELLYFIN_SAMPLING_API_KEY", os.getenv("LLM_API_KEY")),
        )


class JellyfinSamplingHandler:
    """OpenAI-compatible sampling handler for FastMCP 3.2."""

    def __init__(self, config: JellyfinSamplingConfig):
        self.config = config

    async def __call__(self, context: Context, messages: list, tools: list | None = None) -> dict:
        """Handle a sampling request."""
        payload = {
            "model": self.config.model,
            "messages": [self._convert_message(m) for m in messages],
        }
        if tools:
            payload["tools"] = tools

        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.config.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            return resp.json()

    def _convert_message(self, msg) -> dict:
        """Convert FastMCP message to OpenAI format."""
        if hasattr(msg, "role") and hasattr(msg, "content"):
            return {"role": msg.role, "content": msg.content}
        if isinstance(msg, dict):
            return msg
        return {"role": "user", "content": str(msg)}
