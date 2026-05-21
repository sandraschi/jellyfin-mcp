"""User management API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..jel import get_client

router = APIRouter()


class CreateUserRequest(BaseModel):
    name: str
    password: str | None = None


@router.get("/")
async def list_users():
    """List all Jellyfin users."""
    try:
        async with get_client() as client:
            resp = await client.get("/Users")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
async def get_user(user_id: str):
    """Get details for a specific user."""
    try:
        async with get_client() as client:
            resp = await client.get(f"/Users/{user_id}")
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create")
async def create_user(body: CreateUserRequest):
    """Create a new Jellyfin user."""
    try:
        async with get_client() as client:
            resp = await client.post(
                "/Users/New",
                json={"Name": body.name, "Password": body.password or ""},
            )
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
