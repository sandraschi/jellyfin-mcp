"""Search API endpoints."""
from fastapi import APIRouter, HTTPException, Query

from ..jel import get_client

router = APIRouter()


@router.get("/")
async def search(
    query: str | None = Query(None),
    q: str | None = Query(None),
    include_item_types: str = Query("Movie,Series,MusicArtist,Audio"),
    limit: int = Query(50, ge=1, le=200),
):
    """Search Jellyfin media via search hints."""
    search_term = query or q
    if not search_term:
        raise HTTPException(status_code=422, detail="query parameter is required")
    try:
        params = {
            "SearchTerm": search_term,
            "IncludeItemTypes": include_item_types,
            "Limit": limit,
        }
        async with get_client() as client:
            resp = await client.get("/Search/Hints", params=params)
            resp.raise_for_status()
            payload = resp.json()
            hints = payload.get("SearchHints", payload if isinstance(payload, list) else [])
            items = []
            for hint in hints:
                item = hint.get("Item", hint)
                if item:
                    items.append(item)
            return {"success": True, "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/advanced")
async def advanced_search(
    query: str = Query(...),
    include_item_types: str = Query("Movie,Series,MusicArtist,Audio"),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("SortName"),
    sort_order: str = Query("Ascending"),
    has_subtitles: bool | None = Query(None),
    media_types: str | None = Query(None),
    genres: str | None = Query(None),
    years: str | None = Query(None),
):
    """Advanced search with filters."""
    try:
        params: dict = {
            "SearchTerm": query,
            "IncludeItemTypes": include_item_types,
            "Limit": limit,
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Recursive": "true",
        }
        if has_subtitles is not None:
            params["HasSubtitles"] = str(has_subtitles).lower()
        if media_types:
            params["MediaTypes"] = media_types
        if genres:
            params["Genres"] = genres
        if years:
            params["Years"] = years

        async with get_client() as client:
            resp = await client.get("/Items", params=params)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
