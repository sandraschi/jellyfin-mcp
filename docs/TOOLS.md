# MCP Tools Reference

22 portmanteau tools, ~120+ operations. All tools return `{"success": bool, "data": ..., "operation": str}`.

## Core Tools

### jellyfin_library
15 operations: `list`, `get`, `create`, `update`, `delete`, `scan`, `refresh`, `stats`, `cleanup`, `add_path`, `remove_path`, `optimize`, `empty_trash`, `reorder`, `configure`

```python
await jellyfin_library(operation="list")
await jellyfin_library(operation="scan", library_id="abc123", force=True)
await jellyfin_library(operation="create", name="Anime", library_type="show", path="/media/anime")
```

### jellyfin_media
10 operations: `browse`, `search`, `get`, `get_recent`, `get_recommended`, `similar`, `stream_info`, `refresh`, `update`, `delete`

```python
await jellyfin_media(operation="browse", library_id="abc123", sort_by="DateCreated", limit=50)
await jellyfin_media(operation="get", item_id="def456")
await jellyfin_media(operation="get_recent", library_id="abc123", limit=24)
```

### jellyfin_search
6 operations: `search`, `advanced`, `people`, `studios`, `suggest`, `saved`

```python
await jellyfin_search(operation="search", query="inception")
await jellyfin_search(operation="advanced", query="comedy", year=2023, types="Movie")
await jellyfin_search(operation="people", person="Christopher Nolan")
```

### jellyfin_playback
12 operations: `list_sessions`, `play`, `pause`, `stop`, `resume`, `seek`, `skip_next`, `skip_prev`, `set_volume`, `set_subtitle`, `set_audio`, `set_quality`

```python
await jellyfin_playback(operation="list_sessions")
await jellyfin_playback(operation="play", session_id="s1", item_ids=["abc123"])
await jellyfin_playback(operation="pause", session_id="s1")
await jellyfin_playback(operation="seek", session_id="s1", ticks=36000000000)
```

### jellyfin_user
10 operations: `list`, `get`, `create`, `update`, `delete`, `policy`, `password`, `sessions`, `activity`, `devices`

```python
await jellyfin_user(operation="list")
await jellyfin_user(operation="create", name="family", password="secret")
await jellyfin_user(operation="policy", user_id="u1", policy={"IsAdministrator": False})
```

## Advanced Tools

### jellyfin_playlist
9 ops: `list`, `get`, `create`, `update`, `delete`, `add_items`, `remove_items`, `reorder`, `share`

### jellyfin_collections
7 ops: `list`, `get`, `create`, `update`, `delete`, `add_items`, `remove_items`

### jellyfin_metadata
10 ops: `get`, `update`, `refresh`, `identify`, `images`, `backdrops`, `providers`, `lock`, `unlock`, `fetch`

### jellyfin_server
10 ops: `status`, `info`, `health`, `logs`, `restart`, `shutdown`, `updates`, `tasks`, `task_run`, `transcode_queue`

### jellyfin_streaming
8 ops: `sessions`, `clients`, `transcode`, `bandwidth`, `direct_play`, `remote`, `lan`, `kill`

## Jellyfin++ Unique Tools

### jellyfin_plugin
8 ops: `catalog`, `list`, `install`, `uninstall`, `enable`, `disable`, `configure`, `update`

```python
await jellyfin_plugin(operation="catalog")
await jellyfin_plugin(operation="install", plugin_id="intro-skipper")
await jellyfin_plugin(operation="enable", plugin_id="intro-skipper")
```

### jellyfin_livetv
8 ops: `channels`, `guide`, `recordings`, `schedule`, `tuners`, `epg_refresh`, `delete_recording`, `manage`

```python
await jellyfin_livetv(operation="channels")
await jellyfin_livetv(operation="guide", channel_id="ch1")
await jellyfin_livetv(operation="schedule", program_id="p1")
```

### jellyfin_subtitle
7 ops: `search`, `download`, `upload`, `delete`, `sync`, `offset`, `provider_config`

### jellyfin_ffmpeg
6 ops: `profiles`, `performance`, `detect_hw`, `path`, `test`, `benchmarks`

## AI / Enrichment Tools

### jellyfin_enrichment
6 ops: `tmdb`, `wikipedia`, `musicbrainz`, `omdb`, `tvdb`, `batch`

### jellyfin_rag
5 ops: `sync`, `search`, `status`, `reindex`, `purge`

```python
await jellyfin_rag(operation="sync")
await jellyfin_rag(operation="search", query="dark sci-fi with strong female lead", limit=10)
```

### jellyfin_recommend
5 ops: `similar`, `genre`, `director`, `actor`, `history`

### jellyfin_reporting
8 ops: `stats`, `popular`, `recent`, `genres`, `resolution`, `codec`, `user_activity`, `export`

## Utility Tools

### jellyfin_help
6 ops: `discover`, `tool_help`, `status`, `tips`, `quickstart`, `faq`

### jellyfin_integration
5 ops: `export_plex`, `import_plex`, `sync_watchstate`, `backup`, `restore`

### jellyfin_arr_stack
6 ops: `status`, `queue`, `history`, `radarr`, `sonarr`, `lidarr`

### jellyfin_agentic
3 ops: `workflow`, `natural_query`, `batch`

```python
await jellyfin_agentic(operation="workflow", prompt="Find sci-fi movies I haven't watched, check IMDb ratings, add top 5 to playlist")
```
