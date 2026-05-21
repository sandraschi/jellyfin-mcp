"""Metadata management for Jellyfin: get, update, refresh, identify, images, backdrops, providers, lock, unlock, fetch."""

from typing import Annotated, Any, Literal

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
async def jellyfin_metadata(
    operation: Annotated[
        Literal[
            "get", "update", "refresh", "identify",
            "images", "backdrops", "providers",
            "lock", "unlock", "fetch",
        ],
        Field(description="Metadata operation to perform."),
    ],
    item_id: Annotated[str | None, Field(description="Item ID (required for most operations).")] = None,
    metadata: Annotated[dict[str, Any] | None, Field(description="Metadata fields to update (required for update/identify).")] = None,
    image_type: Annotated[
        Literal["Primary", "Backdrop", "Logo", "Thumb", "Banner", "Disc", "Box", "Screenshot", "Menu"] | None,
        Field(description="Image type for image-related operations."),
    ] = None,
    provider_id: Annotated[str | None, Field(description="Metadata provider ID (required for fetch/providers).")] = None,
    search_name: Annotated[str | None, Field(description="Search name for identify/fetch operations.")] = None,
    year: Annotated[int | None, Field(description="Year for identify/fetch operations.")] = None,
) -> ToolResult:
    """Manage Jellyfin item metadata: get, update, refresh, identify, images, backdrops, providers, lock/unlock, and fetch.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_metadata(operation="get", item_id="abc123")
    jellyfin_metadata(operation="update", item_id="abc123", metadata={"Name": "New Title"})
    jellyfin_metadata(operation="refresh", item_id="abc123")
    jellyfin_metadata(operation="images", item_id="abc123", image_type="Primary")
    jellyfin_metadata(operation="fetch", item_id="abc123", provider_id="Tvdb", search_name="The Show", year=2024)
    """
    try:
        jf = _get_jellyfin_service()
        await jf.connect()

        if operation == "get":
            if not item_id:
                raise ValueError("item_id is required for 'get' operation.")
            data = await jf._get(f"/Items/{item_id}")
        elif operation == "update":
            if not item_id:
                raise ValueError("item_id is required for 'update' operation.")
            if not metadata:
                raise ValueError("metadata is required for 'update' operation.")
            data = await jf.update_item(item_id=item_id, metadata=metadata)
        elif operation == "refresh":
            if not item_id:
                raise ValueError("item_id is required for 'refresh' operation.")
            data = await jf._post(f"/Items/{item_id}/Refresh", json_body={"Recursive": True, "MetadataRefreshMode": "FullRefresh"})
        elif operation == "identify":
            if not item_id:
                raise ValueError("item_id is required for 'identify' operation.")
            body = {}
            if search_name:
                body["SearchName"] = search_name
            if year:
                body["Year"] = year
            if provider_id:
                body["ProviderIds"] = {provider_id: search_name or ""}
            if metadata:
                body.update(metadata)
            data = await jf._post(f"/Items/{item_id}/RemoteSearch/Apply", json_body=body or {"SearchName": search_name or ""})
        elif operation == "images":
            if not item_id:
                raise ValueError("item_id is required for 'images' operation.")
            img_type = image_type or "Primary"
            data = await jf._get(f"/Items/{item_id}/Images", IncludeItemTypes=img_type)
        elif operation == "backdrops":
            if not item_id:
                raise ValueError("item_id is required for 'backdrops' operation.")
            data = await jf._get(f"/Items/{item_id}/Images", IncludeItemTypes="Backdrop")
        elif operation == "providers":
            if not item_id:
                raise ValueError("item_id is required for 'providers' operation.")
            data = await jf._get(f"/Items/{item_id}/RemoteSearch")
        elif operation == "lock":
            if not item_id:
                raise ValueError("item_id is required for 'lock' operation.")
            data = await jf._post(f"/Items/{item_id}/Lock", json_body={})
        elif operation == "unlock":
            if not item_id:
                raise ValueError("item_id is required for 'unlock' operation.")
            data = await jf._post(f"/Items/{item_id}/Unlock", json_body={})
        elif operation == "fetch":
            if not item_id:
                raise ValueError("item_id is required for 'fetch' operation.")
            if not search_name:
                raise ValueError("search_name is required for 'fetch' operation.")
            body = {
                "SearchInfo": {
                    "Name": search_name,
                    "Year": year,
                    "ProviderIds": {provider_id: search_name} if provider_id else {},
                },
            }
            data = await jf._post(f"/Items/{item_id}/RemoteSearch/Metadata", json_body=body)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
