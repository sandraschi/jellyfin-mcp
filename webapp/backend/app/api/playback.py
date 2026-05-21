"""Playback/sessions API endpoints."""
from fastapi import APIRouter, HTTPException, Query

from ..jel import get_client

router = APIRouter()


@router.get("/sessions")
async def list_sessions():
    """List all active playback sessions."""
    try:
        async with get_client() as client:
            resp = await client.get("/Sessions")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/play")
async def play_session(session_id: str, item_ids: str = Query(...)):
    """Send play command to a session."""
    try:
        ids = [i.strip() for i in item_ids.split(",")]
        async with get_client() as client:
            resp = await client.post(
                f"/Sessions/{session_id}/Playing",
                json={"ItemIds": ids, "PlayCommand": "PlayNow"},
            )
            resp.raise_for_status()
            return {"success": True, "message": f"Play sent to session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause a playback session."""
    try:
        async with get_client() as client:
            resp = await client.post(f"/Sessions/{session_id}/Playing/Pause")
            resp.raise_for_status()
            return {"success": True, "message": f"Session {session_id} paused"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop a playback session."""
    try:
        async with get_client() as client:
            resp = await client.post(f"/Sessions/{session_id}/Command/Stop")
            resp.raise_for_status()
            return {"success": True, "message": f"Session {session_id} stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/seek")
async def seek_session(session_id: str, ticks: int = Query(...)):
    """Seek to a position in a playback session (in 100-nanosecond ticks)."""
    try:
        async with get_client() as client:
            resp = await client.post(
                f"/Sessions/{session_id}/Playing/Seek",
                json={"SeekPositionTicks": ticks},
            )
            resp.raise_for_status()
            return {"success": True, "message": f"Seeked session {session_id} to {ticks} ticks"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
