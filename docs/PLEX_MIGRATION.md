# Plex → Jellyfin Migration

Complete walkthrough for switching from Plex to Jellyfin with minimal disruption.

## Why Bother?

| Plex | Jellyfin |
|------|----------|
| HW transcoding: $120/lifetime | **Free** |
| DVR / Live TV: $5/mo | **Free** |
| Offline sync: Plex Pass | **Free** |
| Plugins: Deprecated 2024 | **100+ active plugins** |
| Telemetry: Cannot fully disable | **Zero telemetry** |
| Auth: Requires plex.tv cloud | **Fully local, air-gappable** |
| Ads: Plex Movies & TV | **None** |
| API docs: Partial | **Full OpenAPI/Swagger** |
| Intro skip: Plex Pass | **Free plugin** |

## Migration Strategies

### Strategy A: Side-by-Side (Recommended)

Run both servers simultaneously, point them at the same media folders. Migrate users gradually. No downtime.

**Pros:** Zero risk, can fall back to Plex anytime, compare side-by-side
**Cons:** Both servers consume resources during transition

### Strategy B: Cutover

Install Jellyfin, configure libraries, verify, then shut down Plex.

**Pros:** Fast, clean
**Cons:** Users lose access during transition, no fallback

### Strategy C: Fresh Start

Install Jellyfin, let it re-scan everything from scratch. Don't migrate anything.

**Pros:** Cleanest metadata, no legacy cruft
**Cons:** Lose watch history, playlists, collections, user accounts

---

## Strategy A: Side-by-Side Walkthrough

### Phase 1: Install Jellyfin

Jellyfin runs on port 8096 (Plex uses 32400). No conflict.

```powershell
# See docs/JELLYFIN_SERVER.md for full install guide
# Quick Docker:
docker run -d --name jellyfin \
  -p 8096:8096 \
  -v /opt/jellyfin/config:/config \
  -v /mnt/media:/media:ro \
  jellyfin/jellyfin:latest
```

Open `http://localhost:8096` → complete setup wizard → add your media folders.

### Phase 2: Configure Libraries Mirroring Plex

Map Plex libraries to Jellyfin libraries:

| Plex Library | Type | Jellyfin Library | Content Type | Media Path |
|---|---|---|---|---|
| Movies | film | Movies | Movies | same as Plex |
| TV Shows | show | TV Shows | Shows | same as Plex |
| Music | artist | Music | Music | same as Plex |
| Photos | photo | Photos | Photos | same as Plex |
| DVR | — | Recordings | — | Jellyfin handles via Live TV |
| 4K Movies | film | Movies (4K) | Movies | separate 4K path |

**Point at the same files.** Both servers can read the same media directories simultaneously — there's no locking or database conflict. Jellyfin scans the filesystem independently.

### Phase 3: Export Plex Data via plex-mcp

If you have [plex-mcp](https://github.com/sandraschi/plex-mcp) installed:

```python
# Export libraries, collections, playlists
await plex_integration(operation="export", export_path="./plex_export.json")

# The export contains:
# - Library names, types, folder paths
# - Collections with member item names
# - Playlists with track/items list
# - User watch states
```

**Without plex-mcp:** you can still migrate. Plex stores watch state in its SQLite database. Third-party tools like [PlexTraktSync](https://github.com/Taxel/PlexTraktSync) can sync via Trakt as intermediary.

### Phase 4: Create Jellyfin Libraries to Match

Use jellyfin-mcp or Jellyfin web UI. Example via MCP:

```python
# Via jellyfin-mcp
await jellyfin_library(operation="create",
    name="Movies",
    library_type="movie",
    path="/mnt/media/movies")

await jellyfin_library(operation="create",
    name="TV Shows",
    library_type="show",
    path="/mnt/media/tv")

await jellyfin_library(operation="create",
    name="Music",
    library_type="music",
    path="/mnt/media/music")
```

Jellyfin starts scanning immediately. This can take hours for large libraries. Monitor:

```python
await jellyfin_library(operation="stats")
```

### Phase 5: Migrate Watch State

Watch history is the most valuable data to migrate. Three approaches:

**Option A: Via MCP (plex-mcp → jellyfin-mcp)**
```python
# Export from Plex
watch_data = await plex_user(operation="export_watchstate")

# Import to Jellyfin
await jellyfin_integration(operation="sync_watchstate",
    source="plex",
    data=watch_data)
```

**Option B: Via Trakt.tv (Manual)**

1. Install Trakt plugin on **Plex**: UAS → Trakt → authenticate
2. Install Trakt plugin on **Jellyfin**: Dashboard → Plugins → Catalog → Trakt → Install
3. Sync Plex → Trakt (watched history uploads)
4. Sync Trakt → Jellyfin (downloads watched status)
5. Remove Trakt plugins when done (optional)

**Option C: Manual Re-watch Marking**

For small libraries (< 200 items), just re-mark as watched in Jellyfin:

```python
# Mark individual items watched via MCP
await jellyfin_media(operation="update", item_id="abc123",
    metadata={"UserData": {"Played": True}})
```

### Phase 6: Migrate Collections & Playlists

**Collections:** Jellyfin re-detects collections from TMDb automatically if you enable the TMDb Box Sets plugin. For manual collections:

```python
# Recreate collection
await jellyfin_collections(operation="create", name="Marvel Cinematic Universe")
await jellyfin_collections(operation="add_items",
    collection_id="coll1",
    item_ids=["ironman", "hulk", "thor", ...])
```

**Playlists:** Manual recreation or via MCP export/import. Note: playlist item matching relies on media titles — if titles differ between Plex and Jellyfin metadata, manual correction needed.

### Phase 7: Recreate Users

```python
# Create user accounts
await jellyfin_user(operation="create", name="Family")
await jellyfin_user(operation="create", name="Kids")

# Set permissions
await jellyfin_user(operation="policy", user_id="u1", policy={
    "IsAdministrator": False,
    "EnableMediaPlayback": True,
    "EnableLiveTvAccess": True,
})
```

Jellyfin's user system is simpler than Plex Home:
- No "Plex Home" concept — users are independent
- No managed user tiers
- Permissions are straightforward enable/disable flags
- Each user has their own API key

### Phase 8: Configure Hardware Acceleration

Free on Jellyfin. Configure in Dashboard → Playback:

```python
# Check what's detected
await jellyfin_ffmpeg(operation="detect_hw")
# → {"intel_qsv": true, "nvidia_nvenc": false, "vaapi": true}
```

Enable the appropriate option in Jellyfin Dashboard. Test:

```python
await jellyfin_ffmpeg(operation="test")
```

### Phase 9: Install Essential Plugins

```python
# Intro Skip
await jellyfin_plugin(operation="install", plugin_id="intro-skipper")
await jellyfin_plugin(operation="enable", plugin_id="intro-skipper")

# Subtitles
await jellyfin_plugin(operation="install", plugin_id="opensubtitles")
await jellyfin_plugin(operation="enable", plugin_id="opensubtitles")

# Collections
await jellyfin_plugin(operation="install", plugin_id="tmdb-box-sets")
await jellyfin_plugin(operation="enable", plugin_id="tmdb-box-sets")

# Theme Songs
await jellyfin_plugin(operation="install", plugin_id="theme-songs")
await jellyfin_plugin(operation="enable", plugin_id="theme-songs")
```

### Phase 10: Client App Transition

Have users install Jellyfin clients:

| Platform | App |
|----------|-----|
| Android | Jellyfin (Play Store / F-Droid) |
| iOS | Jellyfin Mobile (App Store) |
| Android TV / Fire TV | Jellyfin for Android TV |
| Roku | Jellyfin (Roku Channel Store) |
| WebOS (LG TV) | Jellyfin (LG Content Store) |
| Tizen (Samsung TV) | Jellyfin (Samsung App Store) |
| Xbox | Jellyfin (Xbox Store) |
| Kodi | Jellyfin for Kodi addon |
| Infuse (Apple) | Supports Jellyfin natively |
| Web browser | `http://your-server:8096` |

Server URL for clients: `http://your-server-ip:8096`

### Phase 11: Decommission Plex

Once all users are on Jellyfin and everything verified:

```powershell
# Windows
Stop-Service "Plex Media Server"
Set-Service "Plex Media Server" -StartupType Disabled

# Docker
docker stop plex && docker rm plex

# Linux
sudo systemctl stop plexmediaserver
sudo systemctl disable plexmediaserver
```

**Keep Plex installed for 2-4 weeks** as fallback. If anything unexpected comes up, Plex is still there.

---

## Common Pitfalls

### Metadata Mismatch

Jellyfin and Plex may identify the same file differently (different TMDb ID, different title). This is normal for the first scan. Fix mismatched items:

```python
# Identify correct match
await jellyfin_metadata(operation="identify", item_id="abc", search_name="Inception", year=2010)
```

### TV Show Season Matching

If a show's seasons are split across multiple folders, Jellyfin handles this differently than Plex. Ensure all seasons are under one show folder:

```
# Works:
/TV Shows/Show Name (YYYY)/Season 01/
/TV Shows/Show Name (YYYY)/Season 02/

# Doesn't work well:
/TV/Season 1/Show Name/
/TV/Season 2/Show Name/
```

### Special Episodes (Specials)

Jellyfin expects specials in `Season 00/` (same as Plex):
```
/Show Name (YYYY)/Season 00/S00E01 - Special Name.mkv
```

### Music Library Differences

Jellyfin uses MusicBrainz by default (Plex uses Gracenote). Metadata may differ. If you have well-tagged FLAC/MP3 files (with embedded tags), prefer "Read embedded tags" in Jellyfin's music library settings.

### FFmpeg Path

Jellyfin needs ffmpeg for transcoding. On Windows, install [jellyfin-ffmpeg](https://github.com/jellyfin/jellyfin-ffmpeg/releases). On Docker, it's included. On Linux: `sudo apt install jellyfin-ffmpeg6`.

---

## Migration Checklist

- [ ] Jellyfin installed (different port, no Plex conflict)
- [ ] Media libraries created pointing at same folders
- [ ] Scan complete (all media detected)
- [ ] Metadata verified (spot-check 20 items)
- [ ] Hardware transcoding configured and tested
- [ ] Watch states migrated (via MCP, Trakt, or manual)
- [ ] Collections recreated
- [ ] User accounts recreated with permissions
- [ ] Essential plugins installed
- [ ] Client apps tested on each platform
- [ ] Remote access configured (reverse proxy or Tailscale)
- [ ] Plex kept as fallback for 2-4 weeks
- [ ] Plex decommissioned
