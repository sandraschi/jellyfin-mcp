"""Library API endpoints."""
from fastapi import APIRouter, HTTPException

from ..jel import get_client

router = APIRouter()


@router.get("/")
async def list_libraries():
    """List all Jellyfin libraries (VirtualFolders)."""
    try:
        async with get_client() as client:
            resp = await client.get("/Library/VirtualFolders")
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("Items", data)
            return {"success": True, "data": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{library_id}")
async def get_library(library_id: str):
    """Get details for a specific library."""
    try:
        async with get_client() as client:
            resp = await client.get("/Library/VirtualFolders")
            resp.raise_for_status()
            data = resp.json()
            items = data if isinstance(data, list) else data.get("Items", data)
            for lib in items:
                if lib.get("ItemId") == library_id or lib.get("Id") == library_id:
                    return {"success": True, "data": lib}
            raise HTTPException(status_code=404, detail=f"Library not found: {library_id}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{library_id}/scan")
async def scan_library(library_id: str):
    """Trigger a library scan."""
    try:
        async with get_client() as client:
            resp = await client.post(f"/Items/{library_id}/Refresh")
            resp.raise_for_status()
            return {"success": True, "message": f"Scan started for library {library_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
