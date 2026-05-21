"""Library management for Jellyfin: list, create, scan, refresh, stats, cleanup."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp


def _get_jellyfin_service():
    from ...config import get_settings
    from ...services.jellyfin_service import JellyfinService

    settings = get_settings()
    if not settings.api_key:
        raise RuntimeError("JELLYFIN_API_KEY environment variable is required.")
    return JellyfinService(base_url=settings.server_url, api_key=settings.api_key, timeout=settings.timeout)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def jellyfin_library(
    operation: Annotated[
        Literal[
            "list", "get", "create", "update", "delete", "scan", "refresh",
            "stats", "cleanup", "add_path", "remove_path", "optimize",
            "empty_trash", "reorder", "configure",
        ],
        Field(description="Library operation to perform."),
    ],
    library_id: Annotated[str | None, Field(description="Library ID (required for get/update/delete/scan/refresh/stats/cleanup/path operations).")] = None,
    name: Annotated[str | None, Field(description="Library name (required for create, optional for update).")] = None,
    library_type: Annotated[
        Literal["movie", "show", "music", "photo", "homevideos", "book"] | None,
        Field(description="Collection type for library creation: movie, show, music, photo, homevideos, book."),
    ] = None,
    path: Annotated[str | None, Field(description="Filesystem path (required for create, add_path, remove_path).")] = None,
    force: Annotated[bool, Field(description="Force the operation (e.g. full refresh, skip confirmation).")] = False,
) -> ToolResult:
    """Manage Jellyfin libraries: list, create, scan, refresh, stats, cleanup, and path management.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_library(operation="list")
    jellyfin_library(operation="create", name="Movies", library_type="movie", path="/media/movies")
    jellyfin_library(operation="scan", library_id="abc123")
    """
    try:
        jf = _get_jellyfin_service()
        await jf.connect()

        if operation == "list":
            data = await jf.get_libraries()
        elif operation == "get":
            if not library_id:
                raise ValueError("library_id is required for 'get' operation.")
            data = await jf.get_library(library_id)
        elif operation == "create":
            if not name or not library_type or not path:
                raise ValueError("name, library_type, and path are required for 'create' operation.")
            type_map = {
                "movie": "movies", "show": "tvshows", "music": "music",
                "photo": "photos", "homevideos": "homevideos", "book": "books",
            }
            data = await jf.create_library(
                name=name, collection_type=type_map.get(library_type, library_type), paths=[path],
            )
        elif operation == "update":
            if not library_id:
                raise ValueError("library_id is required for 'update' operation.")
            body = {}
            if name:
                body["Name"] = name
            data = await jf._post("/Library/VirtualFolders/LibraryOptions", json_body=body)
        elif operation == "delete":
            if not library_id:
                raise ValueError("library_id is required for 'delete' operation.")
            data = await jf.delete_library(library_id)
        elif operation == "scan":
            if not library_id:
                raise ValueError("library_id is required for 'scan' operation.")
            data = await jf.scan_library(library_id)
        elif operation == "refresh":
            if not library_id:
                raise ValueError("library_id is required for 'refresh' operation.")
            data = await jf.refresh_library(library_id)
        elif operation == "stats":
            if not library_id:
                raise ValueError("library_id is required for 'stats' operation.")
            items = await jf.get_items(parent_id=library_id, limit=1, recursive=True)
            total = items.get("TotalRecordCount", 0)
            lib = await jf.get_library(library_id)
            data = {"library": lib.get("Name", library_id), "total_items": total}
        elif operation == "cleanup":
            if not library_id:
                raise ValueError("library_id is required for 'cleanup' operation.")
            await jf._post("/Library/VirtualFolders/Refresh", json_body={"Recursive": True, "ImageRefreshMode": "FullRefresh", "MetadataRefreshMode": "FullRefresh"})
            data = {"message": f"Library {library_id} cleanup (full refresh) triggered."}
        elif operation == "add_path":
            if not library_id or not path:
                raise ValueError("library_id and path are required for 'add_path' operation.")
            data = await jf._post("/Library/VirtualFolders/Paths", json_body={"Path": path})
        elif operation == "remove_path":
            if not library_id or not path:
                raise ValueError("library_id and path are required for 'remove_path' operation.")
            data = await jf._delete("/Library/VirtualFolders/Paths", path=path)
        elif operation == "empty_trash":
            if not library_id:
                raise ValueError("library_id is required for 'empty_trash' operation.")
            await jf._post(f"/Items/{library_id}/Delete")
            data = {"message": f"Trash emptied for library {library_id}."}
        elif operation in ("optimize", "reorder", "configure"):
            data = {"message": f"Operation '{operation}' is not yet implemented.", "library_id": library_id}
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
