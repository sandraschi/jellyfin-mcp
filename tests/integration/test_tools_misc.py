"""Integration tests — Live TV and help tools."""

import pytest

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_livetv_channels(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.livetv import jellyfin_livetv

    result = await jellyfin_livetv(operation="channels")
    assert result["success"] is True
    assert "count" in result


@pytest.mark.asyncio
async def test_livetv_manage(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.livetv import jellyfin_livetv

    result = await jellyfin_livetv(operation="manage")
    assert result["success"] is True
    assert "channels" in result["data"]


@pytest.mark.asyncio
async def test_help_discover():
    from jellyfin_mcp.tools.portmanteau.help import jellyfin_help

    result = await jellyfin_help(operation="discover")
    assert result["success"] is True
    assert len(result["data"]) >= 15


@pytest.mark.asyncio
async def test_help_quickstart():
    from jellyfin_mcp.tools.portmanteau.help import jellyfin_help

    result = await jellyfin_help(operation="quickstart")
    assert result["success"] is True
