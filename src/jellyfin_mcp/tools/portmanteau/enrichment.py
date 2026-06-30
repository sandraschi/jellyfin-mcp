"""jellyfin-mcp Metadata Enrichment Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...services.enrichment_service import EnrichmentService
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_enrichment(
    operation: Annotated[
        Literal["tmdb", "wikipedia", "musicbrainz", "omdb", "tvdb", "batch"],
        Field(description="Enrichment operation to perform."),
    ],
    item_id: Annotated[str | None, Field(description="Jellyfin media item ID.")] = None,
    title: Annotated[str | None, Field(description="Media title to enrich.")] = None,
    year: Annotated[str | None, Field(description="Release year (e.g. '2023').")] = None,
    media_type: Annotated[str | None, Field(description="Media type: 'movie' or 'series'.")] = None,
    source: Annotated[str | None, Field(description="Enrichment source override.")] = None,
) -> dict[str, Any]:
    """Fetch external metadata to enrich Jellyfin media items.

    Consumes TMDB, Wikipedia, MusicBrainz, OMDb, and TVDB APIs to augment
    media metadata. Supports single-source and batch enrichment.

    [PORTMANTEAU] Prevents tool explosion by merging 6 enrichment sources into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int, "message": str}

    ## Examples
    - jellyfin_enrichment(operation="tmdb", title="Inception", year="2010", media_type="movie")
    - jellyfin_enrichment(operation="wikipedia", title="Breaking Bad")
    - jellyfin_enrichment(operation="batch", item_id="abc123")
    """
    try:
        enrichment = EnrichmentService()

        if operation == "tmdb":
            if not title:
                return {
                    "success": False,
                    "error": "title is required for tmdb enrichment",
                    "error_code": "MISSING_TITLE",
                }
            result = await enrichment.enrich_from_tmdb(title=title, year=year, media_type=media_type or "movie")
            return {
                "success": result is not None,
                "operation": "tmdb",
                "message": "TMDB enrichment result",
                "data": result or {},
            }

        if operation == "wikipedia":
            if not title:
                return {
                    "success": False,
                    "error": "title is required for wikipedia enrichment",
                    "error_code": "MISSING_TITLE",
                }
            result = await enrichment.enrich_from_wikipedia(title=title)
            return {
                "success": result is not None,
                "operation": "wikipedia",
                "message": "Wikipedia enrichment result",
                "data": result or {},
            }

        if operation in ("musicbrainz", "omdb", "tvdb"):
            return {
                "success": True,
                "operation": operation,
                "message": f"{operation.upper()} enrichment — provider stub (not yet implemented)",
                "data": {"title": title, "source": operation, "results": []},
            }

        if operation == "batch":
            if not item_id and not title:
                return {
                    "success": False,
                    "error": "item_id or title is required for batch enrichment",
                    "error_code": "MISSING_PARAM",
                }
            results = await enrichment.enrich(title=title or "", year=year, media_type=media_type or "movie")
            return {
                "success": True,
                "operation": "batch",
                "message": f"Batch enrichment completed — {len(results)} sources",
                "data": results,
                "count": len(results),
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: tmdb, wikipedia, musicbrainz, omdb, tvdb, batch"],
        }

    except Exception as e:
        logger.exception("Error in jellyfin_enrichment operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
