"""Streaming/transcoding API endpoints."""
from fastapi import APIRouter, HTTPException

from ..jel import get_client

router = APIRouter()


@router.get("/sessions")
async def streaming_sessions():
    """List active streaming sessions."""
    try:
        async with get_client() as client:
            resp = await client.get("/Sessions")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transcode")
async def transcode_info(item_id: str):
    """Get playback/transcode info for an item."""
    try:
        async with get_client() as client:
            resp = await client.post(f"/Items/{item_id}/PlaybackInfo")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
