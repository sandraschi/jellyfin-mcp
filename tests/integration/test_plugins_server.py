"""Integration tests — Jellyfin plugins and server tools."""

import pytest

from tests.conftest import tool_content

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_plugins(live_jellyfin_service):
    plugins = await live_jellyfin_service.get_plugins()
    assert isinstance(plugins, list)


@pytest.mark.asyncio
async def test_plugin_tool_list(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.plugin import jellyfin_plugin

    result = tool_content(await jellyfin_plugin(operation="list"))
    assert result["success"] is True


@pytest.mark.asyncio
async def test_plugin_catalog(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.plugin import jellyfin_plugin

    result = tool_content(await jellyfin_plugin(operation="catalog"))
    assert result["success"] is True


@pytest.mark.asyncio
async def test_server_status_tool(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.server import jellyfin_server

    result = tool_content(await jellyfin_server(operation="status"))
    assert result["success"] is True
    assert result["data"]["healthy"] is True


@pytest.mark.asyncio
async def test_server_tasks_tool(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.server import jellyfin_server

    result = tool_content(await jellyfin_server(operation="tasks"))
    assert result["success"] is True
