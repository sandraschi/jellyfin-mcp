# Plex → Jellyfin Migration

Migrate your media library from Plex to Jellyfin with watch state preservation.

## Why Migrate?

| Plex | Jellyfin |
|------|----------|
| Hardware transcoding: $120 | **Free** |
| DVR / Live TV: $5/mo | **Free** |
| Offline sync: Plex Pass | **Free** |
| Plugins: Deprecated | **100+ plugins** |
| Telemetry: Mandatory | **None** |
| Cloud dependency: Required | **Fully air-gappable** |

## Migration Steps

### 1. Install Jellyfin Alongside Plex

Different port (8096 vs Plex's 32400), no conflict. Both can access the same media files simultaneously.

### 2. Export Plex Data

Via plex-mcp:
```python
await plex_integration(operation="export", export_path="/backup/plex_export.json")
```

### 3. Import into Jellyfin

Via jellyfin-mcp:
```python
await jellyfin_integration(operation="import_plex", source_path="/backup/plex_export.json")
```

This maps:
- Plex library sections → Jellyfin media folders
- Plex collections → Jellyfin collections
- Plex playlists → Jellyfin playlists

### 4. Sync Watch States

```python
await jellyfin_integration(operation="sync_watchstate", source="plex")
```

Preserves: watched/unwatched status, playback position (partial watches).

### 5. Verify

```python
# Check all media detected
await jellyfin_library(operation="stats")

# Verify watch states
await jellyfin_media(operation="get_recent", limit=10)

# Check server health
await jellyfin_server(operation="status")
```

### 6. Decommission Plex

Once satisfied, stop or uninstall Plex Media Server.

## Manual Migration (Without MCP)

If you prefer manual migration:

1. **Media files** — Jellyfin reads the same files. No conversion needed.
2. **Metadata** — Jellyfin re-fetches from TMDB/TVDB. Cleaner than importing Plex's.
3. **Watch history** — Use [Trakt](https://trakt.tv) as intermediary (both Plex and Jellyfin have Trakt plugins).
4. **Users** — Recreate in Jellyfin. Jellyfin's user system is simpler (no Plex Home complexity).

## Directory Structure

Both Plex and Jellyfin use the same naming conventions. Your existing folder structure works:

```
/media/
├── movies/
│   └── Inception (2010)/Inception.2010.1080p.mkv
└── tv/
    └── Breaking Bad/Season 1/S01E01.mkv
```
