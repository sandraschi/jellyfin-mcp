"""
FastMCP 3.2 Unified Transport Configuration for jellyfin-mcp.
Provides STDIO, HTTP Streamable, and SSE transport modes.
"""

import argparse
import asyncio
import logging
import os
from typing import Literal

logger = logging.getLogger(__name__)

TransportType = Literal["stdio", "http", "sse"]

ENV_TRANSPORT = "JELLYFIN_MCP_TRANSPORT"
ENV_HOST = "JELLYFIN_MCP_HOST"
ENV_PORT = "JELLYFIN_MCP_PORT"
ENV_PATH = "JELLYFIN_MCP_PATH"


def get_transport_config() -> dict:
    return {
        "transport": os.getenv(ENV_TRANSPORT, "stdio").lower().strip(),
        "host": os.getenv(ENV_HOST, "127.0.0.1").strip(),
        "port": int(os.getenv(ENV_PORT, "10934").strip()),
        "path": os.getenv(ENV_PATH, "/mcp").strip(),
    }


def create_argument_parser(server_name: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=f"{server_name} - FastMCP 3.2+ Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Environment Variables:
  {ENV_TRANSPORT}    Transport mode: stdio, http, sse (default: stdio)
  {ENV_HOST}         Bind address (default: 127.0.0.1)
  {ENV_PORT}         Port number (default: 10934)
  {ENV_PATH}         HTTP endpoint path (default: /mcp)

Examples:
  python -m jellyfin_mcp --stdio
  python -m jellyfin_mcp --http --port 10934
  JELLYFIN_MCP_TRANSPORT=http JELLYFIN_MCP_PORT=10934 python -m jellyfin_mcp
""",
    )

    transport_group = parser.add_mutually_exclusive_group()
    transport_group.add_argument("--stdio", action="store_true", help="Run in STDIO mode (default)")
    transport_group.add_argument("--http", action="store_true", help="Run in HTTP Streamable mode")
    transport_group.add_argument("--sse", action="store_true", help="Run in SSE mode (deprecated)")
    parser.add_argument("--host", default=None, help=f"Host to bind (default: {ENV_HOST} or 127.0.0.1)")
    parser.add_argument("--port", type=int, default=None, help=f"Port (default: {ENV_PORT} or 10934)")
    parser.add_argument("--path", default=None, help=f"HTTP endpoint path (default: {ENV_PATH} or /mcp)")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")

    return parser


def resolve_transport(args: argparse.Namespace) -> TransportType:
    if args.http:
        return "http"
    if args.sse:
        return "sse"
    if args.stdio:
        return "stdio"
    env_transport = os.getenv(ENV_TRANSPORT, "stdio").lower().strip()
    if env_transport not in ("stdio", "http", "sse"):
        return "stdio"
    return env_transport  # type: ignore


def resolve_config(args: argparse.Namespace) -> dict:
    env_config = get_transport_config()
    return {
        "transport": resolve_transport(args),
        "host": args.host if args.host is not None else env_config["host"],
        "port": args.port if args.port is not None else env_config["port"],
        "path": args.path if args.path is not None else env_config["path"],
    }


def run_server(mcp_app, args: argparse.Namespace | None = None, server_name: str = "jellyfin-mcp") -> None:
    asyncio.run(run_server_async(mcp_app, args, server_name))


async def run_server_async(mcp_app, args: argparse.Namespace | None = None, server_name: str = "jellyfin-mcp") -> None:
    if args is None:
        parser = create_argument_parser(server_name)
        args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    config = resolve_config(args)
    transport = config["transport"]

    logger.info(f"Starting {server_name}")
    logger.info(f"Transport: {transport.upper()}")

    try:
        if transport == "stdio":
            logger.info("Running in STDIO mode")
            await mcp_app.run_stdio_async()

        elif transport == "http":
            host = config["host"]
            port = config["port"]
            path = config["path"]
            endpoint = f"http://{host}:{port}{path}"
            logger.info(f"Running HTTP: {endpoint}")

            app = mcp_app.http_app()
            from fastapi.middleware.cors import CORSMiddleware

            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            @app.get("/health")
            async def health():
                return {"status": "ok", "server": server_name}

            await mcp_app.run_http_async(host=host, port=port, path=path)

        elif transport == "sse":
            host = config["host"]
            port = config["port"]
            logger.info(f"Running SSE: http://{host}:{port}")
            await mcp_app.run_async(transport="sse", host=host, port=port)

    except asyncio.CancelledError:
        logger.info(f"{server_name} task cancelled")
    except Exception as e:
        logger.error(f"{server_name} failed: {e}", exc_info=True)
        raise


__all__ = [
    "TransportType",
    "ENV_TRANSPORT", "ENV_HOST", "ENV_PORT", "ENV_PATH",
    "get_transport_config", "create_argument_parser",
    "resolve_transport", "resolve_config",
    "run_server", "run_server_async",
]
