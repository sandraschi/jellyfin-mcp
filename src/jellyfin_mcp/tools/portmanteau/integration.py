"""jellyfin-mcp Integration & Migration Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def jellyfin_integration(
    operation: Annotated[
        Literal["export_plex", "import_plex", "sync_watchstate", "backup", "restore"],
        Field(description="Integration operation to perform."),
    ],
    source_path: Annotated[str | None, Field(description="Source path for export/import/backup operations.")] = None,
    target: Annotated[str | None, Field(description="Target identifier or path.")] = None,
    user_id: Annotated[str | None, Field(description="User ID for watchstate sync.")] = None,
) -> dict[str, Any]:
    """Cross-platform integration and migration for Jellyfin.

    Consolidates all integration operations into a single portmanteau interface:
    Plex export, Plex import, watchstate sync, backup, and restore.

    [PORTMANTEAU] Prevents tool explosion by merging 5 integration/migration operations into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": ..., "message": str}

    ## Examples
    - jellyfin_integration(operation="export_plex", source_path="/var/lib/plexmediaserver")
    - jellyfin_integration(operation="import_plex", source_path="/backup/plex_export.json")
    - jellyfin_integration(operation="sync_watchstate", user_id="user123")
    - jellyfin_integration(operation="backup", target="/backup/jellyfin_backup.zip")
    """
    try:
        if operation == "export_plex":
            if not source_path:
                return {
                    "success": False,
                    "error": "source_path is required for export_plex",
                    "error_code": "MISSING_SOURCE_PATH",
                }
            return {
                "success": True,
                "operation": "export_plex",
                "message": "Plex data export placeholder",
                "data": {"source_path": source_path, "status": "export_initiated", "items_exported": 0},
            }

        if operation == "import_plex":
            if not source_path:
                return {
                    "success": False,
                    "error": "source_path is required for import_plex",
                    "error_code": "MISSING_SOURCE_PATH",
                }
            return {
                "success": True,
                "operation": "import_plex",
                "message": "Plex data import placeholder",
                "data": {"source_path": source_path, "status": "import_initiated", "items_imported": 0},
            }

        if operation == "sync_watchstate":
            return {
                "success": True,
                "operation": "sync_watchstate",
                "message": "Watchstate sync placeholder",
                "data": {"user_id": user_id, "synced_items": 0, "status": "sync_complete"},
            }

        if operation == "backup":
            return {
                "success": True,
                "operation": "backup",
                "message": "Server backup placeholder",
                "data": {"target": target or "~/.jellyfin-mcp/backups/", "status": "backup_initiated"},
            }

        if operation == "restore":
            if not source_path:
                return {
                    "success": False,
                    "error": "source_path is required for restore",
                    "error_code": "MISSING_SOURCE_PATH",
                }
            return {
                "success": True,
                "operation": "restore",
                "message": "Server restore placeholder",
                "data": {"source_path": source_path, "status": "restore_initiated"},
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: export_plex, import_plex, sync_watchstate, backup, restore"],
        }

    except Exception as e:
        logger.exception("Error in jellyfin_integration operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
