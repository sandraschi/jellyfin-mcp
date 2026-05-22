"""Unit tests for service registry."""

from unittest.mock import AsyncMock, patch

import pytest

from jellyfin_mcp.services.registry import (
    clear_services,
    get_jellyfin_service,
    get_registered_jellyfin_service,
    set_jellyfin_service,
)


@pytest.mark.asyncio
async def test_get_registered_returns_none_when_empty():
    assert get_registered_jellyfin_service() is None


@pytest.mark.asyncio
async def test_set_and_get_registered_service(mock_jellyfin_service):
    set_jellyfin_service(mock_jellyfin_service)
    assert get_registered_jellyfin_service() is mock_jellyfin_service


@pytest.mark.asyncio
async def test_get_jellyfin_service_reuses_registered(mock_jellyfin_service):
    set_jellyfin_service(mock_jellyfin_service)
    service = await get_jellyfin_service()
    assert service is mock_jellyfin_service


@pytest.mark.asyncio
async def test_get_jellyfin_service_creates_on_demand(mock_config):
    created = AsyncMock()
    created.is_initialized = True

    with patch("jellyfin_mcp.config.get_settings", return_value=mock_config):
        with patch("jellyfin_mcp.services.jellyfin_service.JellyfinService") as service_cls:
            service_cls.return_value = created
            created.connect = AsyncMock()

            service = await get_jellyfin_service()
            assert service is created
            created.connect.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_jellyfin_service_requires_api_key():
    from types import SimpleNamespace

    config = SimpleNamespace(server_url="http://localhost:8096", api_key="", timeout=10)

    with patch("jellyfin_mcp.config.get_settings", return_value=config):
        with pytest.raises(RuntimeError, match="JELLYFIN_API_KEY"):
            await get_jellyfin_service()


@pytest.mark.asyncio
async def test_clear_services_disconnects(mock_jellyfin_service):
    mock_jellyfin_service.disconnect = AsyncMock()
    set_jellyfin_service(mock_jellyfin_service)
    await clear_services()
    mock_jellyfin_service.disconnect.assert_awaited_once()
    assert get_registered_jellyfin_service() is None
