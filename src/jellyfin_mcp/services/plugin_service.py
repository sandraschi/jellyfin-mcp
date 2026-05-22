"""Jellyfin plugin service — catalog, install, configure."""

import logging

from .base import ServiceError


class PluginService:
    """Manage Jellyfin plugins: catalog browsing, install, configure."""

    def __init__(self, jellyfin_service):
        self._jf = jellyfin_service
        self._logger = logging.getLogger("plugin_service")
        self._catalog_cache: list[dict] | None = None

    async def get_catalog(self) -> list[dict]:
        """Fetch plugin catalog from the Jellyfin server."""
        if self._catalog_cache:
            return self._catalog_cache

        try:
            data = await self._jf.get_plugin_manifest()
            plugins = []
            for entry in data if isinstance(data, list) else data.get("plugins", []):
                plugins.append({
                    "id": entry.get("guid", entry.get("id", "")),
                    "name": entry.get("name", entry.get("id", "Unknown")),
                    "description": entry.get("description", entry.get("overview", "")),
                    "category": entry.get("category", entry.get("categoryName", "general")),
                    "version": entry.get("version", entry.get("versions", [{}])[0].get("version", "unknown") if entry.get("versions") else "unknown"),
                    "url": entry.get("sourceUrl", entry.get("sourceUrl", "")),
                })
            self._catalog_cache = plugins
            return plugins
        except Exception as e:
            raise ServiceError(f"Failed to fetch plugin catalog: {e}") from e

    async def get_installed(self) -> list[dict]:
        """List installed plugins from Jellyfin server."""
        return await self._jf.get_plugins()

    async def install(self, plugin_id: str, version: str = "latest") -> dict:
        catalog = await self.get_catalog()
        plugin = next((p for p in catalog if p["id"] == plugin_id), None)
        if not plugin:
            raise ServiceError(f"Plugin not found in catalog: {plugin_id}")

        self._logger.info("Installing plugin: %s v%s", plugin["name"], version)
        return await self._jf.install_plugin(plugin_id, version)

    async def uninstall(self, plugin_id: str) -> dict:
        return await self._jf.uninstall_plugin(plugin_id)

    async def enable(self, plugin_id: str) -> dict:
        return await self._jf.enable_plugin(plugin_id)

    async def disable(self, plugin_id: str) -> dict:
        return await self._jf.disable_plugin(plugin_id)

    async def configure(self, plugin_id: str, config: dict) -> dict:
        """Update plugin configuration via Jellyfin API."""
        return await self._jf._post(f"/Plugins/{plugin_id}/Configuration", json_body=config)

    async def get_configuration(self, plugin_id: str) -> dict:
        return await self._jf._get(f"/Plugins/{plugin_id}/Configuration")
