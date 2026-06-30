"""Quick Jellyfin connectivity check."""

import asyncio

from jellyfin_mcp.config import get_settings
from jellyfin_mcp.services.jellyfin_service import JellyfinService


async def main() -> None:
    settings = get_settings()
    jf = JellyfinService(settings.server_url, settings.api_key, settings.timeout)
    await jf.connect()
    info = await jf.get_server_info()
    libs = await jf.get_libraries()
    print(f"version={info.get('Version')}")
    print(f"libraries={len(libs)}")
    await jf.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
