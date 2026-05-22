"""Integration tests — RAG semantic search (slow, optional)."""

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.slow]


@pytest.mark.asyncio
async def test_rag_status(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.rag import jellyfin_rag

    result = await jellyfin_rag(operation="status")
    assert result["success"] is True


@pytest.mark.asyncio
async def test_rag_sync_and_search(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.rag import jellyfin_rag

    items = await live_jellyfin_service.get_items(limit=10)
    media_items = items.get("Items", [])
    if not media_items:
        pytest.skip("No media items to index")

    sync_result = await jellyfin_rag(operation="sync")
    assert sync_result["success"] is True

    search_result = await jellyfin_rag(operation="search", query="movie", limit=3)
    assert search_result["success"] is True
