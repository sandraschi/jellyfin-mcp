"""Jellyfin REST API service wrapper using jellyfin-apiclient-python."""

from typing import Any

import httpx

from .base import AuthenticationError, BaseService, JellyfinConnectionError, NotFoundError


class JellyfinService(BaseService):
    """Core Jellyfin REST API wrapper with executor pattern."""

    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        super().__init__("jellyfin_service")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._http: httpx.AsyncClient | None = None

    async def _initialize(self, **kwargs) -> None:
        self._http = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"X-Emby-Token": self.api_key},
        )
        try:
            resp = await self._http.get("/System/Info")
            self.logger.info("Connected to Jellyfin %s", resp.json().get("Version", "?"))
        except Exception as e:
            raise JellyfinConnectionError(f"Cannot connect to Jellyfin at {self.base_url}: {e}")

    async def connect(self):
        await self.initialize()

    async def disconnect(self):
        if self._http:
            await self._http.aclose()
            self._http = None
        await self.shutdown()

    def _require_client(self) -> httpx.AsyncClient:
        if not self._http:
            raise JellyfinConnectionError("Not connected to Jellyfin")
        return self._http

    async def _get(self, path: str, **params) -> dict:
        client = self._require_client()
        resp = await client.get(path, params=params)
        if resp.status_code == 401:
            raise AuthenticationError("Invalid Jellyfin API key")
        if resp.status_code == 404:
            raise NotFoundError(f"Resource not found: {path}")
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, json_body: dict | None = None, **params) -> dict:
        client = self._require_client()
        resp = await client.post(path, json=json_body, params=params)
        if resp.status_code == 401:
            raise AuthenticationError("Invalid Jellyfin API key")
        resp.raise_for_status()
        return resp.json()

    async def _delete(self, path: str, **params) -> dict:
        client = self._require_client()
        resp = await client.delete(path, params=params)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"success": True}
        return resp.json()

    # --- System ---
    async def get_server_info(self) -> dict:
        return await self._get("/System/Info")

    async def get_server_status(self) -> dict:
        info = await self._get("/System/Info")
        return {
            "version": info.get("Version"),
            "os": info.get("OperatingSystem"),
            "id": info.get("Id"),
            "healthy": True,
        }

    async def get_scheduled_tasks(self) -> list[dict]:
        return await self._get("/ScheduledTasks")

    async def run_task(self, task_id: str) -> dict:
        return await self._post(f"/ScheduledTasks/Running/{task_id}")

    # --- Libraries ---
    async def get_libraries(self) -> list[dict]:
        resp = await self._get("/Library/VirtualFolders")
        return resp if isinstance(resp, list) else resp.get("Items", resp)

    async def get_library(self, library_id: str) -> dict:
        libs = await self.get_libraries()
        for lib in libs:
            if lib.get("ItemId") == library_id or lib.get("Id") == library_id:
                return lib
        raise NotFoundError(f"Library not found: {library_id}")

    async def scan_library(self, library_id: str) -> dict:
        return await self._post(f"/Items/{library_id}/Refresh", json_body={"Recursive": True})

    async def create_library(self, name: str, collection_type: str, paths: list[str]) -> dict:
        body = {
            "Name": name,
            "CollectionType": collection_type,
            "LibraryOptions": {"PathInfos": [{"Path": p} for p in paths]},
        }
        return await self._post("/Library/VirtualFolders", json_body=body)

    async def delete_library(self, library_id: str) -> dict:
        return await self._delete("/Library/VirtualFolders", id=library_id)

    async def refresh_library(self, library_id: str) -> dict:
        return await self._post(f"/Items/{library_id}/Refresh", json_body={"Recursive": True, "ImageRefreshMode": "FullRefresh", "MetadataRefreshMode": "FullRefresh"})

    # --- Items (Media) ---
    async def get_items(
        self,
        parent_id: str | None = None,
        include_item_types: str | None = None,
        sort_by: str = "SortName",
        sort_order: str = "Ascending",
        limit: int = 100,
        recursive: bool = True,
        filters: str | None = None,
        search_term: str | None = None,
    ) -> dict:
        params: dict[str, Any] = {
            "SortBy": sort_by,
            "SortOrder": sort_order,
            "Limit": limit,
            "Recursive": str(recursive).lower(),
        }
        if parent_id:
            params["ParentId"] = parent_id
        if include_item_types:
            params["IncludeItemTypes"] = include_item_types
        if filters:
            params["Filters"] = filters
        if search_term:
            params["SearchTerm"] = search_term
        return await self._get("/Items", **params)

    async def get_item(self, item_id: str) -> dict:
        return await self._get(f"/Users/{{user_id}}/Items/{item_id}")

    async def get_recent(self, library_id: str, limit: int = 24) -> dict:
        return await self._get("/Users/{user_id}/Items/Latest", ParentId=library_id, Limit=limit)

    async def get_similar(self, item_id: str, limit: int = 10) -> dict:
        return await self._get(f"/Items/{item_id}/Similar", Limit=limit)

    async def update_item(self, item_id: str, metadata: dict) -> dict:
        return await self._post(f"/Items/{item_id}", json_body=metadata)

    async def delete_item(self, item_id: str) -> dict:
        return await self._delete(f"/Items/{item_id}")

    async def get_item_stream_info(self, item_id: str) -> dict:
        return await self._post(f"/Items/{item_id}/PlaybackInfo")

    # --- Search ---
    async def search(
        self,
        query: str,
        include_item_types: str = "Movie,Series,MusicArtist,Audio",
        limit: int = 50,
    ) -> dict:
        return await self._get(
            "/Search/Hints",
            SearchTerm=query,
            IncludeItemTypes=include_item_types,
            Limit=limit,
        )

    # --- Users ---
    async def get_users(self) -> list[dict]:
        return await self._get("/Users")

    async def get_user(self, user_id: str) -> dict:
        return await self._get(f"/Users/{user_id}")

    async def create_user(self, name: str, password: str | None = None) -> dict:
        return await self._post("/Users/New", json_body={"Name": name, "Password": password or ""})

    async def delete_user(self, user_id: str) -> dict:
        return await self._delete(f"/Users/{user_id}")

    async def update_user_policy(self, user_id: str, policy: dict) -> dict:
        return await self._post(f"/Users/{user_id}/Policy", json_body=policy)

    # --- Sessions / Playback ---
    async def get_sessions(self) -> list[dict]:
        return await self._get("/Sessions")

    async def send_play_command(self, session_id: str, item_ids: list[str], start_index: int = 0) -> dict:
        return await self._post(
            f"/Sessions/{session_id}/Playing",
            json_body={"ItemIds": item_ids, "StartIndex": start_index},
        )

    async def send_command(self, session_id: str, command: str, **kwargs) -> dict:
        return await self._post(
            f"/Sessions/{session_id}/Command/{command}", json_body=kwargs or {}
        )

    async def stop_session(self, session_id: str) -> dict:
        return await self._post(f"/Sessions/{session_id}/Command/Stop")

    async def pause_session(self, session_id: str) -> dict:
        return await self._post(f"/Sessions/{session_id}/Playing/Pause")

    async def unpause_session(self, session_id: str) -> dict:
        return await self._post(f"/Sessions/{session_id}/Playing/Unpause")

    async def seek_session(self, session_id: str, ticks: int) -> dict:
        return await self._post(f"/Sessions/{session_id}/Playing/Seek", json_body={"SeekPositionTicks": ticks})

    # --- Playlists ---
    async def get_playlists(self, user_id: str) -> dict:
        return await self._get("/Playlists", UserId=user_id)

    async def create_playlist(self, name: str, item_ids: list[str], user_id: str) -> dict:
        return await self._post(
            "/Playlists",
            json_body={"Name": name, "Ids": item_ids, "UserId": user_id},
        )

    async def add_to_playlist(self, playlist_id: str, item_ids: list[str], user_id: str) -> dict:
        return await self._post(
            f"/Playlists/{playlist_id}/Items",
            json_body={"Ids": item_ids, "UserId": user_id},
        )

    async def remove_from_playlist(self, playlist_id: str, item_ids: list[str]) -> dict:
        return await self._delete(f"/Playlists/{playlist_id}/Items", Ids=",".join(item_ids))

    async def delete_playlist(self, playlist_id: str) -> dict:
        return await self._delete(f"/Playlists/{playlist_id}")

    # --- Collections ---
    async def get_collections(self, user_id: str) -> dict:
        return await self._get("/Collections", UserId=user_id)

    async def create_collection(self, name: str, item_ids: list[str]) -> dict:
        return await self._post("/Collections", json_body={"Name": name, "Ids": item_ids})

    async def delete_collection(self, collection_id: str) -> dict:
        return await self._delete(f"/Collections/{collection_id}")

    # --- Plugins ---
    async def get_plugins(self) -> list[dict]:
        return await self._get("/Plugins")

    async def get_plugin_manifest(self) -> dict:
        """Fetch remote plugin catalog."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get("https://raw.githubusercontent.com/jellyfin/jellyfin-plugin-manifest/master/manifest.json")
            return resp.json()

    async def install_plugin(self, plugin_id: str, version: str = "latest") -> dict:
        return await self._post(f"/Plugins/{plugin_id}/Install", json_body={"Version": version})

    async def uninstall_plugin(self, plugin_id: str) -> dict:
        return await self._delete(f"/Plugins/{plugin_id}")

    async def enable_plugin(self, plugin_id: str) -> dict:
        return await self._post(f"/Plugins/{plugin_id}/Enable")

    async def disable_plugin(self, plugin_id: str) -> dict:
        return await self._post(f"/Plugins/{plugin_id}/Disable")

    # --- Live TV ---
    async def get_channels(self) -> dict:
        return await self._get("/LiveTv/Channels")

    async def get_recordings(self) -> dict:
        return await self._get("/LiveTv/Recordings")

    async def get_epg(self, channel_id: str | None = None) -> dict:
        params = {}
        if channel_id:
            params["ChannelId"] = channel_id
        return await self._get("/LiveTv/Programs", **params)

    async def create_recording(self, program_id: str) -> dict:
        return await self._post("/LiveTv/Recordings", json_body={"ProgramId": program_id})

    # --- Subtitles ---
    async def search_subtitles(self, item_id: str, language: str = "eng") -> dict:
        return await self._get(f"/Items/{item_id}/RemoteSearch/Subtitles/{language}")

    async def download_subtitles(self, item_id: str, subtitle_id: str) -> dict:
        return await self._post(f"/Items/{item_id}/RemoteSearch/Subtitles/Download", json_body={"Id": subtitle_id})

    # --- Devices ---
    async def get_devices(self) -> dict:
        return await self._get("/Devices")

    # --- Images ---
    async def get_image_url(self, item_id: str, image_type: str = "Primary", image_index: int = 0) -> str:
        return f"{self.base_url}/Items/{item_id}/Images/{image_type}/{image_index}"
