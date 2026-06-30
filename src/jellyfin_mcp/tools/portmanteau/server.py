"""Server management for Jellyfin: status, info, health, logs, restart, shutdown, updates, tasks, task_run, transcode_queue."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_server(
    operation: Annotated[
        Literal[
            "status",
            "info",
            "health",
            "logs",
            "restart",
            "shutdown",
            "updates",
            "tasks",
            "task_run",
            "transcode_queue",
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
        jf = await get_jellyfin_service()

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
            # Returns list of available log files; Jellyfin serves individual logs by filename
            data = await jf._get("/System/Logs")
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
            # Active transcodes appear as sessions with TranscodingInfo populated
            sessions = await jf.get_sessions()
            data = [
                {
                    "session_id": s.get("Id"),
                    "user": s.get("UserName", ""),
                    "item": s.get("NowPlayingItem", {}).get("Name", ""),
                    "transcode_info": s.get("TranscodingInfo"),
                }
                for s in (sessions if isinstance(sessions, list) else [])
                if s.get("TranscodingInfo")
            ]
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
