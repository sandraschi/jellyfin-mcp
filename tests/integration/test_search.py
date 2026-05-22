"""Integration tests — Jellyfin search."""

import pytest

from tests.conftest import tool_content

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_search_hints(live_jellyfin_service):
    result = await live_jellyfin_service.search(query="a", limit=5)
    assert "SearchHints" in result or "Items" in result


@pytest.mark.asyncio
async def test_search_tool(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.search import jellyfin_search

    result = tool_content(await jellyfin_search(operation="search", query="a", limit=5))
    assert result["success"] is True


@pytest.mark.asyncio
async def test_search_tool_requires_query(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.search import jellyfin_search

    result = tool_content(await jellyfin_search(operation="search"))
    assert result["success"] is False
