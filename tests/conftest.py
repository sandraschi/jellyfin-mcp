"""Test configuration and shared fixtures."""

import pytest


@pytest.fixture
def mock_config():
    """Mock JellyfinConfig for testing."""
    from jellyfin_mcp.config import JellyfinConfig

    return JellyfinConfig(
        server_url="http://localhost:8096",
        api_key="test-api-key",
        timeout=10,
        ws_enabled=False,
    )


@pytest.fixture
def mock_jellyfin_service():
    """Mock JellyfinService that returns canned responses."""
    from unittest.mock import AsyncMock

    service = AsyncMock()
    service.get_libraries = AsyncMock(return_value=[
        {"Id": "lib1", "Name": "Movies", "CollectionType": "movies", "ItemCount": 42},
        {"Id": "lib2", "Name": "TV Shows", "CollectionType": "tvshows", "ItemCount": 15},
    ])
    service.get_server_info = AsyncMock(return_value={
        "Version": "10.11.9", "OperatingSystem": "Windows", "Id": "server1",
    })
    service.get_sessions = AsyncMock(return_value=[])
    service.get_plugins = AsyncMock(return_value=[])
    service.get_items = AsyncMock(return_value={
        "Items": [
            {"Id": "item1", "Name": "Test Movie", "Type": "Movie", "ProductionYear": 2024},
        ],
        "TotalRecordCount": 1,
    })
    service.get_item = AsyncMock(return_value={
        "Id": "item1", "Name": "Test Movie", "Type": "Movie", "ProductionYear": 2024,
    })
    return service
