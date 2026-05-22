"""jellyfin-mcp RAG Semantic Search Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...services.rag_service import RAGService
from ...services.registry import get_jellyfin_service
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_rag(
    operation: Annotated[
        Literal["sync", "search", "status", "reindex", "purge"],
        Field(description="RAG operation to perform."),
    ],
    query: Annotated[str | None, Field(description="Natural language search query.")] = None,
    limit: Annotated[int | None, Field(description="Max results to return (default: 10).")] = 10,
    library_id: Annotated[str | None, Field(description="Optional library ID to scope the operation.")] = None,
) -> dict[str, Any]:
    """Semantic (RAG) search over Jellyfin media metadata.

    Uses LanceDB + sentence-transformers to index and search media metadata.
    Supports sync, search, status, reindex, and purge operations.

    [PORTMANTEAU] Prevents tool explosion by merging 5 RAG operations into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int, "message": str}

    ## Examples
    - jellyfin_rag(operation="sync") — index all current library metadata
    - jellyfin_rag(operation="search", query="dark sci-fi movies with time travel")
    - jellyfin_rag(operation="status") — check indexed item count
    - jellyfin_rag(operation="purge") — clear the RAG index
    """
    try:
        rag = RAGService()

        if operation == "sync":
            jf = await get_jellyfin_service()
            # Fetch all items across all libraries (up to 5000)
            raw = await jf.get_items(limit=5000, recursive=True)
            items = raw.get("Items", raw) if isinstance(raw, dict) else raw
            # Normalise field names to lowercase for RAGService
            normalised = [
                {
                    "id": i.get("Id", ""),
                    "name": i.get("Name", ""),
                    "overview": i.get("Overview", ""),
                    "genres": i.get("Genres", []),
                    "type": i.get("Type", ""),
                    "production_year": i.get("ProductionYear"),
                }
                for i in (items if isinstance(items, list) else [])
            ]
            result = await rag.sync_metadata(items=normalised)
            return {
                "success": True,
                "operation": "sync",
                "message": f"RAG sync complete — {result.get('indexed', 0)} of {result.get('total', 0)} items indexed",
                "data": result,
            }

        if operation == "search":
            if not query:
                return {"success": False, "error": "query is required for search", "error_code": "MISSING_QUERY"}
            results = await rag.search(query=query, limit=limit or 10)
            return {
                "success": True,
                "operation": "search",
                "message": f"Found {len(results)} results for '{query}'",
                "data": results,
                "count": len(results),
            }

        if operation == "status":
            status = await rag.get_status()
            return {
                "success": True,
                "operation": "status",
                "message": f"RAG index status: {status.get('indexed_items', 0)} items indexed",
                "data": status,
            }

        if operation == "reindex":
            await rag.initialize()
            status = await rag.get_status()
            return {
                "success": True,
                "operation": "reindex",
                "message": "RAG index rebuilt",
                "data": status,
            }

        if operation == "purge":
            result = await rag.purge()
            return {
                "success": True,
                "operation": "purge",
                "message": "RAG index cleared — run sync to re-index",
                "data": result,
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: sync, search, status, reindex, purge"],
        }

    except ImportError as e:
        return {
            "success": False,
            "error": str(e),
            "error_code": "MISSING_DEPENDENCIES",
            "operation": operation,
        }
    except Exception as e:
        logger.exception("Error in jellyfin_rag operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
