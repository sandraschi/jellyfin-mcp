"""Integration tests — live Jellyfin server connection."""

import pytest

from jellyfin_mcp.services.base import JellyfinConnectionError
from jellyfin_mcp.services.jellyfin_service import JellyfinService

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_connect_to_live_server(jellyfin_config):
    service = JellyfinService(
        jellyfin_config.server_url,
        jellyfin_config.api_key,
        jellyfin_config.timeout,
    )
    await service.connect()
    info = await service.get_server_info()
    assert "Version" in info
    await service.disconnect()


@pytest.mark.asyncio
async def test_invalid_api_key_raises(live_jellyfin_service, jellyfin_config):
    bad = JellyfinService(jellyfin_config.server_url, "invalid-key-000", jellyfin_config.timeout)
    with pytest.raises(JellyfinConnectionError):
        await bad.connect()


@pytest.mark.asyncio
async def test_server_status_healthy(live_jellyfin_service):
    status = await live_jellyfin_service.get_server_status()
    assert status["healthy"] is True
    assert status["version"]
