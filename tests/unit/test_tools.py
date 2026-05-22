"""Unit tests for portmanteau MCP tools."""

from unittest.mock import AsyncMock

import pytest

from jellyfin_mcp.services.registry import set_jellyfin_service
from tests.conftest import tool_content


@pytest.mark.asyncio
async def test_jellyfin_library_list(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.library import jellyfin_library

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_library(operation="list"))
    assert result["success"] is True
    assert result["operation"] == "list"
    assert len(result["data"]) == 2


@pytest.mark.asyncio
async def test_jellyfin_library_get_requires_id(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.library import jellyfin_library

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_library(operation="get"))
    assert result["success"] is False
    assert "library_id" in result["error"]


@pytest.mark.asyncio
async def test_jellyfin_library_stats(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.library import jellyfin_library

    mock_jellyfin_service.get_library = AsyncMock(return_value={"Name": "Movies", "ItemId": "lib1"})
    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_library(operation="stats", library_id="lib1"))
    assert result["success"] is True
    assert result["data"]["total_items"] == 1


@pytest.mark.asyncio
async def test_jellyfin_media_browse(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.media import jellyfin_media

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_media(operation="browse", library_id="lib1"))
    assert result["success"] is True
    assert result["data"]["TotalRecordCount"] == 1


@pytest.mark.asyncio
async def test_jellyfin_media_get(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.media import jellyfin_media

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_media(operation="get", item_id="item1"))
    assert result["success"] is True
    assert result["data"]["Name"] == "Test Movie"


@pytest.mark.asyncio
async def test_jellyfin_search_requires_query(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.search import jellyfin_search

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_search(operation="search"))
    assert result["success"] is False


@pytest.mark.asyncio
async def test_jellyfin_user_list(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.user import jellyfin_user

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_user(operation="list"))
    assert result["success"] is True
    assert len(result["data"]) == 1


@pytest.mark.asyncio
async def test_jellyfin_playback_sessions(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.playback import jellyfin_playback

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_playback(operation="list_sessions"))
    assert result["success"] is True
    assert result["data"] == []


@pytest.mark.asyncio
async def test_jellyfin_server_info(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.server import jellyfin_server

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_server(operation="info"))
    assert result["success"] is True
    assert result["data"]["Version"] == "10.11.9"


@pytest.mark.asyncio
async def test_jellyfin_plugin_list(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.plugin import jellyfin_plugin

    set_jellyfin_service(mock_jellyfin_service)
    result = tool_content(await jellyfin_plugin(operation="list"))
    assert result["success"] is True


@pytest.mark.asyncio
async def test_jellyfin_help_discover():
    from jellyfin_mcp.tools.portmanteau.help import jellyfin_help

    result = await jellyfin_help(operation="discover")
    assert result["success"] is True
    assert isinstance(result["data"], list)
    assert len(result["data"]) >= 15


@pytest.mark.asyncio
async def test_jellyfin_livetv_channels(mock_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.livetv import jellyfin_livetv

    set_jellyfin_service(mock_jellyfin_service)
    result = await jellyfin_livetv(operation="channels")
    assert result["success"] is True
    assert result["operation"] == "channels"
