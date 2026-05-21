"""WebSocket event bridge for Jellyfin real-time events."""

import asyncio
import json
import logging

import aiohttp


class WebSocketService:
    """Manages Jellyfin WebSocket connection and dispatches events."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._running = False
        self._listeners: list[callable] = []
        self._logger = logging.getLogger("websocket_service")

    async def start(self):
        """Connect to Jellyfin WebSocket and begin listening."""
        ws_url = self.base_url.replace("http", "ws") + "/websocket"
        try:
            self._ws = await aiohttp.ClientSession().ws_connect(
                ws_url,
                headers={"X-Emby-Token": self.api_key},
                heartbeat=30,
            )
            self._running = True
            self._logger.info("WebSocket connected to Jellyfin")
            asyncio.create_task(self._listen())
        except Exception as e:
            self._logger.warning("WebSocket connection failed (non-fatal): %s", e)

    async def stop(self):
        self._running = False
        if self._ws and not self._ws.closed:
            await self._ws.close()

    async def _listen(self):
        """Event loop: receive and dispatch WebSocket messages."""
        while self._running and self._ws and not self._ws.closed:
            try:
                msg = await self._ws.receive(timeout=30)
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    message_type = data.get("MessageType", "")
                    for listener in self._listeners:
                        try:
                            await listener(message_type, data)
                        except Exception:
                            pass
                elif msg.type == aiohttp.WSMsgType.CLOSED or msg.type == aiohttp.WSMsgType.ERROR:
                    break
            except TimeoutError:
                continue
            except Exception as e:
                self._logger.debug("WebSocket read error: %s", e)
                break

        if self._running:
            self._logger.info("WebSocket disconnected, will reconnect")
            await asyncio.sleep(5)
            asyncio.create_task(self.start())

    def add_listener(self, listener: callable):
        """Register async callback(event_type: str, data: dict)."""
        self._listeners.append(listener)

    def remove_listener(self, listener: callable):
        if listener in self._listeners:
            self._listeners.remove(listener)

    async def get_events(self) -> asyncio.Queue:
        """Return an asyncio.Queue that receives (event_type, data) tuples."""
        queue = asyncio.Queue()

        async def _relay(event_type, data):
            await queue.put((event_type, data))

        self.add_listener(_relay)
        return queue
