"""Shared FastMCP instance for jellyfin-mcp."""

import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.prompts import Message

from .sampling import JellyfinSamplingConfig, JellyfinSamplingHandler

if os.name == "nt":
    try:
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        pass


_is_stdio_mode = not sys.stdout.isatty()
if os.getenv("JELLYFIN_ALLOW_LOGGING", "").lower() in ("1", "true", "yes") or any(
    "pytest" in (arg or "") for arg in sys.argv
):
    _is_stdio_mode = False

import logging

_original_getLogger = logging.getLogger

if _is_stdio_mode:
    class NullLogger(logging.Logger):
        def __init__(self, name="null", level=logging.NOTSET):
            super().__init__(name, level)
            self.propagate = False
            self.handlers = []

        def handle(self, record):
            pass

        def addHandler(self, hdlr):
            pass

        def removeHandler(self, hdlr):
            pass

        def hasHandlers(self):
            return False

    logging.getLogger = lambda name=None: NullLogger(name or "root")


@asynccontextmanager
async def _jellyfin_lifespan(app):
    """FastMCP 3.2 lifespan hook — connect/disconnect Jellyfin."""
    try:
        from .config import get_settings
        from .services.jellyfin_service import JellyfinService

        settings = get_settings()
        if settings.api_key:
            service = JellyfinService(
                base_url=settings.server_url,
                api_key=settings.api_key,
                timeout=settings.timeout,
            )
            await service.connect()
            app.state.jellyfin_service = service
    except Exception:
        pass

    try:
        if settings.ws_enabled:
            from .services.websocket_service import WebSocketService
            ws_service = WebSocketService(base_url=settings.server_url, api_key=settings.api_key)
            await ws_service.start()
            app.state.ws_service = ws_service
    except Exception:
        pass

    yield

    ws = getattr(app.state, "ws_service", None)
    if ws:
        await ws.stop()
    jf = getattr(app.state, "jellyfin_service", None)
    if jf:
        await jf.disconnect()


_sampling_config = JellyfinSamplingConfig.from_env()
_sampling_handler = JellyfinSamplingHandler(config=_sampling_config)
_USE_CLIENT_SAMPLING = os.getenv("JELLYFIN_SAMPLING_USE_CLIENT_LLM", "").lower() in ("1", "true", "yes")

mcp = FastMCP(
    "JellyfinMCP",
    instructions=(
        "JellyfinMCP is a FastMCP 3.2+ server for Jellyfin Media Server — the open-source Plex alternative. "
        "Portmanteau tools include jellyfin_library, jellyfin_media, jellyfin_search, jellyfin_playback, "
        "jellyfin_user, jellyfin_playlist, jellyfin_server, jellyfin_streaming, jellyfin_plugin, "
        "jellyfin_livetv, jellyfin_subtitle, jellyfin_rag, jellyfin_enrichment, jellyfin_help. "
        "Supports WebSocket real-time events, plugin management, Live TV/DVR, and hardware transcoding (free). "
        "RAG: jellyfin_rag sync then semantic_search. "
        "Sampling: configure JELLYFIN_SAMPLING_BASE_URL for server-side LLM. "
        "Resources: resource://jellyfin/capabilities, resource://jellyfin/plugins, resource://jellyfin/quickstart."
    ),
    lifespan=_jellyfin_lifespan,
    sampling_handler=_sampling_handler,
    sampling_handler_behavior="fallback" if _USE_CLIENT_SAMPLING else "always",
    on_duplicate="replace",
    strict_input_validation=True,
)


@mcp.resource("resource://jellyfin/capabilities")
def jellyfin_capabilities_resource() -> str:
    return """# jellyfin-mcp capabilities (FastMCP 3.2+)

## Tools
Portmanteau: jellyfin_library, jellyfin_media, jellyfin_search, jellyfin_playback, jellyfin_user,
jellyfin_playlist, jellyfin_collections, jellyfin_metadata, jellyfin_server, jellyfin_streaming,
jellyfin_plugin, jellyfin_arr_stack, jellyfin_subtitle, jellyfin_livetv, jellyfin_ffmpeg,
jellyfin_enrichment, jellyfin_rag, jellyfin_reporting, jellyfin_recommend, jellyfin_help,
jellyfin_integration, jellyfin_agentic — 22 tools, 120+ operations.

## Unique Features (vs Plex)
- Plugin management (install/configure/uninstall via MCP)
- WebSocket real-time events (playback, transcode, sessions)
- Live TV/DVR (EPG grid, recordings, tuners)
- Hardware transcoding (free, no paywall)
- Fully air-gappable (local auth, no cloud)
- Full OpenAPI/Swagger API docs

## Sampling
Default: OpenAI-compatible HTTP at JELLYFIN_SAMPLING_BASE_URL (e.g. Ollama http://127.0.0.1:11434/v1).
jellyfin_agentic: sample_step loop with real tool execution.
"""


@mcp.resource("resource://jellyfin/plugins")
def jellyfin_plugins_resource() -> str:
    return """# Jellyfin Top Plugins

| Plugin | ID | Purpose |
|--------|-----|---------|
| Intro Skipper | intro-skipper | Auto-detect/skip intros |
| Open Subtitles | opensubtitles | Download subtitles |
| Subtitle Extract | subtitle-extract | Extract embedded subtitles |
| Theme Songs | theme-songs | Play theme songs |
| LDAP Auth | ldap-auth | LDAP/AD authentication |
| Reports | reports | Library reports |
| Merge Versions | merge-versions | Auto-merge movie versions |
| Trakt | trakt | Scrobble to Trakt.tv |
| TMDb Box Sets | tmdb-box-sets | Auto-collections from TMDb |
| AniDB | anidb | Anime metadata |

Use jellyfin_plugin(operation="catalog") for full list.
Use jellyfin_plugin(operation="install", plugin_id="...") to install.
"""


@mcp.resource("resource://jellyfin/quickstart")
def jellyfin_quickstart_resource() -> str:
    return """# jellyfin-mcp Quickstart

1. jellyfin_library(operation="list") — list all libraries
2. jellyfin_media(operation="browse", library_id="...") — browse media
3. jellyfin_search(operation="search", query="...") — search across libraries
4. jellyfin_playback(operation="list_sessions") — active playback sessions
5. jellyfin_plugin(operation="catalog") — available plugins
6. jellyfin_rag(operation="sync") then jellyfin_rag(operation="search", query="...") — semantic search
7. jellyfin_help(operation="discover") — all tools and operations
"""


@mcp.prompt()
def jellyfin_media_guide() -> list[Message]:
    """Guide for Jellyfin media search and discovery."""
    return [
        Message(
            "Use jellyfin_search for keyword search; use jellyfin_rag(operation='search', query='...') "
            "for natural-language semantic search. Run jellyfin_rag(operation='sync') first to index metadata.",
            role="user",
        )
    ]


def http_app():
    """Return ASGI app for HTTP mode (FastMCP 3.2)."""
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware

    allowed_origins = [
        "http://localhost:10935",
        "http://127.0.0.1:10935",
        "http://localhost:10934",
        "http://127.0.0.1:10934",
    ]
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"],
        )
    ]
    return mcp.http_app(middleware=middleware)


if _is_stdio_mode:
    logging.getLogger = _original_getLogger
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
