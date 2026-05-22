"""jellyfin-mcp Live TV / DVR Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def jellyfin_livetv(
    operation: Annotated[
        Literal["channels", "guide", "recordings", "schedule", "tuners", "epg_refresh", "delete_recording", "manage"],
        Field(description="Live TV operation to perform."),
    ],
    channel_id: Annotated[str | None, Field(description="Channel ID.")] = None,
    program_id: Annotated[str | None, Field(description="Program / show ID.")] = None,
    recording_id: Annotated[str | None, Field(description="Recording ID.")] = None,
    start_time: Annotated[str | None, Field(description="ISO 8601 start time for schedule query.")] = None,
    end_time: Annotated[str | None, Field(description="ISO 8601 end time for schedule query.")] = None,
) -> dict[str, Any]:
    """Live TV and DVR management for Jellyfin.

    Consolidates all Live TV / DVR operations into a single portmanteau interface:
    channels, guide (EPG), recordings, schedule, tuners, EPG refresh, delete recording, and manage.

    [PORTMANTEAU] Prevents tool explosion by merging 8 related operations into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": [...], "count": int, "message": str}

    ## Examples
    - jellyfin_livetv(operation="channels")
    - jellyfin_livetv(operation="guide", start_time="2025-01-01T00:00:00Z", end_time="2025-01-02T00:00:00Z")
    - jellyfin_livetv(operation="recordings")
    - jellyfin_livetv(operation="schedule", program_id="abc123")
    - jellyfin_livetv(operation="delete_recording", recording_id="rec123")
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "channels":
            data = await jf.get_channels()
            items = data.get("Items", data if isinstance(data, list) else [])
            return {
                "success": True,
                "operation": "channels",
                "message": "Live TV channels",
                "data": items,
                "count": len(items),
            }

        if operation == "guide":
            epg = await jf.get_epg(channel_id=channel_id)
            items = epg.get("Items", epg if isinstance(epg, list) else [])
            return {
                "success": True,
                "operation": "guide",
                "message": "EPG guide data",
                "data": {"start_time": start_time, "end_time": end_time, "entries": items},
                "count": len(items),
            }

        if operation == "recordings":
            data = await jf.get_recordings()
            items = data.get("Items", data if isinstance(data, list) else [])
            return {
                "success": True,
                "operation": "recordings",
                "message": "DVR recordings list",
                "data": items,
                "count": len(items),
            }

        if operation == "schedule":
            if not program_id:
                return {"success": False, "error": "program_id is required for schedule", "error_code": "MISSING_PROGRAM_ID"}
            result = await jf.create_recording(program_id)
            return {
                "success": True,
                "operation": "schedule",
                "message": "Recording scheduled",
                "data": result,
            }

        if operation == "tuners":
            info = await jf._get("/LiveTv/Info")
            items = info.get("TunerHosts", info.get("Services", []))
            if not isinstance(items, list):
                items = []
            return {
                "success": True,
                "operation": "tuners",
                "message": "Available tuners",
                "data": items,
                "count": len(items),
            }

        if operation == "epg_refresh":
            await jf._post("/LiveTv/GuideInfo")
            return {
                "success": True,
                "operation": "epg_refresh",
                "message": "EPG data refresh initiated",
                "data": {"status": "refresh_initiated"},
            }

        if operation == "delete_recording":
            if not recording_id:
                return {"success": False, "error": "recording_id is required", "error_code": "MISSING_RECORDING_ID"}
            await jf._delete(f"/LiveTv/Recordings/{recording_id}")
            return {
                "success": True,
                "operation": "delete_recording",
                "message": "Recording deleted",
                "data": {"recording_id": recording_id, "deleted": True},
            }

        if operation == "manage":
            channels = await jf.get_channels()
            recordings = await jf.get_recordings()
            channel_items = channels.get("Items", channels if isinstance(channels, list) else [])
            recording_items = recordings.get("Items", recordings if isinstance(recordings, list) else [])
            try:
                info = await jf._get("/LiveTv/Info")
                tuner_items = info.get("TunerHosts", info.get("Services", []))
                if not isinstance(tuner_items, list):
                    tuner_items = []
            except Exception:
                tuner_items = []
            return {
                "success": True,
                "operation": "manage",
                "message": "Live TV management overview",
                "data": {
                    "channels": len(channel_items),
                    "tuners": len(tuner_items),
                    "recordings": len(recording_items),
                    "status": "operational",
                },
            }

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: channels, guide, recordings, schedule, tuners, epg_refresh, delete_recording, manage"],
        }

    except Exception as e:
        logger.exception("Error in jellyfin_livetv operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
