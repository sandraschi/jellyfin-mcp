"""
jellyfin-mcp — FastMCP 3.2+ Server for Jellyfin Media Server.
"""

from .app import _is_stdio_mode, mcp
from .utils import get_logger

logger = get_logger(__name__)

from .tools import portmanteau  # noqa: F401, E402

try:
    from .tools.agentic import register_agentic_jellyfin_tools
    register_agentic_jellyfin_tools(mcp)
except ImportError as e:
    logger.warning("Agentic tools not registered: %s", e)

if not _is_stdio_mode:
    from starlette.applications import Starlette
    from starlette.middleware import Middleware
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route

    async def health(request):
        return JSONResponse({"status": "ok"})

    _mcp_app = mcp.http_app(
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["http://localhost:10935", "http://127.0.0.1:10935",
                               "http://localhost:10934", "http://127.0.0.1:10934"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        ]
    )

    app = Starlette(
        routes=[
            Route("/health", health),
            Mount("/", app=_mcp_app),
        ]
    )


def main():
    """Main entry point — supports STDIO, HTTP, and SSE transport."""
    from .transport import run_server

    logger.info("Starting jellyfin-mcp (FastMCP 3.2+)")
    run_server(mcp, server_name="jellyfin-mcp")


if __name__ == "__main__":
    main()
