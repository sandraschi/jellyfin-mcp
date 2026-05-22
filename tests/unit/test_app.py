"""Unit tests for app lifespan and MCP instance."""

from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_lifespan_connects_and_clears_services(mock_config):
    from jellyfin_mcp.app import _jellyfin_lifespan
    from jellyfin_mcp.services.registry import get_registered_jellyfin_service

    app = AsyncMock()
    app.state = AsyncMock()

    mock_service = AsyncMock()
    mock_service.is_initialized = True
    mock_service.connect = AsyncMock()
    mock_service.disconnect = AsyncMock()

    with patch("jellyfin_mcp.config.get_settings", return_value=mock_config):
        with patch("jellyfin_mcp.services.jellyfin_service.JellyfinService", return_value=mock_service):
            async with _jellyfin_lifespan(app):
                assert get_registered_jellyfin_service() is mock_service

    assert get_registered_jellyfin_service() is None
    mock_service.disconnect.assert_awaited()


@pytest.mark.asyncio
async def test_lifespan_survives_connection_failure():
    from jellyfin_mcp.app import _jellyfin_lifespan

    app = AsyncMock()
    app.state = AsyncMock()

    with patch("jellyfin_mcp.config.get_settings", side_effect=RuntimeError("config error")):
        async with _jellyfin_lifespan(app):
            pass


def test_mcp_instance_has_instructions():
    from jellyfin_mcp.app import mcp

    assert mcp.name == "JellyfinMCP"
    assert "jellyfin_library" in mcp.instructions


def test_capabilities_resource():
    from jellyfin_mcp.app import jellyfin_capabilities_resource

    text = jellyfin_capabilities_resource()
    assert "jellyfin_plugin" in text
    assert "22 tools" in text
