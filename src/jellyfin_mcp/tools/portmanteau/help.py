"""jellyfin-mcp Help & Discovery Portmanteau Tool."""

from typing import Annotated, Any, Literal

from pydantic import Field

from ...app import mcp
from ...utils import get_logger

logger = get_logger(__name__)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_help(
    operation: Annotated[
        Literal["discover", "tool_help", "status", "tips", "quickstart", "faq"],
        Field(description="Help operation to perform."),
    ],
    tool_name: Annotated[str | None, Field(description="Specific tool name for tool_help operation.")] = None,
    topic: Annotated[str | None, Field(description="Topic to filter help content.")] = None,
) -> dict[str, Any]:
    """Help, discovery, and user guide for jellyfin-mcp.

    Consolidates all help and discovery operations into a single interface:
    tool discovery, per-tool help, server status, usage tips, quickstart guide, and FAQ.

    [PORTMANTEAU] Prevents tool explosion by merging 6 help operations into one tool.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}, "message": str}

    ## Examples
    - jellyfin_help(operation="discover")
    - jellyfin_help(operation="tool_help", tool_name="jellyfin_rag")
    - jellyfin_help(operation="quickstart")
    - jellyfin_help(operation="faq", topic="transcoding")
    """
    try:
        _tools_catalog = {
            "jellyfin_library": {"operations": ["list", "get", "create", "update", "delete", "scan", "refresh", "stats", "cleanup", "add_path", "remove_path", "optimize", "empty_trash", "reorder", "configure"], "category": "library"},
            "jellyfin_media": {"operations": ["browse", "search", "get", "get_recent", "get_recommended", "similar", "stream_info", "refresh", "update", "delete"], "category": "media"},
            "jellyfin_search": {"operations": ["search", "advanced", "people", "studios", "suggest", "saved"], "category": "search"},
            "jellyfin_playback": {"operations": ["list_sessions", "play", "pause", "stop", "resume", "seek", "skip_next", "skip_prev", "set_volume", "set_subtitle", "set_audio", "set_quality"], "category": "playback"},
            "jellyfin_user": {"operations": ["list", "get", "create", "update", "delete", "policy", "password", "sessions", "activity", "devices"], "category": "user"},
            "jellyfin_playlist": {"operations": ["list", "get", "create", "update", "delete", "add_items", "remove_items", "reorder", "share"], "category": "playlist"},
            "jellyfin_collections": {"operations": ["list", "get", "create", "update", "delete", "add_items", "remove_items"], "category": "collections"},
            "jellyfin_metadata": {"operations": ["get", "update", "refresh", "identify", "images", "backdrops", "providers", "lock", "unlock", "fetch"], "category": "metadata"},
            "jellyfin_server": {"operations": ["status", "info", "health", "logs", "restart", "shutdown", "updates", "tasks", "task_run", "transcode_queue"], "category": "server"},
            "jellyfin_streaming": {"operations": ["sessions", "clients", "transcode", "bandwidth", "direct_play", "remote", "lan", "kill"], "category": "streaming"},
            "jellyfin_plugin": {"operations": ["catalog", "list", "install", "uninstall", "enable", "disable", "configure", "update"], "category": "plugin"},
            "jellyfin_arr_stack": {"operations": ["status", "queue", "history", "radarr", "sonarr", "lidarr"], "category": "integration"},
            "jellyfin_subtitle": {"operations": ["search", "download", "upload", "delete", "sync", "offset", "provider_config"], "category": "subtitle"},
            "jellyfin_livetv": {"operations": ["channels", "guide", "recordings", "schedule", "tuners", "epg_refresh", "delete_recording", "manage"], "category": "livetv"},
            "jellyfin_ffmpeg": {"operations": ["profiles", "performance", "detect_hw", "path", "test", "benchmarks"], "category": "transcoding"},
            "jellyfin_enrichment": {"operations": ["tmdb", "wikipedia", "musicbrainz", "omdb", "tvdb", "batch"], "category": "metadata"},
            "jellyfin_rag": {"operations": ["sync", "search", "status", "reindex", "purge"], "category": "search"},
            "jellyfin_reporting": {"operations": ["stats", "popular", "recent", "genres", "resolution", "codec", "user_activity", "export"], "category": "reporting"},
            "jellyfin_recommend": {"operations": ["similar", "genre", "director", "actor", "history"], "category": "recommendation"},
            "jellyfin_integration": {"operations": ["export_plex", "import_plex", "sync_watchstate", "backup", "restore"], "category": "integration"},
            "jellyfin_agentic": {"operations": ["workflow", "natural_query", "batch"], "category": "agentic"},
        }

        if operation == "discover":
            catalog = [{"name": k, "category": v["category"], "operations": v["operations"]} for k, v in _tools_catalog.items()]
            if topic:
                catalog = [t for t in catalog if t["category"] == topic]
            return {
                "success": True,
                "operation": "discover",
                "message": f"Discovered {len(catalog)} tools",
                "data": catalog,
                "count": len(catalog),
            }

        if operation == "tool_help":
            if not tool_name:
                return {"success": False, "error": "tool_name is required for tool_help", "error_code": "MISSING_TOOL_NAME"}
            tool = _tools_catalog.get(tool_name)
            if not tool:
                return {"success": False, "error": f"Tool '{tool_name}' not found", "error_code": "TOOL_NOT_FOUND",
                        "suggestions": ["Use operation='discover' to list all tools"]}
            return {
                "success": True,
                "operation": "tool_help",
                "message": f"Help for {tool_name}",
                "data": {"name": tool_name, "category": tool["category"], "operations": tool["operations"]},
            }

        if operation == "status":
            return {
                "success": True,
                "operation": "status",
                "message": "jellyfin-mcp server status",
                "data": {"server": "jellyfin-mcp", "version": "0.1.0", "transport": "stdio", "tools_registered": len(_tools_catalog)},
            }

        if operation == "tips":
            return {
                "success": True,
                "operation": "tips",
                "message": "Usage tips for jellyfin-mcp",
                "data": {
                    "tips": [
                        "Run jellyfin_rag(operation='sync') before semantic search",
                        "Use jellyfin_help(operation='discover') to see all available tools",
                        "Check jellyfin_server(operation='status') before troubleshooting",
                    ],
                },
            }

        if operation == "quickstart":
            return {
                "success": True,
                "operation": "quickstart",
                "message": "Quickstart guide",
                "data": {
                    "steps": [
                        "1. jellyfin_library(operation='list') — list libraries",
                        "2. jellyfin_media(operation='browse', library_id='...') — browse content",
                        "3. jellyfin_search(operation='search', query='...') — search",
                        "4. jellyfin_rag(operation='sync') then jellyfin_rag(operation='search', query='...') — semantic search",
                        "5. jellyfin_help(operation='discover') — all tools",
                    ],
                },
            }

        if operation == "faq":
            faqs = {
                "transcoding": "Jellyfin supports hardware transcoding for free (VAAPI, NVENC, QSV, VideoToolbox, AMF).",
                "plugins": "Use jellyfin_plugin(operation='catalog') then jellyfin_plugin(operation='install', plugin_id='...').",
                "rag": "Run jellyfin_rag(operation='sync') to index metadata, then jellyfin_rag(operation='search', query='...').",
            }
            if topic and topic in faqs:
                return {"success": True, "operation": "faq", "message": f"FAQ: {topic}", "data": {"topic": topic, "answer": faqs[topic]}}
            return {"success": True, "operation": "faq", "message": "Frequently asked questions", "data": {"faqs": faqs, "topic": topic}}

        return {
            "success": False,
            "error": f"Unknown operation: {operation}",
            "error_code": "INVALID_OPERATION",
            "suggestions": ["Valid operations: discover, tool_help, status, tips, quickstart, faq"],
        }

    except Exception as e:
        logger.exception("Error in jellyfin_help operation '%s':", operation)
        return {"success": False, "error": str(e), "error_code": "EXECUTION_ERROR", "operation": operation}
