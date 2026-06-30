"""Plugin management API endpoints."""

from fastapi import APIRouter, HTTPException

from ..jel import get_client

router = APIRouter()


@router.get("")
@router.get("/")
async def list_plugins():
    """List installed Jellyfin plugins."""
    try:
        async with get_client() as client:
            resp = await client.get("/Plugins")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog")
async def plugin_catalog():
    """Fetch plugin catalog from the Jellyfin server."""
    try:
        async with get_client() as client:
            resp = await client.get("/Packages")
            resp.raise_for_status()
            data = resp.json()
            packages = data if isinstance(data, list) else data.get("Items", data)
            return {"success": True, "data": packages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/install")
async def install_plugin(plugin_id: str, version: str = "latest"):
    """Install a plugin by ID."""
    try:
        async with get_client() as client:
            resp = await client.post(
                f"/Plugins/{plugin_id}/Install",
                json={"Version": version},
            )
            resp.raise_for_status()
            return {"success": True, "message": f"Plugin {plugin_id} install requested"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    """Enable a plugin."""
    try:
        async with get_client() as client:
            resp = await client.post(f"/Plugins/{plugin_id}/Enable")
            resp.raise_for_status()
            return {"success": True, "message": f"Plugin {plugin_id} enabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    """Disable a plugin."""
    try:
        async with get_client() as client:
            resp = await client.post(f"/Plugins/{plugin_id}/Disable")
            resp.raise_for_status()
            return {"success": True, "message": f"Plugin {plugin_id} disabled"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
