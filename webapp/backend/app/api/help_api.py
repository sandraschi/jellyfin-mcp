"""Help/discovery API endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/tools")
async def list_tools():
    """Return the full list of available Jellyfin MCP tools and operations."""
    return {
        "success": True,
        "data": {
            "tools": [
                {
                    "name": "jellyfin_library",
                    "operations": ["list", "get", "scan", "create", "delete", "refresh"],
                    "description": "Manage Jellyfin media libraries",
                },
                {
                    "name": "jellyfin_media",
                    "operations": ["browse", "get_details", "get_recent", "get_similar", "update", "delete"],
                    "description": "Browse and manage Jellyfin media items",
                },
                {
                    "name": "jellyfin_search",
                    "operations": ["search", "advanced_search"],
                    "description": "Search across all Jellyfin libraries",
                },
                {
                    "name": "jellyfin_playback",
                    "operations": ["list_sessions", "play", "pause", "stop", "seek", "get_playback_info"],
                    "description": "Control Jellyfin playback sessions",
                },
                {
                    "name": "jellyfin_user",
                    "operations": ["list", "get", "create", "delete", "update_policy"],
                    "description": "Manage Jellyfin users",
                },
                {
                    "name": "jellyfin_playlist",
                    "operations": ["list", "create", "add_items", "remove_items", "delete"],
                    "description": "Manage Jellyfin playlists",
                },
                {
                    "name": "jellyfin_collections",
                    "operations": ["list", "create", "delete"],
                    "description": "Manage Jellyfin collections",
                },
                {
                    "name": "jellyfin_server",
                    "operations": ["status", "info", "tasks", "run_task"],
                    "description": "Jellyfin server management",
                },
                {
                    "name": "jellyfin_streaming",
                    "operations": ["list_sessions", "get_transcode_info"],
                    "description": "Streaming and transcoding management",
                },
                {
                    "name": "jellyfin_plugin",
                    "operations": ["list", "catalog", "install", "enable", "disable", "uninstall"],
                    "description": "Plugin management (Jellyfin exclusive feature)",
                },
                {
                    "name": "jellyfin_livetv",
                    "operations": ["channels", "guide", "recordings", "record"],
                    "description": "Live TV and DVR management",
                },
                {
                    "name": "jellyfin_subtitle",
                    "operations": ["search", "download"],
                    "description": "Subtitle search and download",
                },
                {
                    "name": "jellyfin_rag",
                    "operations": ["sync", "search", "status"],
                    "description": "Semantic search over Jellyfin metadata",
                },
                {
                    "name": "jellyfin_enrichment",
                    "operations": ["enrich", "enrich_by_tmdb_id"],
                    "description": "Metadata enrichment via TMDB/Wikipedia",
                },
                {
                    "name": "jellyfin_help",
                    "operations": ["discover", "quickstart"],
                    "description": "Tool discovery and quickstart guide",
                },
                {
                    "name": "jellyfin_arr_stack",
                    "operations": ["status", "search_missing", "add_missing"],
                    "description": "Cross-coordinate with Sonarr/Radarr *arr stack",
                },
                {
                    "name": "jellyfin_ffmpeg",
                    "operations": ["list_encoders", "transcode", "probe"],
                    "description": "FFmpeg operations (hardware transcoding)",
                },
                {
                    "name": "jellyfin_reporting",
                    "operations": ["library_report", "user_activity", "storage_usage"],
                    "description": "Library and usage reporting",
                },
                {
                    "name": "jellyfin_recommend",
                    "operations": ["similar", "genre_based", "continue_watching"],
                    "description": "Content recommendations",
                },
                {
                    "name": "jellyfin_metadata",
                    "operations": ["get", "refresh", "identify", "download_images"],
                    "description": "Metadata management",
                },
            ]
        },
    }


@router.get("/quickstart")
async def quickstart():
    """Return quickstart guide for jellyfin-mcp."""
    return {
        "success": True,
        "data": {
            "guide": [
                {"step": 1, "action": "List libraries", "tool": "jellyfin_library", "operation": "list"},
                {"step": 2, "action": "Browse media", "tool": "jellyfin_media", "operation": "browse"},
                {"step": 3, "action": "Search content", "tool": "jellyfin_search", "operation": "search"},
                {"step": 4, "action": "Manage playback", "tool": "jellyfin_playback", "operation": "list_sessions"},
                {"step": 5, "action": "Browse plugins", "tool": "jellyfin_plugin", "operation": "catalog"},
                {"step": 6, "action": "Semantic search", "tool": "jellyfin_rag", "operation": "sync then search"},
                {"step": 7, "action": "Discover all tools", "tool": "jellyfin_help", "operation": "discover"},
            ]
        },
    }
