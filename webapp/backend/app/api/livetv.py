"""Live TV / DVR API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from ..jel import get_client

router = APIRouter()


@router.get("/channels")
async def list_channels():
    """List Live TV channels."""
    try:
        async with get_client() as client:
            resp = await client.get("/LiveTv/Channels")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/guide")
async def epg_guide(channel_id: str | None = Query(None)):
    """Get EPG program guide, optionally filtered by channel."""
    try:
        params = {}
        if channel_id:
            params["ChannelId"] = channel_id
        async with get_client() as client:
            resp = await client.get("/LiveTv/Programs", params=params)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recordings")
async def list_recordings():
    """List DVR recordings."""
    try:
        async with get_client() as client:
            resp = await client.get("/LiveTv/Recordings")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record")
async def create_recording(program_id: str = Query(...)):
    """Schedule a recording for a program."""
    try:
        async with get_client() as client:
            resp = await client.post(
                "/LiveTv/Recordings",
                json={"ProgramId": program_id},
            )
            resp.raise_for_status()
            return {"success": True, "message": f"Recording scheduled for program {program_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
