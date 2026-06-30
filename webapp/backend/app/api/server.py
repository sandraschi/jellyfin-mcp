"""Server status/info API endpoints."""

from fastapi import APIRouter, HTTPException

from ..jel import get_client

router = APIRouter()


@router.get("/status")
async def server_status():
    """Get Jellyfin server health status."""
    try:
        async with get_client() as client:
            resp = await client.get("/System/Info")
            resp.raise_for_status()
            info = resp.json()
            return {
                "success": True,
                "data": {
                    "version": info.get("Version"),
                    "os": info.get("OperatingSystem"),
                    "id": info.get("Id"),
                    "healthy": True,
                },
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def server_info():
    """Get comprehensive server info."""
    try:
        async with get_client() as client:
            resp = await client.get("/System/Info")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks")
async def server_tasks():
    """List scheduled tasks."""
    try:
        async with get_client() as client:
            resp = await client.get("/ScheduledTasks")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
