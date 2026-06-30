"""Probe plugin catalog endpoints."""

import asyncio

import httpx

from jellyfin_mcp.config import get_settings


async def main() -> None:
    settings = get_settings()
    headers = {"X-Emby-Token": settings.api_key}
    base = settings.server_url

    paths = [
        "/Packages",
        "/Packages/Available",
        "/Plugins/Available",
        "/System/Info/Public",
    ]
    async with httpx.AsyncClient(base_url=base, headers=headers, timeout=30) as client:
        for path in paths:
            resp = await client.get(path)
            print(path, resp.status_code, str(resp.text)[:120])

    urls = [
        "https://repo.jellyfin.org/files/plugin/manifest.json",
        "https://raw.githubusercontent.com/jellyfin/jellyfin-plugin-manifest/master/manifest.json",
        "https://raw.githubusercontent.com/jellyfin/jellyfin-plugin-repository/master/manifest.json",
    ]
    async with httpx.AsyncClient(timeout=30) as client:
        for url in urls:
            resp = await client.get(url)
            print(url, resp.status_code)


if __name__ == "__main__":
    asyncio.run(main())
