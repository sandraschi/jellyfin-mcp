"""Collections management for Jellyfin: list, get, create, update, delete, add_items, remove_items."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def jellyfin_collections(
    operation: Annotated[
        Literal["list", "get", "create", "update", "delete", "add_items", "remove_items"],
        Field(description="Collections operation to perform."),
    ],
    collection_id: Annotated[str | None, Field(description="Collection ID (required for get/update/delete/add_items/remove_items).")] = None,
    name: Annotated[str | None, Field(description="Collection name (required for create, optional for update).")] = None,
    item_ids: Annotated[list[str] | None, Field(description="List of item IDs (required for create/add_items/remove_items).")] = None,
    user_id: Annotated[str | None, Field(description="User ID for user-scoped collection operations.")] = None,
) -> ToolResult:
    """Manage Jellyfin collections: list, get, create, update, delete, and add/remove items.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_collections(operation="list", user_id="abc123")
    jellyfin_collections(operation="create", name="Marvel Universe", item_ids=["1", "2"])
    jellyfin_collections(operation="add_items", collection_id="col123", item_ids=["3"])
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "list":
            uid = user_id or await jf.get_default_user_id()
            data = await jf.get_collections(uid)
        elif operation == "get":
            if not collection_id:
                raise ValueError("collection_id is required for 'get' operation.")
            data = await jf._get(f"/Collections/{collection_id}")
        elif operation == "create":
            if not name:
                raise ValueError("name is required for 'create' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'create' operation.")
            data = await jf.create_collection(name=name, item_ids=item_ids)
        elif operation == "update":
            if not collection_id:
                raise ValueError("collection_id is required for 'update' operation.")
            body = {}
            if name:
                body["Name"] = name
            data = await jf._post(f"/Collections/{collection_id}", json_body=body)
        elif operation == "delete":
            if not collection_id:
                raise ValueError("collection_id is required for 'delete' operation.")
            data = await jf.delete_collection(collection_id)
        elif operation == "add_items":
            if not collection_id:
                raise ValueError("collection_id is required for 'add_items' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'add_items' operation.")
            data = await jf._post(f"/Collections/{collection_id}/Items", json_body={"Ids": item_ids})
        elif operation == "remove_items":
            if not collection_id:
                raise ValueError("collection_id is required for 'remove_items' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'remove_items' operation.")
            ids_param = ",".join(item_ids)
            data = await jf._delete(f"/Collections/{collection_id}/Items", ids=ids_param)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
