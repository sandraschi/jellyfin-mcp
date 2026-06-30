"""*Arr stack status for Jellyfin: query Radarr, Sonarr, Lidarr HTTP APIs for health and queue data."""

import os
from typing import Annotated, Literal

import httpx
from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp

ARR_SERVICES = {
    "radarr": {"env_url": "RADARR_URL", "default_url": "http://localhost:7878"},
    "sonarr": {"env_url": "SONARR_URL", "default_url": "http://localhost:8989"},
    "lidarr": {"env_url": "LIDARR_URL", "default_url": "http://localhost:8686"},
}


def _get_arr_url(service: str) -> str | None:
    """Get the URL for an *arr service from environment."""
    url = os.getenv(ARR_SERVICES[service]["env_url"], "") or ARR_SERVICES[service]["default_url"]
    test_url = os.getenv(ARR_SERVICES[service]["env_url"], "")
    if not test_url:
        return None
    return url.rstrip("/")


async def _query_arr_api(service: str, endpoint: str, params: dict | None = None) -> dict | None:
    """Query an *arr service API endpoint."""
    url = _get_arr_url(service)
    if not url:
        return None

    api_key = os.getenv("ARR_API_KEY", "")
    headers = {"X-Api-Key": api_key} if api_key else {}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(f"{url}/api/v3/{endpoint}", headers=headers, params=params)
            if resp.status_code == 200:
                return resp.json()
            return {"_error": f"HTTP {resp.status_code}", "_url": url}
    except Exception as e:
        return {"_error": str(e), "_url": url}


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_arr_stack(
    operation: Annotated[
        Literal["status", "queue", "history", "radarr", "sonarr", "lidarr"],
        Field(description="Arr stack operation to perform."),
    ],
    service: Annotated[
        Literal["radarr", "sonarr", "lidarr"] | None,
        Field(description="Target *arr service (required for queue/history, optional for status)."),
    ] = None,
    limit: Annotated[int, Field(description="Max results for queue/history. Default: 20.", ge=1, le=500)] = 20,
) -> ToolResult:
    """Query Radarr, Sonarr, and Lidarr HTTP APIs for media stack health and queue data.

    Configure via env vars: RADARR_URL, SONARR_URL, LIDARR_URL, ARR_API_KEY.
    Only configured services will report in status/list operations.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_arr_stack(operation="status")
    jellyfin_arr_stack(operation="queue", service="radarr")
    jellyfin_arr_stack(operation="history", service="sonarr", limit=50)
    jellyfin_arr_stack(operation="radarr")
    """
    try:
        if operation == "status":
            results = {}
            for svc in ["radarr", "sonarr", "lidarr"]:
                data = await _query_arr_api(svc, "system/status")
                if data is None:
                    results[svc] = {
                        "configured": False,
                        "message": f"Not configured. Set {ARR_SERVICES[svc]['env_url']} env var.",
                    }
                elif "_error" in data:
                    results[svc] = {
                        "configured": True,
                        "reachable": False,
                        "error": data["_error"],
                        "url": data["_url"],
                    }
                else:
                    results[svc] = {
                        "configured": True,
                        "reachable": True,
                        "version": data.get("version", "unknown"),
                        "app_name": data.get("appName", svc),
                    }
            data = results

        elif operation == "queue":
            if not service or service not in ARR_SERVICES:
                raise ValueError("service is required for 'queue' operation. Use 'radarr', 'sonarr', or 'lidarr'.")
            raw = await _query_arr_api(service, "queue", params={"pageSize": limit})
            if raw is None:
                raise ValueError(f"{service} is not configured. Set {ARR_SERVICES[service]['env_url']} env var.")
            if "_error" in raw:
                raise ValueError(f"Failed to query {service}: {raw['_error']}")
            items = raw if isinstance(raw, list) else raw.get("records", raw.get("items", []))
            data = {service: {"queue_count": len(items), "items": items}}

        elif operation == "history":
            if not service or service not in ARR_SERVICES:
                raise ValueError("service is required for 'history' operation. Use 'radarr', 'sonarr', or 'lidarr'.")
            raw = await _query_arr_api(service, "history", params={"pageSize": limit})
            if raw is None:
                raise ValueError(f"{service} is not configured. Set {ARR_SERVICES[service]['env_url']} env var.")
            if "_error" in raw:
                raise ValueError(f"Failed to query {service}: {raw['_error']}")
            items = raw if isinstance(raw, list) else raw.get("records", raw.get("items", []))
            data = {service: {"history_count": len(items), "items": items}}

        elif operation in ("radarr", "sonarr", "lidarr"):
            raw = await _query_arr_api(operation, "system/status")
            if raw is None:
                data = {
                    operation: {"configured": False, "message": f"Set {ARR_SERVICES[operation]['env_url']} env var."}
                }
            elif "_error" in raw:
                data = {operation: {"configured": True, "reachable": False, "error": raw["_error"], "url": raw["_url"]}}
            else:
                health = await _query_arr_api(operation, "health")
                queue = await _query_arr_api(operation, "queue", params={"pageSize": 1})
                data = {
                    operation: {
                        "configured": True,
                        "reachable": True,
                        "version": raw.get("version", "unknown"),
                        "app_name": raw.get("appName", operation),
                        "health": health if health and "_error" not in health else None,
                        "pending": len(queue)
                        if isinstance(queue, list)
                        else queue.get("totalRecords", 0)
                        if isinstance(queue, dict)
                        else 0,
                    }
                }

        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
