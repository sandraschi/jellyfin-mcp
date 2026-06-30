"""Playback control for Jellyfin: sessions, play, pause, stop, seek, volume, subtitles, audio, quality."""

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from ...app import mcp
from ...services.registry import get_jellyfin_service


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def jellyfin_playback(
    operation: Annotated[
        Literal[
            "list_sessions",
            "play",
            "pause",
            "stop",
            "resume",
            "seek",
            "skip_next",
            "skip_prev",
            "set_volume",
            "set_subtitle",
            "set_audio",
            "set_quality",
        ],
        Field(description="Playback operation to perform."),
    ],
    session_id: Annotated[
        str | None, Field(description="Session ID (required for all operations except list_sessions).")
    ] = None,
    item_ids: Annotated[list[str] | None, Field(description="List of item IDs to play (required for 'play').")] = None,
    ticks: Annotated[
        int | None, Field(description="Seek position in ticks (1 tick = 100ns; required for 'seek').")
    ] = None,
    volume: Annotated[
        int | None, Field(description="Volume level 0-100 (required for 'set_volume').", ge=0, le=100)
    ] = None,
    subtitle_index: Annotated[
        int | None, Field(description="Subtitle stream index (required for 'set_subtitle').", ge=-1)
    ] = None,
    audio_index: Annotated[
        int | None, Field(description="Audio stream index (required for 'set_audio').", ge=0)
    ] = None,
    quality: Annotated[str | None, Field(description="Streaming quality preset (required for 'set_quality').")] = None,
    start_index: Annotated[int, Field(description="Index in the item list to start playback from (for 'play').")] = 0,
) -> ToolResult:
    """Control Jellyfin playback: list active sessions, play, pause, stop, seek, set volume/subtitles/audio/quality.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_playback(operation="list_sessions")
    jellyfin_playback(operation="play", session_id="abc", item_ids=["def456"])
    jellyfin_playback(operation="pause", session_id="abc")
    jellyfin_playback(operation="seek", session_id="abc", ticks=6000000000)
    jellyfin_playback(operation="set_volume", session_id="abc", volume=75)
    """
    try:
        jf = await get_jellyfin_service()

        if operation == "list_sessions":
            data = await jf.get_sessions()
        elif operation == "play":
            if not session_id:
                raise ValueError("session_id is required for 'play' operation.")
            if not item_ids:
                raise ValueError("item_ids is required for 'play' operation.")
            data = await jf.send_play_command(session_id, item_ids, start_index=start_index)
        elif operation == "pause":
            if not session_id:
                raise ValueError("session_id is required for 'pause' operation.")
            data = await jf.pause_session(session_id)
        elif operation == "stop":
            if not session_id:
                raise ValueError("session_id is required for 'stop' operation.")
            data = await jf.stop_session(session_id)
        elif operation == "resume":
            if not session_id:
                raise ValueError("session_id is required for 'resume' operation.")
            data = await jf.unpause_session(session_id)
        elif operation == "seek":
            if not session_id:
                raise ValueError("session_id is required for 'seek' operation.")
            if ticks is None:
                raise ValueError("ticks is required for 'seek' operation.")
            data = await jf.seek_session(session_id, ticks)
        elif operation == "skip_next":
            if not session_id:
                raise ValueError("session_id is required for 'skip_next' operation.")
            data = await jf.send_command(session_id, "NextTrack")
        elif operation == "skip_prev":
            if not session_id:
                raise ValueError("session_id is required for 'skip_prev' operation.")
            data = await jf.send_command(session_id, "PreviousTrack")
        elif operation == "set_volume":
            if not session_id:
                raise ValueError("session_id is required for 'set_volume' operation.")
            if volume is None:
                raise ValueError("volume is required for 'set_volume' operation.")
            data = await jf.send_command(session_id, "SetVolume", volume=volume)
        elif operation == "set_subtitle":
            if not session_id:
                raise ValueError("session_id is required for 'set_subtitle' operation.")
            if subtitle_index is None:
                raise ValueError("subtitle_index is required for 'set_subtitle' operation.")
            data = await jf.send_command(session_id, "SetSubtitleStreamIndex", index=subtitle_index)
        elif operation == "set_audio":
            if not session_id:
                raise ValueError("session_id is required for 'set_audio' operation.")
            if audio_index is None:
                raise ValueError("audio_index is required for 'set_audio' operation.")
            data = await jf.send_command(session_id, "SetAudioStreamIndex", index=audio_index)
        elif operation == "set_quality":
            if not session_id:
                raise ValueError("session_id is required for 'set_quality' operation.")
            if not quality:
                raise ValueError("quality is required for 'set_quality' operation.")
            data = await jf.send_command(session_id, "SetMaxStreamingBitrate", bitrate=quality)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
