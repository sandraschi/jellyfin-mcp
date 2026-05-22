"""Integration tests — Jellyfin media items."""

import pytest

from tests.conftest import tool_content

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_items(live_jellyfin_service):
    result = await live_jellyfin_service.get_items(limit=5)
    assert "Items" in result
    assert "TotalRecordCount" in result


@pytest.mark.asyncio
async def test_media_browse_tool(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.media import jellyfin_media

    libraries = await live_jellyfin_service.get_libraries()
    if not libraries:
        pytest.skip("No libraries configured")

    library_id = libraries[0].get("ItemId") or libraries[0].get("Id")
    result = tool_content(await jellyfin_media(operation="browse", library_id=library_id, limit=5))
    assert result["success"] is True


@pytest.mark.asyncio
async def test_get_item_when_media_exists(live_jellyfin_service):
    items = await live_jellyfin_service.get_items(limit=1)
    if not items.get("Items"):
        pytest.skip("No media items in library")

    item_id = items["Items"][0]["Id"]
    item = await live_jellyfin_service.get_item(item_id)
    assert item["Id"] == item_id


@pytest.mark.asyncio
async def test_media_get_tool(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.media import jellyfin_media

    items = await live_jellyfin_service.get_items(limit=1)
    if not items.get("Items"):
        pytest.skip("No media items in library")

    item_id = items["Items"][0]["Id"]
    result = tool_content(await jellyfin_media(operation="get", item_id=item_id))
    assert result["success"] is True
    assert result["data"]["Id"] == item_id
