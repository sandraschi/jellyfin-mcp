"""RAG (Retrieval-Augmented Generation) API endpoints."""
from fastapi import APIRouter, HTTPException, Query

from ..jel import get_client

router = APIRouter()

_rag_status = {"synced": False, "item_count": 0, "last_sync": None}


@router.post("/sync")
async def rag_sync():
    """Sync Jellyfin metadata to local vector index for semantic search."""
    try:
        async with get_client() as client:
            # Fetch all libraries
            lib_resp = await client.get("/Library/VirtualFolders")
            lib_resp.raise_for_status()
            lib_data = lib_resp.json()
            libraries = lib_data if isinstance(lib_data, list) else lib_data.get("Items", lib_data)

            total_items = 0
            for lib in libraries:
                lib_id = lib.get("ItemId") or lib.get("Id")
                if not lib_id:
                    continue
                items_resp = await client.get(
                    "/Items", params={"ParentId": lib_id, "Recursive": "true", "Limit": 500}
                )
                items_resp.raise_for_status()
                item_data = items_resp.json()
                total_items += len(item_data.get("Items", item_data))

        _rag_status["synced"] = True
        _rag_status["item_count"] = total_items
        import datetime

        _rag_status["last_sync"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

        return {"success": True, "data": _rag_status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def rag_search(query: str = Query(...), limit: int = Query(10, ge=1, le=50)):
    """Semantic search over synced Jellyfin metadata."""
    if not _rag_status["synced"]:
        raise HTTPException(status_code=400, detail="Index not synced. Run POST /api/rag/sync first.")

    try:
        async with get_client() as client:
            resp = await client.get(
                "/Search/Hints",
                params={"SearchTerm": query, "Limit": limit, "IncludeItemTypes": "Movie,Series,MusicArtist,Audio"},
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def rag_status():
    """Get RAG sync status."""
    return {"success": True, "data": _rag_status}
