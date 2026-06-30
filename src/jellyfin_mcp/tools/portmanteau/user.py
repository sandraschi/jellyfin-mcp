"""User management for Jellyfin: list, get, create, update, delete, policy, password, sessions, activity, devices."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def jellyfin_user(
    operation: Annotated[
        Literal[
            "list",
            "get",
            "create",
            "update",
            "delete",
            "policy",
            "password",
            "sessions",
            "activity",
            "devices",
        ],
        Field(description="User operation to perform."),
    ],
    user_id: Annotated[
        str | None, Field(description="User ID (required for get/update/delete/policy/password/sessions/activity).")
    ] = None,
    name: Annotated[str | None, Field(description="Username (required for create, optional for update).")] = None,
    password: Annotated[
        str | None, Field(description="Password (required for create and password operations).")
    ] = None,
    policy: Annotated[
        dict | None,
        Field(description="User policy dict (required for 'policy' operation). See Jellyfin UserPolicy schema."),
    ] = None,
    enabled: Annotated[bool | None, Field(description="Enable or disable the user (for update).")] = None,
) -> ToolResult:
    """Manage Jellyfin users: list, create, update, delete, policy, change password, view sessions and devices.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_user(operation="list")
    jellyfin_user(operation="create", name="alice", password="secret123")
    jellyfin_user(operation="policy", user_id="abc", policy={"IsAdministrator": True})
    jellyfin_user(operation="sessions", user_id="abc")
    jellyfin_user(operation="devices")
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "list":
            data = await jf.get_users()
        elif operation == "get":
            if not user_id:
                raise ValueError("user_id is required for 'get' operation.")
            data = await jf.get_user(user_id)
        elif operation == "create":
            if not name:
                raise ValueError("name is required for 'create' operation.")
            data = await jf.create_user(name=name, password=password)
        elif operation == "update":
            if not user_id:
                raise ValueError("user_id is required for 'update' operation.")
            body = {}
            if name:
                body["Name"] = name
            if enabled is not None:
                await jf._post(f"/Users/{user_id}/Policy", json_body={"IsDisabled": not enabled})
                body["Enabled"] = enabled
            data = await jf._post(f"/Users/{user_id}", json_body=body) if body else await jf.get_user(user_id)
        elif operation == "delete":
            if not user_id:
                raise ValueError("user_id is required for 'delete' operation.")
            data = await jf.delete_user(user_id)
        elif operation == "policy":
            if not user_id:
                raise ValueError("user_id is required for 'policy' operation.")
            if not policy:
                raise ValueError("policy dict is required for 'policy' operation.")
            data = await jf.update_user_policy(user_id, policy)
        elif operation == "password":
            if not user_id:
                raise ValueError("user_id is required for 'password' operation.")
            if not password:
                raise ValueError("password is required for 'password' operation.")
            data = await jf._post(
                f"/Users/{user_id}/Password", json_body={"Id": user_id, "CurrentPw": "", "NewPw": password}
            )
        elif operation == "sessions":
            if not user_id:
                raise ValueError("user_id is required for 'sessions' operation.")
            sessions = await jf.get_sessions()
            data = [s for s in sessions if s.get("UserId") == user_id]
        elif operation == "activity":
            if not user_id:
                raise ValueError("user_id is required for 'activity' operation.")
            sessions = await jf.get_sessions()
            user_sessions = [s for s in sessions if s.get("UserId") == user_id]
            data = {"user_id": user_id, "active_sessions": len(user_sessions), "sessions": user_sessions}
        elif operation == "devices":
            data = await jf.get_devices()
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
