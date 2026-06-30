"""jellyfin-mcp Recommendation Engine Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_recommend(
    operation: Annotated[
        Literal["similar", "genre", "director", "actor", "history"],
        Field(description="Recommendation operation to perform."),
    ],
    item_id: Annotated[str | None, Field(description="Reference media item ID.")] = None,
    user_id: Annotated[str | None, Field(description="User ID for personalized recommendations.")] = None,
    genre: Annotated[str | None, Field(description="Genre to base recommendations on.")] = None,
    director: Annotated[str | None, Field(description="Director to base recommendations on.")] = None,
    actor: Annotated[str | None, Field(description="Actor to base recommendations on.")] = None,
    limit: Annotated[int | None, Field(description="Max recommendations (default: 10).")] = 10,
) -> dict[str, Any]:
    """Media recommendation engine for Jellyfin libraries.

    Consolidates all recommendation operations into a single portmanteau interface:
    similar items, genre-based, director-based, actor-based, and watch-history-based.

    [PORTMANTEAU] Prevents tool explosion by merging 5 recommendation types into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int, "message": str}

    ## Examples
    - jellyfin_recommend(operation="similar", item_id="movie123")
    - jellyfin_recommend(operation="genre", genre="sci-fi", limit=5)
    - jellyfin_recommend(operation="director", director="Christopher Nolan")
    - jellyfin_recommend(operation="history", user_id="user123")
    """
    try:
        if operation == "similar":
            if not item_id:
                return {
                    "success": False,
                    "error": "item_id is required for similar recommendations",
                    "error_code": "MISSING_ITEM_ID",
                }
            jf = await get_jellyfin_service()
            raw = await jf.get_similar(item_id, limit=limit or 10)
            items = raw.get("Items", raw) if isinstance(raw, dict) else raw
            return {
                "success": True,
                "operation": "similar",
                "message": f"Found {len(items)} similar items",
                "data": items,
                "count": len(items),
                "item_id": item_id,
            }

        if operation == "genre":
            if not genre:
                return {
                    "success": False,
                    "error": "genre is required for genre recommendations",
                    "error_code": "MISSING_GENRE",
                }
            jf = await get_jellyfin_service()
            # Pass genre as server-side filter; Jellyfin accepts Genres as a comma-separated param
            raw = await jf.get_items(limit=limit or 10, recursive=True, genres=genre)
            items = raw.get("Items", []) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "genre",
                "message": f"{len(items)} recommendations in genre '{genre}'",
                "data": items,
                "count": len(items),
                "genre": genre,
            }

        if operation == "director":
            if not director:
                return {"success": False, "error": "director is required", "error_code": "MISSING_DIRECTOR"}
            jf = await get_jellyfin_service()
            raw = await jf.search(query=director, include_item_types="Movie,Series", limit=limit or 10)
            items = raw.get("SearchHints", raw.get("Items", [])) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "director",
                "message": f"{len(items)} recommendations by director '{director}'",
                "data": items,
                "count": len(items),
                "director": director,
            }

        if operation == "actor":
            if not actor:
                return {"success": False, "error": "actor is required", "error_code": "MISSING_ACTOR"}
            jf = await get_jellyfin_service()
            raw = await jf.search(query=actor, include_item_types="Movie,Series", limit=limit or 10)
            items = raw.get("SearchHints", raw.get("Items", [])) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "actor",
                "message": f"{len(items)} recommendations featuring '{actor}'",
                "data": items,
                "count": len(items),
                "actor": actor,
            }

        if operation == "history":
            jf = await get_jellyfin_service()
            uid = user_id or await jf.get_default_user_id()
            # Use played-items endpoint for actual watch history, not live sessions
            raw = await jf._get(
                f"/Users/{uid}/Items",
                SortBy="DatePlayed",
                SortOrder="Descending",
                Filters="IsPlayed",
                Limit=limit or 10,
                Recursive="true",
            )
            items = raw.get("Items", []) if isinstance(raw, dict) else []
            return {
                "success": True,
                "operation": "history",
                "message": f"{len(items)} recently played items for user",
                "data": items,
                "count": len(items),
                "user_id": uid,
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: similar, genre, director, actor, history"],
        }

    except Exception as e:
        logger.exception("Error in jellyfin_recommend operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
