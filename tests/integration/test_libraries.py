"""Integration tests — Jellyfin libraries."""

import pytest

from tests.conftest import tool_content

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_libraries(live_jellyfin_service):
    libraries = await live_jellyfin_service.get_libraries()
    assert isinstance(libraries, list)
    assert len(libraries) >= 0


@pytest.mark.asyncio
async def test_library_tool_list(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.library import jellyfin_library

    result = tool_content(await jellyfin_library(operation="list"))
    assert result["success"] is True
    assert isinstance(result["data"], list)


@pytest.mark.asyncio
async def test_library_stats_when_libraries_exist(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.library import jellyfin_library

    libraries = await live_jellyfin_service.get_libraries()
    if not libraries:
        pytest.skip("No libraries configured on Jellyfin server")

    library_id = libraries[0].get("ItemId") or libraries[0].get("Id")
    result = tool_content(await jellyfin_library(operation="stats", library_id=library_id))
    assert result["success"] is True
    assert "total_items" in result["data"]
