"""Pydantic v2 data models for jellyfin-mcp."""

from pydantic import BaseModel, Field


class MediaItem(BaseModel):
    """A Jellyfin media item (movie, episode, track, etc.)."""

    id: str = Field(default="")
    name: str = Field(default="")
    type: str = Field(default="")  # Movie, Series, Episode, Audio, etc.
    production_year: int | None = Field(default=None)
    community_rating: float | None = Field(default=None)
    run_time_ticks: int | None = Field(default=None)
    genres: list[str] = Field(default_factory=list)
    overview: str | None = Field(default=None)


class LibrarySection(BaseModel):
    """A Jellyfin library section."""

    id: str = Field(default="")
    name: str = Field(default="")
    collection_type: str | None = Field(default=None)
    item_count: int = Field(default=0)
    locations: list[str] = Field(default_factory=list)


class PlaybackSession(BaseModel):
    """An active playback session."""

    session_id: str = Field(default="")
    user_name: str = Field(default="")
    client: str = Field(default="")
    device: str = Field(default="")
    now_playing: str | None = Field(default=None)
    state: str = Field(default="stopped")  # playing, paused, stopped
    position_ticks: int = Field(default=0)
    method: str = Field(default="")  # DirectPlay, Transcode


class PluginInfo(BaseModel):
    """A Jellyfin plugin."""

    id: str = Field(default="")
    name: str = Field(default="")
    version: str = Field(default="")
    description: str = Field(default="")
    status: str = Field(default="inactive")  # active, inactive, error
    category: str = Field(default="general")


class ServerInfo(BaseModel):
    """Jellyfin server information."""

    version: str = Field(default="")
    os: str = Field(default="")
    id: str = Field(default="")
    healthy: bool = Field(default=True)
