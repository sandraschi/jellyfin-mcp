"""Unified search across Jellyfin: hints, advanced filters, people, studios, suggestions."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_search(
    operation: Annotated[
        Literal["search", "advanced", "people", "studios", "suggest", "saved"],
        Field(description="Search operation to perform."),
    ],
    query: Annotated[str | None, Field(description="Search term (required for search/advanced/suggest).")] = None,
    types: Annotated[
        str | None,
        Field(description="Comma-separated item types for advanced search (Movie,Series,MusicArtist,Audio,Photo)."),
    ] = None,
    limit: Annotated[int, Field(description="Max results.", ge=1, le=200)] = 50,
    filters: Annotated[str | None, Field(description="Comma-separated Jellyfin filters (e.g. 'IsUnplayed').")] = None,
    person: Annotated[str | None, Field(description="Person name filter (for people search).")] = None,
    studio: Annotated[str | None, Field(description="Studio name filter (for studios search).")] = None,
    year: Annotated[int | None, Field(description="Release year filter for advanced search.")] = None,
) -> ToolResult:
    """Search Jellyfin: hints-based search, advanced filtering, people, studios, and suggestions.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_search(operation="search", query="Inception")
    jellyfin_search(operation="advanced", query="action", types="Movie", year=2020, limit=10)
    jellyfin_search(operation="people", person="Christopher Nolan")
    jellyfin_search(operation="suggest", query="star")
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "search":
            if not query:
                raise ValueError("query is required for 'search' operation.")
            item_types = types or "Movie,Series,MusicArtist,Audio"
            data = await jf.search(query=query, include_item_types=item_types, limit=limit)
        elif operation == "advanced":
            if not query:
                raise ValueError("query is required for 'advanced' operation.")
            kwargs = {
                "search_term": query,
                "limit": limit,
                "recursive": True,
                "sort_by": "SortName",
                "sort_order": "Ascending",
            }
            if types:
                kwargs["include_item_types"] = types
            if filters:
                kwargs["filters"] = filters
            if year:
                kwargs["filters"] = f"({filters or ''}),Years" if filters else "Years"
                kwargs["years"] = str(year)
            data = await jf.get_items(**kwargs)
        elif operation == "people":
            params = {"Limit": limit}
            if person:
                params["SearchTerm"] = person
            data = await jf._get("/Persons", **params)
        elif operation == "studios":
            params = {"Limit": limit}
            if studio:
                params["SearchTerm"] = studio
            data = await jf._get("/Studios", **params)
        elif operation == "suggest":
            if not query:
                raise ValueError("query is required for 'suggest' operation.")
            item_types = types or "Movie,Series,MusicArtist,Audio"
            data = await jf.search(query=query, include_item_types=item_types, limit=min(limit, 20))
        elif operation == "saved":
            data = {
                "message": "Saved searches are not a built-in Jellyfin feature.",
                "hint": "Use jellyfin_playlist or jellyfin_collections for saved content.",
            }
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
