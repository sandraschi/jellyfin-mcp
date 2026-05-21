"""Server management for Jellyfin: status, info, health, logs, restart, shutdown, updates, tasks, task_run, transcode_queue."""

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


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_server(
    operation: Annotated[
        Literal[
            "status", "info", "health", "logs",
            "restart", "shutdown", "updates",
            "tasks", "task_run", "transcode_queue",
        ],
        Field(description="Server operation to perform."),
    ],
    task_id: Annotated[str | None, Field(description="Task ID (required for task_run).")] = None,
    lines: Annotated[int, Field(description="Number of log lines to return. Default: 100.", ge=1, le=1000)] = 100,
) -> ToolResult:
    """Query and manage Jellyfin server: status, info, health, logs, restart, shutdown, updates, scheduled tasks, and transcode queue.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_server(operation="status")
    jellyfin_server(operation="logs", lines=50)
    jellyfin_server(operation="tasks")
    jellyfin_server(operation="task_run", task_id="abc123")
    jellyfin_server(operation="transcode_queue")
    """
    try:
        jf = _get_jellyfin_service()
        await jf.connect()

        if operation == "status":
            data = await jf.get_server_status()
        elif operation == "info":
            data = await jf.get_server_info()
        elif operation == "health":
            info = await jf.get_server_info()
            data = {
                "version": info.get("Version"),
                "os": info.get("OperatingSystem"),
                "id": info.get("Id"),
                "healthy": True,
                "product_name": info.get("ProductName"),
                "startup_wizard_completed": info.get("StartupWizardCompleted"),
            }
        elif operation == "logs":
            data = await jf._get("/System/Logs/Log", limit=lines)
        elif operation == "restart":
            data = await jf._post("/System/Restart", json_body={})
        elif operation == "shutdown":
            data = await jf._post("/System/Shutdown", json_body={})
        elif operation == "updates":
            data = await jf._get("/System/Configuration")
        elif operation == "tasks":
            data = await jf.get_scheduled_tasks()
        elif operation == "task_run":
            if not task_id:
                raise ValueError("task_id is required for 'task_run' operation.")
            data = await jf.run_task(task_id)
        elif operation == "transcode_queue":
            data = await jf._get("/System/Transcoding")
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
