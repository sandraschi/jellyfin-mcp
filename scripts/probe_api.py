"""Probe Jellyfin API paths for test fixes."""
import asyncio

from jellyfin_mcp.config import get_settings
from jellyfin_mcp.services.jellyfin_service import JellyfinService


async def main() -> None:
    settings = get_settings()
    jf = JellyfinService(settings.server_url, settings.api_key, settings.timeout)
    await jf.connect()
    uid = await jf.get_default_user_id()
    items = await jf.get_items(limit=1)
    item_id = items["Items"][0]["Id"]

    for label, coro in [
        ("user path", jf._get(f"/Users/{uid}/Items/{item_id}")),
        ("items+UserId", jf._get(f"/Items/{item_id}", UserId=uid)),
        ("items plain", jf._get(f"/Items/{item_id}")),
    ]:
        try:
            result = await coro
            print(f"{label}: OK {result.get('Name')}")
        except Exception as e:
            print(f"{label}: FAIL {e}")

    for path in ["/LiveTv/TunerHosts", "/LiveTv/Tuners", "/LiveTv/Info"]:
        try:
            result = await jf._get(path)
            print(f"{path}: OK {type(result)}")
        except Exception as e:
            print(f"{path}: FAIL {e}")

    await jf.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
