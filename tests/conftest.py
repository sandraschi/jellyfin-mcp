"""Shared pytest configuration and fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest

from jellyfin_mcp.config import JellyfinConfig
from jellyfin_mcp.services.jellyfin_service import JellyfinService


def tool_content(result) -> dict:
    """Extract dict content from a ToolResult or plain dict."""
    if isinstance(result, dict):
        return result
    content = getattr(result, "content", result)
    if isinstance(content, dict):
        return content
    if isinstance(content, list) and content:
        first = content[0]
        if hasattr(first, "text"):
            import json

            return json.loads(first.text)
    return {"raw": content}


@pytest.fixture
def mock_config() -> JellyfinConfig:
    """Mock JellyfinConfig for unit tests."""
    return JellyfinConfig(
        server_url="http://localhost:8096",
        api_key="test-api-key",
        timeout=10,
        ws_enabled=False,
    )


@pytest.fixture
def mock_jellyfin_service() -> AsyncMock:
    """Mock JellyfinService with canned responses."""
    service = AsyncMock(spec=JellyfinService)
    service.is_initialized = True
    service.get_libraries = AsyncMock(
        return_value=[
            {"Id": "lib1", "ItemId": "lib1", "Name": "Movies", "CollectionType": "movies", "ItemCount": 42},
            {"Id": "lib2", "ItemId": "lib2", "Name": "TV Shows", "CollectionType": "tvshows", "ItemCount": 15},
        ]
    )
    service.get_server_info = AsyncMock(
        return_value={"Version": "10.11.9", "OperatingSystem": "Windows", "Id": "server1"}
    )
    service.get_server_status = AsyncMock(
        return_value={"version": "10.11.9", "os": "Windows", "id": "server1", "healthy": True}
    )
    service.get_sessions = AsyncMock(return_value=[])
    service.get_plugins = AsyncMock(return_value=[])
    service.get_users = AsyncMock(return_value=[{"Id": "user1", "Name": "admin"}])
    service.get_default_user_id = AsyncMock(return_value="user1")
    service.get_items = AsyncMock(
        return_value={
            "Items": [{"Id": "item1", "Name": "Test Movie", "Type": "Movie", "ProductionYear": 2024}],
            "TotalRecordCount": 1,
        }
    )
    service.get_item = AsyncMock(
        return_value={"Id": "item1", "Name": "Test Movie", "Type": "Movie", "ProductionYear": 2024}
    )
    service.get_channels = AsyncMock(return_value={"Items": []})
    service.get_recordings = AsyncMock(return_value={"Items": []})
    service.get_epg = AsyncMock(return_value={"Items": []})
    service._get = AsyncMock(return_value={"Items": []})
    service._post = AsyncMock(return_value={"success": True})
    service._delete = AsyncMock(return_value={"success": True})
    return service


@pytest.fixture(autouse=True)
async def reset_service_registry():
    """Ensure service registry is clean between tests."""
    from jellyfin_mcp.services.registry import clear_services

    await clear_services()
    yield
    await clear_services()


@pytest.fixture
def integration_enabled() -> bool:
    """True when live Jellyfin credentials are configured."""
    try:
        config = JellyfinConfig.load_config()
    except Exception:
        return False
    return bool(config.api_key and config.api_key != "your-jellyfin-api-key-here")


@pytest.fixture
def jellyfin_config(integration_enabled: bool) -> JellyfinConfig:
    """Load real Jellyfin config or skip integration tests."""
    if not integration_enabled:
        pytest.skip("JELLYFIN_API_KEY not configured for integration tests")
    return JellyfinConfig.load_config()


@pytest.fixture
async def live_jellyfin_service(jellyfin_config: JellyfinConfig) -> AsyncIterator[JellyfinService]:
    """Connected JellyfinService against the running server."""
    from jellyfin_mcp.services.registry import set_jellyfin_service

    service = JellyfinService(
        base_url=jellyfin_config.server_url,
        api_key=jellyfin_config.api_key,
        timeout=jellyfin_config.timeout,
    )
    await service.connect()
    set_jellyfin_service(service)
    yield service
    await service.disconnect()
