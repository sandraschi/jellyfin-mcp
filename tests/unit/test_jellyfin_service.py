"""Unit tests for JellyfinService HTTP wrapper."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from jellyfin_mcp.services.base import AuthenticationError, NotFoundError
from jellyfin_mcp.services.jellyfin_service import JellyfinService


def _mock_response(status_code: int, json_data=None):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError("error", request=MagicMock(), response=response)
    return response


@pytest.mark.asyncio
async def test_connect_validates_server():
    service = JellyfinService("http://localhost:8096", "test-key", timeout=10)
    mock_client = AsyncMock()
    mock_client.get = AsyncMock(return_value=_mock_response(200, {"Version": "10.11.9"}))

    with patch("httpx.AsyncClient", return_value=mock_client):
        await service.connect()

    assert service.is_initialized
    mock_client.get.assert_awaited_with("/System/Info")


@pytest.mark.asyncio
async def test_get_raises_authentication_error_on_401():
    service = JellyfinService("http://localhost:8096", "bad-key", timeout=10)
    service._http = AsyncMock()
    service._http.get = AsyncMock(return_value=_mock_response(401))

    with pytest.raises(AuthenticationError):
        await service._get("/Items")


@pytest.mark.asyncio
async def test_get_raises_not_found_on_404():
    service = JellyfinService("http://localhost:8096", "test-key", timeout=10)
    service._http = AsyncMock()
    service._http.get = AsyncMock(return_value=_mock_response(404))

    with pytest.raises(NotFoundError):
        await service._get("/Items/missing")


@pytest.mark.asyncio
async def test_get_item_uses_user_scoped_path():
    service = JellyfinService("http://localhost:8096", "test-key", timeout=10)
    service.get_default_user_id = AsyncMock(return_value="user-1")
    service._get = AsyncMock(return_value={"Id": "abc", "Name": "Movie"})

    result = await service.get_item("abc")
    service._get.assert_awaited_with("/Users/user-1/Items/abc")
    assert result["Id"] == "abc"


@pytest.mark.asyncio
async def test_get_default_user_id_caches_result():
    service = JellyfinService("http://localhost:8096", "test-key", timeout=10)
    service.get_users = AsyncMock(return_value=[{"Id": "user-1", "Name": "admin"}])

    user_id = await service.get_default_user_id()
    assert user_id == "user-1"
    assert service._default_user_id == "user-1"

    await service.get_default_user_id()
    service.get_users.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_recent_resolves_user_id():
    service = JellyfinService("http://localhost:8096", "test-key", timeout=10)
    service.get_default_user_id = AsyncMock(return_value="user-1")
    service._get = AsyncMock(return_value=[{"Id": "item1"}])

    await service.get_recent("lib1", limit=5)
    service._get.assert_awaited_with("/Users/user-1/Items/Latest", ParentId="lib1", Limit=5)


@pytest.mark.asyncio
async def test_get_libraries_returns_list():
    service = JellyfinService("http://localhost:8096", "test-key", timeout=10)
    service._get = AsyncMock(return_value=[{"Name": "Movies"}])

    libs = await service.get_libraries()
    assert len(libs) == 1
    assert libs[0]["Name"] == "Movies"
