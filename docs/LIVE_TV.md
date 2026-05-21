# Live TV & DVR

Jellyfin++ exclusive. Unlike Plex (where Live TV requires Plex Pass), Jellyfin provides free DVR with HDHomeRun, IPTV (M3U), XML TV guide data, and TVHeadend.

## Supported Tuners

| Tuner | Setup |
|-------|-------|
| HDHomeRun | Auto-discovered via UDP broadcast |
| IPTV (M3U) | Provide M3U playlist URL |
| TVHeadend | Connect to TVHeadend server |
| XML TV | EPG guide data URL |

## MCP Tool

```python
# List channels
await jellyfin_livetv(operation="channels")
# → returns all configured channels with numbers and names

# View EPG guide
await jellyfin_livetv(operation="guide")
await jellyfin_livetv(operation="guide", channel_id="ch1")
# → program schedule with start/end times, titles, descriptions

# List recordings
await jellyfin_livetv(operation="recordings")
await jellyfin_livetv(operation="recordings", status="completed")

# Schedule recording
await jellyfin_livetv(operation="schedule", program_id="prog123")

# Cancel recording
await jellyfin_livetv(operation="delete_recording", recording_id="rec456")

# List tuners
await jellyfin_livetv(operation="tuners")

# Refresh guide data
await jellyfin_livetv(operation="epg_refresh")

# Manage DVR settings
await jellyfin_livetv(operation="manage")
```

## Webapp

Visit `/livetv` in the webapp:
- **EPG Grid** — time slots (horizontal) × channels (vertical), color-coded by genre
- **Current program** highlighted, upcoming programs listed
- **Record** button on any program
- **Recordings tab** — completed, in-progress, scheduled

## Setup Jellyfin Live TV

Before using MCP tools, configure a tuner in Jellyfin:

1. Jellyfin Dashboard → **Live TV**
2. Add tuner device (HDHomeRun auto-detected, or paste M3U URL)
3. Add EPG source (XML TV URL or built-in guide)
4. Map channels
5. Refresh guide data

Once configured, all `jellyfin_livetv` operations work immediately.
