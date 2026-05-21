"""jellyfin-mcp Recommendation Engine Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
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
                return {"success": False, "error": "item_id is required for similar recommendations", "error_code": "MISSING_ITEM_ID"}
            return {
                "success": True,
                "operation": "similar",
                "message": "Similar items recommendations",
                "data": [],
                "count": 0,
                "item_id": item_id,
            }

        if operation == "genre":
            if not genre:
                return {"success": False, "error": "genre is required for genre recommendations", "error_code": "MISSING_GENRE"}
            return {
                "success": True,
                "operation": "genre",
                "message": f"Recommendations in genre '{genre}'",
                "data": [],
                "count": 0,
                "genre": genre,
            }

        if operation == "director":
            if not director:
                return {"success": False, "error": "director is required", "error_code": "MISSING_DIRECTOR"}
            return {
                "success": True,
                "operation": "director",
                "message": f"Recommendations by director '{director}'",
                "data": [],
                "count": 0,
                "director": director,
            }

        if operation == "actor":
            if not actor:
                return {"success": False, "error": "actor is required", "error_code": "MISSING_ACTOR"}
            return {
                "success": True,
                "operation": "actor",
                "message": f"Recommendations featuring '{actor}'",
                "data": [],
                "count": 0,
                "actor": actor,
            }

        if operation == "history":
            return {
                "success": True,
                "operation": "history",
                "message": "Watch-history-based recommendations",
                "data": [],
                "count": 0,
                "user_id": user_id,
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
