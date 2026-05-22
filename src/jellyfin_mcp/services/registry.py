"""Shared service registry — reuse lifespan connections across tool calls."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..utils import get_logger

if TYPE_CHECKING:
    from .jellyfin_service import JellyfinService
    from .websocket_service import WebSocketService

logger = get_logger(__name__)

_jellyfin_service: JellyfinService | None = None
_ws_service: WebSocketService | None = None


def get_registered_jellyfin_service() -> JellyfinService | None:
    """Return the shared Jellyfin service if already connected."""
    if _jellyfin_service is not None and _jellyfin_service.is_initialized:
        return _jellyfin_service
    return None


def set_jellyfin_service(service: JellyfinService | None) -> None:
    """Register a shared Jellyfin service instance."""
    global _jellyfin_service
    _jellyfin_service = service


def set_ws_service(service: WebSocketService | None) -> None:
    """Register a shared WebSocket service instance."""
    global _ws_service
    _ws_service = service


def get_ws_service() -> WebSocketService | None:
    """Return the shared WebSocket service if registered."""
    return _ws_service


async def get_jellyfin_service() -> JellyfinService:
    """Return a connected Jellyfin service, reusing the registry when available."""
    existing = get_registered_jellyfin_service()
    if existing is not None:
        return existing

    from ..config import get_settings
    from .jellyfin_service import JellyfinService

    settings = get_settings()
    if not settings.api_key:
        raise RuntimeError("JELLYFIN_API_KEY environment variable is required.")

    service = JellyfinService(
        base_url=settings.server_url,
        api_key=settings.api_key,
        timeout=settings.timeout,
    )
    await service.connect()
    set_jellyfin_service(service)
    logger.debug("Created on-demand Jellyfin service connection")
    return service


async def clear_services() -> None:
    """Disconnect and clear all registered services."""
    global _jellyfin_service, _ws_service

    if _ws_service is not None:
        try:
            await _ws_service.stop()
        except Exception as e:
            logger.warning("WebSocket service shutdown failed: %s", e)
        _ws_service = None

    if _jellyfin_service is not None:
        try:
            await _jellyfin_service.disconnect()
        except Exception as e:
            logger.warning("Jellyfin service shutdown failed: %s", e)
        _jellyfin_service = None
