"""Playlist management for Jellyfin: list, get, create, update, delete, add_items, remove_items, reorder, share."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def jellyfin_playlist(
    operation: Annotated[
        Literal[
            "list",
            "get",
            "create",
            "update",
            "delete",
            "add_items",
            "remove_items",
            "reorder",
            "share",
        ],
        Field(description="Playlist operation to perform."),
    ],
    playlist_id: Annotated[
        str | None,
        Field(description="Playlist ID (required for get/update/delete/add_items/remove_items/reorder/share)."),
    ] = None,
    name: Annotated[str | None, Field(description="Playlist name (required for create, optional for update).")] = None,
    item_ids: Annotated[
        list[str] | None, Field(description="List of item IDs (required for create/add_items/remove_items).")
    ] = None,
    user_id: Annotated[
        str | None, Field(description="User ID of the playlist owner (required for create and most operations).")
    ] = None,
    items: Annotated[list[str] | None, Field(description="Reordered list of item IDs for reorder operation.")] = None,
) -> ToolResult:
    """Manage Jellyfin playlists: list, get, create, update, delete, add/remove items, reorder, and share.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_playlist(operation="list", user_id="abc123")
    jellyfin_playlist(operation="create", name="Favorites", item_ids=["1", "2"], user_id="abc123")
    jellyfin_playlist(operation="add_items", playlist_id="pl123", item_ids=["3"], user_id="abc123")
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "list":
            if not user_id:
                raise ValueError("user_id is required for 'list' operation.")
            data = await jf.get_playlists(user_id)
        elif operation == "get":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'get' operation.")
            data = await jf._get(f"/Playlists/{playlist_id}")
        elif operation == "create":
            if not name:
                raise ValueError("name is required for 'create' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'create' operation.")
            if not user_id:
                raise ValueError("user_id is required for 'create' operation.")
            data = await jf.create_playlist(name=name, item_ids=item_ids, user_id=user_id)
        elif operation == "update":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'update' operation.")
            body = {}
            if name:
                body["Name"] = name
            data = await jf._post(f"/Playlists/{playlist_id}", json_body=body)
        elif operation == "delete":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'delete' operation.")
            data = await jf.delete_playlist(playlist_id)
        elif operation == "add_items":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'add_items' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'add_items' operation.")
            if not user_id:
                raise ValueError("user_id is required for 'add_items' operation.")
            data = await jf.add_to_playlist(playlist_id=playlist_id, item_ids=item_ids, user_id=user_id)
        elif operation == "remove_items":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'remove_items' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'remove_items' operation.")
            data = await jf.remove_from_playlist(playlist_id=playlist_id, item_ids=item_ids)
        elif operation == "reorder":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'reorder' operation.")
            if not items:
                raise ValueError("items is required for 'reorder' operation (ordered list of item IDs).")
            data = await jf._post(f"/Playlists/{playlist_id}/Items/Order", json_body={"Ids": items})
        elif operation == "share":
            if not playlist_id:
                raise ValueError("playlist_id is required for 'share' operation.")
            data = await jf._get(f"/Playlists/{playlist_id}/Share")
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
