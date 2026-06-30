"""Media browsing for Jellyfin: browse, search, get, recent, similar, stream info, refresh, update, delete."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_media(
    operation: Annotated[
        Literal[
            "browse",
            "search",
            "get",
            "get_recent",
            "get_recommended",
            "similar",
            "stream_info",
            "refresh",
            "update",
            "delete",
        ],
        Field(description="Media operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="Library/parent ID for browsing or recent items.")] = None,
    item_id: Annotated[
        str | None, Field(description="Item ID (required for get/similar/stream_info/refresh/update/delete).")
    ] = None,
    query: Annotated[str | None, Field(description="Search term for browsing within a library.")] = None,
    media_type: Annotated[
        Literal["Movie", "Series", "MusicArtist", "Audio", "Photo"] | None,
        Field(description="Filter by media type: Movie, Series, MusicArtist, Audio, Photo."),
    ] = None,
    sort_by: Annotated[str, Field(description="Sort field. Default: SortName.")] = "SortName",
    sort_order: Annotated[Literal["Ascending", "Descending"], Field(description="Sort direction.")] = "Ascending",
    limit: Annotated[int, Field(description="Max items to return.", ge=1, le=500)] = 50,
    filters: Annotated[
        str | None, Field(description="Comma-separated Jellyfin filters (e.g. 'IsUnplayed,IsFavorite').")
    ] = None,
    metadata: Annotated[
        dict | None,
        Field(
            description="Metadata fields to update (for 'update' operation). Merged with the current item before posting."
        ),
    ] = None,
) -> ToolResult:
    """Browse and manage Jellyfin media items: browse library, search, get details, similar, stream info, CRUD.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_media(operation="browse", library_id="abc123")
    jellyfin_media(operation="get", item_id="def456")
    jellyfin_media(operation="get_recent", library_id="abc123", limit=10)
    jellyfin_media(operation="similar", item_id="def456")
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "browse":
            kwargs = {
                "sort_by": sort_by,
                "sort_order": sort_order,
                "limit": limit,
                "recursive": True,
            }
            if library_id:
                kwargs["parent_id"] = library_id
            if media_type:
                kwargs["include_item_types"] = media_type
            if filters:
                kwargs["filters"] = filters
            data = await jf.get_items(**kwargs)
        elif operation == "search":
            if not query:
                raise ValueError("query is required for 'search' operation.")
            kwargs = {
                "sort_by": sort_by,
                "sort_order": sort_order,
                "limit": limit,
                "recursive": True,
                "search_term": query,
            }
            if media_type:
                kwargs["include_item_types"] = media_type
            data = await jf.get_items(**kwargs)
        elif operation == "get":
            if not item_id:
                raise ValueError("item_id is required for 'get' operation.")
            data = await jf.get_item(item_id)
        elif operation == "get_recent":
            if not library_id:
                raise ValueError("library_id is required for 'get_recent' operation.")
            data = await jf.get_recent(library_id, limit=limit)
        elif operation == "get_recommended":
            kwargs = {"sort_by": "Random", "sort_order": "Ascending", "limit": limit, "recursive": True}
            if library_id:
                kwargs["parent_id"] = library_id
            if media_type:
                kwargs["include_item_types"] = media_type
            if filters:
                kwargs["filters"] = filters
            data = await jf.get_items(**kwargs)
        elif operation == "similar":
            if not item_id:
                raise ValueError("item_id is required for 'similar' operation.")
            data = await jf.get_similar(item_id, limit=limit)
        elif operation == "stream_info":
            if not item_id:
                raise ValueError("item_id is required for 'stream_info' operation.")
            data = await jf.get_item_stream_info(item_id)
        elif operation == "refresh":
            if not item_id:
                raise ValueError("item_id is required for 'refresh' operation.")
            data = await jf._post(f"/Items/{item_id}/Refresh", json_body={"Recursive": True})
        elif operation == "update":
            if not item_id:
                raise ValueError("item_id is required for 'update' operation.")
            if not metadata:
                raise ValueError("metadata is required for 'update' operation — pass a dict of fields to change.")
            current = await jf.get_item(item_id)
            current.update(metadata)
            data = await jf.update_item(item_id=item_id, metadata=current)
        elif operation == "delete":
            if not item_id:
                raise ValueError("item_id is required for 'delete' operation.")
            data = await jf.delete_item(item_id)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
