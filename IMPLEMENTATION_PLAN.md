# jellyfin-mcp — Implementation Plan

**Start:** 2026-05-21 | **Target Completion:** 2026-05-28 (4 weeks)
**Reference Architecture:** plex-mcp (D:\Dev\repos\plex-mcp)

---

## Phase 1: Repo Scaffold 

### Files to Create
- [x] `pyproject.toml` — uv + hatchling build, FastMCP 3.2+, jellyfin-apiclient-python
- [x] `justfile` — install, start, webapp, lint, fmt, fix, test, e2e, ci, build, clean
- [x] `.gitignore` — python, node, tauri patterns
- [x] `.env.example` — JELLYFIN_URL, JELLYFIN_API_KEY, sampling config
- [x] `src/jellyfin_mcp/__init__.py` — package init, version export
- [x] `src/jellyfin_mcp/__main__.py` — `python -m jellyfin_mcp` entry
- [x] `src/jellyfin_mcp/config.py` — JellyfinConfig (Pydantic v2 BaseSettings), env loading
- [x] `src/jellyfin_mcp/app.py` — FastMCP instance, lifespan, resources, prompts, http_app()
- [x] `src/jellyfin_mcp/transport.py` — Unified STDIO/HTTP/SSE transport
- [x] `src/jellyfin_mcp/server.py` — Main entry point, tool imports, ASGI app export
- [x] `src/jellyfin_mcp/utils/__init__.py` — Logger, error helpers
- [x] `src/jellyfin_mcp/prefabs.py` — Prefab card builders (jellyfin-specific)
- [x] `run_server.py` — PyInstaller entry point

## Phase 2: Service Layer

### Files to Create
- [x] `src/jellyfin_mcp/services/__init__.py`
- [x] `src/jellyfin_mcp/services/base.py` — BaseService, executor pattern, error hierarchy
- [x] `src/jellyfin_mcp/services/jellyfin_service.py` — Core REST API wrapper (all endpoints)
- [x] `src/jellyfin_mcp/services/websocket_service.py` — Real-time event bridge
- [x] `src/jellyfin_mcp/services/plugin_service.py` — Plugin lifecycle management
- [x] `src/jellyfin_mcp/services/enrichment_service.py` — TMDB, MusicBrainz, Wikipedia
- [x] `src/jellyfin_mcp/services/rag_service.py` — LanceDB semantic search

## Phase 3: MCP Portmanteau Tools

### Core Tools (Phase 3a)
- [x] `tools/portmanteau/__init__.py` — Tool registration hub
- [x] `tools/portmanteau/library.py` — jellyfin_library (15 ops)
- [x] `tools/portmanteau/media.py` — jellyfin_media (10 ops)
- [x] `tools/portmanteau/search.py` — jellyfin_search (6 ops)
- [x] `tools/portmanteau/playback.py` — jellyfin_playback (12 ops)
- [x] `tools/portmanteau/user.py` — jellyfin_user (10 ops)

### Advanced Tools (Phase 3b)
- [x] `tools/portmanteau/playlist.py` — jellyfin_playlist (9 ops)
- [x] `tools/portmanteau/collections.py` — jellyfin_collections (7 ops)
- [x] `tools/portmanteau/metadata.py` — jellyfin_metadata (10 ops)
- [x] `tools/portmanteau/server.py` — jellyfin_server (10 ops)
- [x] `tools/portmanteau/streaming.py` — jellyfin_streaming (8 ops)
- [x] `tools/portmanteau/plugin.py` — jellyfin_plugin (8 ops)
- [x] `tools/portmanteau/arr_stack.py` — jellyfin_arr_stack (6 ops)
- [x] `tools/portmanteau/subtitle.py` — jellyfin_subtitle (7 ops)
- [x] `tools/portmanteau/livetv.py` — jellyfin_livetv (8 ops)
- [x] `tools/portmanteau/ffmpeg.py` — jellyfin_ffmpeg (6 ops)
- [x] `tools/portmanteau/enrichment.py` — jellyfin_enrichment (6 ops)
- [x] `tools/portmanteau/rag.py` — jellyfin_rag (5 ops)
- [x] `tools/portmanteau/reporting.py` — jellyfin_reporting (8 ops)
- [x] `tools/portmanteau/recommend.py` — jellyfin_recommend (5 ops)
- [x] `tools/portmanteau/help.py` — jellyfin_help (6 ops)
- [x] `tools/portmanteau/integration.py` — jellyfin_integration (5 ops)
- [x] `tools/agentic.py` — jellyfin_agentic (3 ops, dynamic registration)

## Phase 4: Webapp Backend

### Files to Create
- [x] `webapp/backend/app/__init__.py`
- [x] `webapp/backend/app/main.py` — FastAPI app, lazy MCP mount, CORS
- [x] `webapp/backend/app/config.py` — Backend config
- [x] `webapp/backend/app/api/__init__.py`
- [x] `webapp/backend/app/api/library.py` — Library routes
- [x] `webapp/backend/app/api/media.py` — Media browse/detail routes
- [x] `webapp/backend/app/api/search.py` — Search routes
- [x] `webapp/backend/app/api/playback.py` — Playback routes
- [x] `webapp/backend/app/api/plugins.py` — Plugin management routes
- [x] `webapp/backend/app/api/users.py` — User management routes
- [x] `webapp/backend/app/api/streaming.py` — Streaming/sessions routes
- [x] `webapp/backend/app/api/server.py` — Server status routes
- [x] `webapp/backend/app/api/images.py` — Artwork proxy
- [x] `webapp/backend/app/api/rag.py` — Semantic search routes
- [x] `webapp/backend/app/api/llm.py` — Chat routes
- [x] `webapp/backend/app/api/settings.py` — Settings routes
- [x] `webapp/backend/app/api/help_api.py` — Help/tool reference
- [x] `webapp/backend/app/api/livetv.py` — Live TV routes (Jellyfin++ unique)
- [x] `webapp/backend/app/api/ws.py` — WebSocket proxy
- [x] `webapp/start.ps1` — Port cleanup + backend + frontend launcher
- [x] `webapp/start.bat` — Windows batch wrapper

## Phase 5: Webapp Frontend (Beautiful Jellyfin++ UI)

### Files to Create
- [x] `webapp/frontend/package.json` — Next.js 15.2, React 18, Tailwind 3, Lucide
- [x] `webapp/frontend/next.config.js` — API rewrites, image proxy
- [x] `webapp/frontend/tsconfig.json`
- [x] `webapp/frontend/tailwind.config.ts` — Jellyfin purple theme
- [x] `webapp/frontend/biome.json`
- [x] `webapp/frontend/app/globals.css` — Tailwind + custom jellyfin theme
- [x] `webapp/frontend/app/layout.tsx` — Root layout with sidebar
- [x] `webapp/frontend/app/page.tsx` — Overview dashboard
- [x] `webapp/frontend/app/libraries/page.tsx` — Library browser
- [x] `webapp/frontend/app/media/[type]/page.tsx` — Media grid (movies/shows/music)
- [x] `webapp/frontend/app/media/[type]/[id]/page.tsx` — Media detail page
- [x] `webapp/frontend/app/search/page.tsx` — Search page
- [x] `webapp/frontend/app/playback/page.tsx` — Live playback dashboard (WebSocket)
- [x] `webapp/frontend/app/plugins/page.tsx` — Plugin catalog & management
- [x] `webapp/frontend/app/livetv/page.tsx` — EPG grid + DVR (Jellyfin++ unique)
- [x] `webapp/frontend/app/users/page.tsx` — User management
- [x] `webapp/frontend/app/settings/page.tsx` — Settings page
- [x] `webapp/frontend/app/rag/page.tsx` — Semantic search
- [x] `webapp/frontend/app/chat/page.tsx` — LLM chat
- [x] `webapp/frontend/app/help/page.tsx` — Help/tool reference
- [x] `webapp/frontend/components/layout/sidebar.tsx` — Navigation sidebar
- [x] `webapp/frontend/components/layout/app-layout.tsx` — Layout wrapper
- [x] `webapp/frontend/components/media/MediaCard.tsx` — Poster card component
- [x] `webapp/frontend/components/media/MediaGrid.tsx` — Responsive grid
- [x] `webapp/frontend/components/media/MediaDetail.tsx` — Detail modal/page
- [x] `webapp/frontend/components/playback/SessionCard.tsx` — Active session display
- [x] `webapp/frontend/components/playback/TranscodeMonitor.tsx` — Real-time transcode
- [x] `webapp/frontend/components/plugins/PluginCard.tsx` — Plugin display
- [x] `webapp/frontend/components/livetv/EPGGrid.tsx` — TV guide grid
- [x] `webapp/frontend/utils/api.ts` — API fetch wrappers
- [x] `webapp/frontend/utils/jellyfin-media.ts` — Image URL helpers
- [x] `webapp/frontend/playwright.config.ts` — E2E test config

## Phase 6: Tauri Native Wrapper

### Files to Create
- [x] `native/Cargo.toml` — Rust deps (tauri 2, shell, fs, process)
- [x] `native/build.rs` — Tauri build script
- [x] `native/tauri.conf.json` — Window config, sidecar, plugins
- [x] `native/.gitignore` — binaries/, target/, gen/
- [x] `native/src/main.rs` — Entry point, sidecar launch, cleanup
- [x] `native/capabilities/default.json` — Tauri 2.0 permissions
- [x] `native/build.ps1` — Full build pipeline

## Phase 7: Quality & Tests

### Tasks
- [x] `tests/__init__.py`
- [x] `tests/test_portmanteau_library.py` — Library tool tests
- [x] `tests/test_portmanteau_media.py` — Media tool tests
- [x] `tests/conftest.py` — Fixtures (mock JellyfinService)
- [ ] Run `just lint` — Ruff + Biome
- [ ] Run `just fmt`
- [ ] Verify `uv sync` succeeds
- [ ] Verify `python -m jellyfin_mcp --stdio` starts
