"""Media/Items API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from ..jel import get_client

router = APIRouter()

MEDIA_TYPE_MAP = {
    "Movies": "Movie",
    "Series": "Series",
    "Music": "MusicAlbum",
    "Photos": "Photo",
    "Books": "Book",
}


@router.get("/browse")
async def browse_items(
    parent_id: str | None = Query(None),
    include_item_types: str | None = Query(None),
    sort_by: str = Query("SortName"),
    sort_order: str = Query("Ascending"),
    limit: int = Query(100, ge=1, le=500),
    filters: str | None = Query(None),
):
    """Browse items in a library or folder."""
    try:
        params = {
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Limit": limit,
            "Recursive": "true",
        }
        if parent_id:
            params["ParentId"] = parent_id
        if include_item_types:
            params["IncludeItemTypes"] = include_item_types
        if filters:
            params["Filters"] = filters

        async with get_client() as client:
            resp = await client.get("/Items", params=params)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent(
    library_id: str = Query(...),
    limit: int = Query(24, ge=1, le=100),
):
    """Get recently added items in a library."""
    try:
        params = {"ParentId": library_id, "Limit": limit}
        async with get_client() as client:
            resp = await client.get("/Items/Latest", params=params)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/similar")
async def get_similar(
    item_id: str = Query(...),
    limit: int = Query(10, ge=1, le=50),
):
    """Get items similar to a given item."""
    try:
        async with get_client() as client:
            resp = await client.get(f"/Items/{item_id}/Similar", params={"Limit": limit})
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{path_id}")
async def browse_or_get_item(
    path_id: str,
    limit: int = Query(100, ge=1, le=500),
    sort_by: str = Query("SortName"),
    sort_order: str = Query("Ascending"),
):
    """Browse by media type label (Movies, Series, ...) or fetch a single item by ID."""
    if path_id in MEDIA_TYPE_MAP:
        try:
            params = {
                "IncludeItemTypes": MEDIA_TYPE_MAP[path_id],
                "SortBy": sort_by,
                "SortOrder": sort_order,
                "Limit": limit,
                "Recursive": "true",
            }
            async with get_client() as client:
                resp = await client.get("/Items", params=params)
                resp.raise_for_status()
                return {"success": True, "data": resp.json()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    try:
        async with get_client() as client:
            users_resp = await client.get("/Users")
            users_resp.raise_for_status()
            users = users_resp.json()
            user_id = users[0]["Id"] if users else ""
            resp = await client.get(f"/Users/{user_id}/Items/{path_id}")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
