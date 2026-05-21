# Architecture

Short overview. Full 340-line architecture doc in [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs/blob/main/projects/jellyfin-mcp/ARCHITECTURE.md).

## System Diagram

```
┌─────────────────┐     ┌──────────────────┐
│  Claude Desktop  │     │  Web Browser      │
│  (MCP Client)    │     │  (React Dashboard)│
└────────┬────────┘     └────────┬─────────┘
         │ MCP (stdio/http)      │ HTTP / WS
┌────────▼──────────────────────▼──────────┐
│           jellyfin-mcp Server             │
│                                           │
│  Transport  STDIO | HTTP | SSE | WS       │
│  FastMCP    app.py — lifespan, sampling   │
│  Tools      22 portmanteau (120+ ops)     │
│  Services   JellyfinService, WS, Plugin   │
│  Webapp     FastAPI 10934 + Next.js 10935  │
└──────────────────┬───────────────────────┘
                   │ HTTP + WebSocket
┌──────────────────▼───────────────────────┐
│        Jellyfin Server (port 8096)        │
│        REST API + WebSocket events        │
└──────────────────────────────────────────┘
```

## Key Components

| Layer | Location | Purpose |
|-------|----------|---------|
| MCP Instance | `src/jellyfin_mcp/app.py` | FastMCP 3.2+ with lifespan, sampling, resources |
| Transport | `src/jellyfin_mcp/transport.py` | Unified STDIO/HTTP/SSE entry |
| Tools | `src/jellyfin_mcp/tools/portmanteau/` | 22 `@mcp.tool()` decorators |
| JellyfinService | `src/jellyfin_mcp/services/jellyfin_service.py` | REST API wrapper (httpx, executor pattern) |
| WebSocketService | `src/jellyfin_mcp/services/websocket_service.py` | Real-time event bridge (aiohttp) |
| PluginService | `src/jellyfin_mcp/services/plugin_service.py` | Plugin catalog, install lifecycle |
| RAGService | `src/jellyfin_mcp/services/rag_service.py` | LanceDB + sentence-transformers |
| EnrichmentService | `src/jellyfin_mcp/services/enrichment_service.py` | TMDB, Wikipedia augmentation |
| Prefabs | `src/jellyfin_mcp/prefabs.py` | Interactive UI cards via prefab_ui |
| Backend | `webapp/backend/app/main.py` | FastAPI, lazy FastMCP mount |
| Frontend | `webapp/frontend/` | Next.js 15.2, 12 pages, dark theme |
| Native | `native/` | Tauri 2.0, sidecar, installer |

## Data Flow

```
Claude → "list my movies"
  → jellyfin_media(operation="browse", ...)
  → JellyfinService.get_items(parent_id="...")
  → httpx → http://jellyfin:8096/Items?ParentId=...
  → Jellyfin → { Items: [...], TotalRecordCount: 42 }
  → ToolResult(content={"success": True, "data": [...]})
  → Claude
```

## Ports

| Port | Service |
|---|---|
| 10934 | Backend — FastAPI + MCP + WebSocket |
| 10935 | Frontend — Next.js dev + HMR |
| 8096 | Jellyfin Server (external) |

## Comparison with plex-mcp

| | plex-mcp | jellyfin-mcp |
|---|---|---|
| Tools | 20 portmanteau | **22 portmanteau** |
| Real-time | Polling only | **WebSocket event bus** |
| Plugin mgmt | N/A (deprecated) | **First-class tools + UI** |
| Live TV | N/A | **EPG grid + DVR** |
| Auth | Cloud (plex.tv) | **Local (air-gappable)** |
| Ports | 10740/10741 | 10934/10935 |
