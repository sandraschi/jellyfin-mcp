"""Image proxy API — forwards image requests to Jellyfin server."""
import logging

import httpx
from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask

from ..jel import get_base_url, get_api_key

logger = logging.getLogger(__name__)
router = APIRouter()


@router.api_route("/{path:path}", methods=["GET", "HEAD"])
async def proxy_image(path: str):
    """Proxy image/asset requests to Jellyfin. Handles 307 redirects."""
    base_url = get_base_url()
    api_key = get_api_key()

    if not api_key:
        return Response(status_code=500, content="JELLYFIN_API_KEY not set")

    url = f"{base_url}/{path}"
    params = {"X-Emby-Token": api_key}

    client = httpx.AsyncClient(follow_redirects=True)
    try:
        req = client.build_request("GET", url, params=params)
        r = await client.send(req, stream=True)

        return StreamingResponse(
            r.aiter_bytes(),
            status_code=r.status_code,
            media_type=r.headers.get("content-type"),
            background=BackgroundTask(client.aclose),
        )
    except Exception:
        await client.aclose()
        logger.exception("Image proxy error for path=%s", path)
        return Response(status_code=500, content="Image proxy failed")
