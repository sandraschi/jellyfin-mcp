
## [Unreleased] — 2026-06-14

### Added
- Tauri CORS: 	auri://localhost, http://tauri.localhost, https://tauri.localhost in CORS origins
- Tauri CORS: _TAURI env var toggle with llow_origin_regex for secure WebView access
- build.ps1: auto-copy NSIS installer to dist/ on build
- CUA-NSIS: config-driven smoke test (`scripts/cua-smoke.py`, `scripts/cua-nsis-config.json`)
- CUA-NSIS: `just build-native` + `just cua-nsis-test` recipes
- CUA-NSIS: 11-phase smoke (install, launch, WebView OCR, feature route, diagnostics, uninstall)
- CUA-NSIS: local certification — all 11 phases pass locally (2026-06-14)

### Changed
- CORS: llow_origins=["*"] → explicit origins list for Tauri webview compatibility
# Changelog — jellyfin-mcp

## 0.1.1 (2026-05-22)

- Complete Tauri 2.0 stack: PyInstaller one-file sidecar, build-sidecar.ps1, icon generator
- Next.js static export for Tauri; client-side dashboard pages; `API_BASE` for production
- Just recipes: `tauri-build`, `tauri-dev`, `tauri-sidecar`

## 0.1.0

- Initial release: 22 portmanteau MCP tools, Next.js webapp, WebSocket playback dashboard

