"""Integration tests — Jellyfin users and sessions."""

import pytest

from tests.conftest import tool_content

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_get_users(live_jellyfin_service):
    users = await live_jellyfin_service.get_users()
    assert isinstance(users, list)
    assert len(users) >= 1


@pytest.mark.asyncio
async def test_default_user_id(live_jellyfin_service):
    user_id = await live_jellyfin_service.get_default_user_id()
    assert isinstance(user_id, str)
    assert len(user_id) > 0


@pytest.mark.asyncio
async def test_user_tool_list(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.user import jellyfin_user

    result = tool_content(await jellyfin_user(operation="list"))
    assert result["success"] is True
    assert len(result["data"]) >= 1


@pytest.mark.asyncio
async def test_playback_sessions(live_jellyfin_service):
    sessions = await live_jellyfin_service.get_sessions()
    assert isinstance(sessions, list)


@pytest.mark.asyncio
async def test_playback_tool_list_sessions(live_jellyfin_service):
    from jellyfin_mcp.tools.portmanteau.playback import jellyfin_playback

    result = tool_content(await jellyfin_playback(operation="list_sessions"))
    assert result["success"] is True
    assert isinstance(result["data"], list)
