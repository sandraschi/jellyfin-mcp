# Webapp Guide

The jellyfin-mcp webapp is a beautiful dark-themed React dashboard at **http://localhost:10935** (backend at 10934).

## Start

```powershell
just webapp
# Backend: http://localhost:10934 (health: /health, docs: /docs)
# Frontend: http://localhost:10935
```

## Pages

### Overview Dashboard
Server health card (version, uptime), library stats grid, recent activity, quick scan/refresh actions.

### Library Browser (`/libraries`)
Card grid showing each library: name, type badge (Movie/Series/Music/Photo), item count, last scan date. Click to browse.

### Media Browser (`/media/Movies`, `/media/Series`, `/media/Music`)
Responsive poster grid with lazy loading. Filter by library, sort by name/date/rating. Hover effects reveal quick actions.

### Search (`/search`)
Full-text + advanced filter search across all libraries. Type to get suggestions, results with poster thumbnails.

### Playback Dashboard (`/playback`)
**Live WebSocket dashboard** — no polling. Shows:
- Active sessions with progress bars
- Now-playing artwork and metadata
- Transcode status (DirectPlay / DirectStream / Transcode)
- Per-session bandwidth
- Controls (play/pause/stop/seek)

Green dot indicator when WebSocket connected.

### Plugins (`/plugins`)
Jellyfin-exclusive. Browse catalog, install with one click, enable/disable toggles, configure per-plugin settings.

### Live TV (`/livetv`)
Jellyfin-exclusive. EPG grid (time slots × channels), current/upcoming programs, one-click recording, DVR manager.

### Users (`/users`)
List users, create accounts, edit permissions and policies, view active sessions, watch history.

### Settings (`/settings`)
Jellyfin URL and API key, LLM config (base URL, model, API key), RAG index path. Settings persist to `.env`.

### RAG Search (`/rag`)
Semantic search over indexed media metadata. "Sync metadata" button to index, search input for natural-language queries, results with relevance scores.

### AI Chat (`/chat`)
LLM-powered natural language interface. Select model, ask questions about your library, get recommendations. Uses JELLYFIN_SAMPLING_BASE_URL for LLM.

### Help (`/help`)
Full tool catalog with operation lists, quickstart walkthrough, FAQ.

## Theme

Dark purple/blue Jellyfin theme:
- Background: `#101020` (deep dark)
- Surfaces: `#1A1A2E`, `#252540`
- Accent: `#AA5CC3` (Jellyfin purple), `#00A4DC` (Jellyfin blue)
- Text: `#E2E8F0` (slate-200)
- Lucide icons throughout

## Architecture

```
Browser → localhost:10935 (Next.js) → rewrite /api/* → localhost:10934 (FastAPI)
         localhost:10935 → rewrite /ws → localhost:10934/ws (WebSocket proxy)
         localhost:10935 → rewrite /image/* → localhost:10934/image/* (artwork proxy)
```
