"""Backend configuration."""

from pydantic_settings import BaseSettings


class BackendSettings(BaseSettings):
    API_TITLE: str = "jellyfin-mcp Webapp API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "Webapp backend for jellyfin-mcp"
    CORS_ORIGINS: str = (
        "http://localhost:10935,http://127.0.0.1:10935,http://tauri.localhost,https://tauri.localhost,tauri://localhost"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = BackendSettings()
