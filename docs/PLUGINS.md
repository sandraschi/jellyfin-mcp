# Plugin Management

Jellyfin++ exclusive. Unlike Plex (which deprecated plugins entirely), Jellyfin has a thriving 100+ plugin ecosystem. jellyfin-mcp wraps the full plugin lifecycle.

## MCP Tool

```python
# Browse catalog
await jellyfin_plugin(operation="catalog")

# List installed
await jellyfin_plugin(operation="list")

# Install
await jellyfin_plugin(operation="install", plugin_id="intro-skipper")

# Enable / disable
await jellyfin_plugin(operation="enable", plugin_id="intro-skipper")
await jellyfin_plugin(operation="disable", plugin_id="intro-skipper")

# Configure
await jellyfin_plugin(operation="configure", plugin_id="intro-skipper", config={"MaxIntroDuration": 120})

# Update
await jellyfin_plugin(operation="update", plugin_id="intro-skipper")

# Uninstall
await jellyfin_plugin(operation="uninstall", plugin_id="intro-skipper")
```

## Top Plugins

| Plugin | ID | Category |
|--------|-----|----------|
| Intro Skipper | `intro-skipper` | Media Enhancement |
| Open Subtitles | `opensubtitles` | Subtitles |
| Subtitle Extract | `subtitle-extract` | Subtitles |
| Theme Songs | `theme-songs` | Media Enhancement |
| LDAP Auth | `ldap-auth` | Authentication |
| Reports | `reports` | Reporting |
| Merge Versions | `merge-versions` | Organization |
| Trakt | `trakt` | Integration |
| TMDb Box Sets | `tmdb-box-sets` | Collections |
| AniDB | `anidb` | Metadata |

## Webapp

Visit `/plugins` in the webapp:
- **Installed tab** — current plugins with enable/disable toggles
- **Catalog tab** — browsable plugin catalog with descriptions, categories, install buttons
- **Configure** — click any plugin to open config panel

## How It Works

```
jellyfin_plugin("install") → PluginService
  → Fetch Jellyfin plugin manifest (GitHub raw JSON)
  → POST /Plugins/{id}/Install to Jellyfin server
  → Plugin .dll downloaded to config/plugins/
  → Server restart may be required
```

## Plugin Catalog Source

Jellyfin maintains an official plugin manifest:
`https://raw.githubusercontent.com/jellyfin/jellyfin-plugin-manifest/master/manifest.json`

The `PluginService` caches this catalog locally (memory, per-session).
