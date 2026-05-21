"""Streaming and session monitoring for Jellyfin: sessions, clients, transcode, bandwidth, direct_play, remote, lan, kill."""

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
async def jellyfin_streaming(
    operation: Annotated[
        Literal[
            "sessions", "clients", "transcode",
            "bandwidth", "direct_play", "remote",
            "lan", "kill",
        ],
        Field(description="Streaming operation to perform."),
    ],
    session_id: Annotated[str | None, Field(description="Session ID (required for kill).")] = None,
) -> ToolResult:
    """Monitor and control Jellyfin streaming: active sessions, clients, transcoding, bandwidth, direct play stats, remote vs LAN, and session termination.

    ## Return Format
    {"success": bool, "data": ..., "operation": str}

    ## Examples
    jellyfin_streaming(operation="sessions")
    jellyfin_streaming(operation="transcode")
    jellyfin_streaming(operation="kill", session_id="sess123")
    """
    try:
        jf = _get_jellyfin_service()
        await jf.connect()

        if operation == "sessions":
            data = await jf.get_sessions()
        elif operation == "clients":
            sessions = await jf.get_sessions()
            clients = []
            seen = set()
            for s in (sessions if isinstance(sessions, list) else []):
                client = s.get("Client", "") or s.get("DeviceName", "")
                device_id = s.get("DeviceId", "")
                if device_id and device_id not in seen:
                    seen.add(device_id)
                    clients.append({
                        "device_id": device_id,
                        "client": client,
                        "device_name": s.get("DeviceName", ""),
                        "app_version": s.get("ApplicationVersion", ""),
                        "user_name": s.get("UserName", ""),
                        "play_state": s.get("PlayState", {}).get("PositionTicks", 0) > 0,
                    })
            data = clients
        elif operation == "transcode":
            sessions = await jf.get_sessions()
            transcoding = []
            for s in (sessions if isinstance(sessions, list) else []):
                if s.get("TranscodingInfo"):
                    transcoding.append({
                        "session_id": s.get("Id"),
                        "user": s.get("UserName", ""),
                        "item": s.get("NowPlayingItem", {}).get("Name", ""),
                        "transcode_info": s.get("TranscodingInfo"),
                        "play_state": s.get("PlayState", {}),
                    })
            data = transcoding
        elif operation == "bandwidth":
            sessions = await jf.get_sessions()
            total_bitrate = 0
            details = []
            for s in (sessions if isinstance(sessions, list) else []):
                info = s.get("TranscodingInfo", {}) or {}
                bitrate = info.get("Bitrate", 0)
                total_bitrate += bitrate
                if bitrate or s.get("PlayState", {}).get("IsPaused") is False:
                    details.append({
                        "session_id": s.get("Id"),
                        "user": s.get("UserName", ""),
                        "bitrate_bps": bitrate,
                        "bitrate_mbps": round(bitrate / 1_000_000, 2) if bitrate else 0,
                    })
            data = {"total_bitrate_bps": total_bitrate, "total_bitrate_mbps": round(total_bitrate / 1_000_000, 2), "sessions": details}
        elif operation == "direct_play":
            sessions = await jf.get_sessions()
            direct = []
            for s in (sessions if isinstance(sessions, list) else []):
                info = s.get("TranscodingInfo", {}) or {}
                if s.get("PlayState", {}).get("PlayMethod") == "DirectPlay":
                    direct.append({
                        "session_id": s.get("Id"),
                        "user": s.get("UserName", ""),
                        "item": s.get("NowPlayingItem", {}).get("Name", ""),
                        "media_type": s.get("NowPlayingItem", {}).get("Type", ""),
                    })
            data = {"direct_play_count": len(direct), "sessions": direct}
        elif operation == "remote":
            sessions = await jf.get_sessions()
            remote = []
            for s in (sessions if isinstance(sessions, list) else []):
                if s.get("RemoteEndPoint"):
                    remote.append({
                        "session_id": s.get("Id"),
                        "user": s.get("UserName", ""),
                        "remote_endpoint": s.get("RemoteEndPoint", ""),
                        "client": s.get("Client", ""),
                    })
            data = {"remote_count": len(remote), "sessions": remote}
        elif operation == "lan":
            sessions = await jf.get_sessions()
            lan = []
            for s in (sessions if isinstance(sessions, list) else []):
                if not s.get("RemoteEndPoint"):
                    lan.append({
                        "session_id": s.get("Id"),
                        "user": s.get("UserName", ""),
                        "device": s.get("DeviceName", ""),
                    })
            data = {"lan_count": len(lan), "sessions": lan}
        elif operation == "kill":
            if not session_id:
                raise ValueError("session_id is required for 'kill' operation.")
            data = await jf.stop_session(session_id)
        else:
            raise ValueError(f"Unknown operation: {operation}")

        return ToolResult(content={"success": True, "data": data, "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e), "operation": operation})
