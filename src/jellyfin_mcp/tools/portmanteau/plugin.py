"""Plugin management for Jellyfin: catalog, list, install, uninstall, enable, disable, configure, update."""

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
async def jellyfin_plugin(
    operation: Annotated[
        Literal["catalog", "list", "install", "uninstall", "enable", "disable", "configure", "update"],
        Field(description="Plugin operation to perform."),
    ],
    plugin_id: Annotated[str | None, Field(description="Plugin ID (required for install/uninstall/enable/disable/configure/update).")] = None,
    version: Annotated[str | None, Field(description="Plugin version for install/update operations. Default: 'latest'.")] = None,
    config: Annotated[dict[str, Any] | None, Field(description="Plugin configuration dict (required for configure).")] = None,
) -> ToolResult:
    """Manage Jellyfin plugins: browse catalog, list installed, install, uninstall, enable, disable, configure, and update.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_plugin(operation="catalog")
    jellyfin_plugin(operation="list")
    jellyfin_plugin(operation="install", plugin_id="intro-skipper")
    jellyfin_plugin(operation="configure", plugin_id="intro-skipper", config={"enabled": True})
    """
    try:
        jf = _get_jellyfin_service()
        await jf.connect()

        from ...services.plugin_service import PluginService

        plugin_service = PluginService(jf)

        if operation == "catalog":
            data = await plugin_service.get_catalog()
        elif operation == "list":
            data = await plugin_service.get_installed()
        elif operation == "install":
            if not plugin_id:
                raise ValueError("plugin_id is required for 'install' operation.")
            data = await plugin_service.install(plugin_id, version=version or "latest")
        elif operation == "uninstall":
            if not plugin_id:
                raise ValueError("plugin_id is required for 'uninstall' operation.")
            data = await plugin_service.uninstall(plugin_id)
        elif operation == "enable":
            if not plugin_id:
                raise ValueError("plugin_id is required for 'enable' operation.")
            data = await plugin_service.enable(plugin_id)
        elif operation == "disable":
            if not plugin_id:
                raise ValueError("plugin_id is required for 'disable' operation.")
            data = await plugin_service.disable(plugin_id)
        elif operation == "configure":
            if not plugin_id:
                raise ValueError("plugin_id is required for 'configure' operation.")
            if not config:
                raise ValueError("config is required for 'configure' operation.")
            data = await plugin_service.configure(plugin_id, config)
        elif operation == "update":
            if not plugin_id:
                raise ValueError("plugin_id is required for 'update' operation.")
            data = await plugin_service.install(plugin_id, version=version or "latest")
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
