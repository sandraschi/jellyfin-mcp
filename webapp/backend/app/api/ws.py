"""WebSocket proxy — forwards Jellyfin WebSocket events to browser clients."""
import asyncio
import json
import logging
import os

import aiohttp
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)
router = APIRouter()

# Track connected browser clients
_active_connections: set[WebSocket] = set()


def _get_jellyfin_ws_url() -> str:
    url = os.getenv("JELLYFIN_URL") or os.getenv("JELLYFIN_SERVER_URL", "http://localhost:8096")
    url = url.rstrip("/")
    return url.replace("http", "ws") + "/websocket"


def _get_api_key() -> str:
    return os.getenv("JELLYFIN_API_KEY") or os.getenv("JELLYFIN_TOKEN", "")


async def _jellyfin_listener():
    """Connect to Jellyfin WebSocket and broadcast events to all browser clients."""
    ws_url = _get_jellyfin_ws_url()
    api_key = _get_api_key()

    try:
        session = aiohttp.ClientSession()
        ws = await session.ws_connect(ws_url, headers={"X-Emby-Token": api_key}, heartbeat=30)
        logger.info("WebSocket connected to Jellyfin at %s", ws_url)

        while True:
            msg = await ws.receive(timeout=30)
            if msg.type == aiohttp.WSMsgType.TEXT:
                data = json.loads(msg.data)
                to_remove = set()
                for conn in _active_connections:
                    try:
                        if conn.client_state != WebSocketState.DISCONNECTED:
                            await conn.send_text(msg.data)
                    except Exception:
                        to_remove.add(conn)
                _active_connections.difference_update(to_remove)
            elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                break
    except Exception as e:
        logger.warning("Jellyfin WebSocket connection error: %s", e)
    finally:
        if "ws" in locals() and not ws.closed:
            await ws.close()
        if "session" in locals():
            await session.close()


_jf_ws_task: asyncio.Task | None = None


@router.websocket("/ws")
async def websocket_proxy(ws: WebSocket):
    """Browser WebSocket endpoint — proxies Jellyfin events."""
    global _jf_ws_task

    await ws.accept()
    _active_connections.add(ws)

    # Start Jellyfin WebSocket listener on first connection
    if _jf_ws_task is None or _jf_ws_task.done():
        _jf_ws_task = asyncio.create_task(_jellyfin_listener())

    try:
        while True:
            data = await ws.receive_text()
            # Forward any browser commands to Jellyfin if needed
            # For now, just keep the connection alive
    except WebSocketDisconnect:
        _active_connections.discard(ws)
    except Exception:
        _active_connections.discard(ws)
