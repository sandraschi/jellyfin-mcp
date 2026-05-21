# Tauri 2.0 Native Desktop App

jellyfin-mcp ships with a Tauri 2.0 native wrapper — a 15 MB installer that bundles the entire stack: Rust shell, React frontend, Python backend (PyInstaller sidecar).

## Why Tauri?

| | Electron | Tauri 2.0 |
|---|---|---|
| Bundle size | ~200 MB | **~15 MB** |
| Memory (idle) | ~300 MB | **~50 MB** |
| Backend | Node.js | **Rust** |
| System tray | Plugin | **Built-in** |
| Auto-updater | Plugin | **Built-in** |

## Build

```powershell
# One command — builds frontend, compiles Python to .exe, bundles installer
just build-native

# Installer lands at:
# native/target/release/bundle/nsis/Jellyfin MCP_0.1.0_x64-setup.exe
```

## What the Installer Contains

```
15 MB .exe installer
  ├── Rust shell (WebView2 window, system tray, lifecycle)
  ├── React webapp (bundled, no Node.js needed)
  └── Python backend (PyInstaller-compiled .exe, no Python needed)
```

User double-clicks the installer → everything works. No Python, Node.js, or git required.

## Architecture

```
Tauri window (WebView2)
  ↓ loads
React webapp (from native/target/)
  ↓ fetches /api/*
Python backend (PyInstaller sidecar .exe)
  ↓ HTTP
Jellyfin Server (local or remote, port 8096)
```

## Sidecar Lifecycle

- Tauri spawns the Python backend as a sidecar process on app start
- Backend runs on localhost:10934
- WebView loads webapp on localhost:10935 (or bundled build)
- On app exit, sidecar is killed cleanly

## Dev Mode

```powershell
# Debug build (no PyInstaller, uses dev server)
just build-native-debug
```

Opens with DevTools. Frontend loads from Next.js dev server at `http://localhost:10935`.

## CI/CD (Future)

When shipping regularly, add `.github/workflows/native.yml` with:
- `tauri-apps/setup-tauri@v2`
- Python build (PyInstaller)
- Frontend build (Next.js)
- Tauri bundler
- Upload installer artifact

Currently manual: `just build-native` → upload `.exe` to GitHub Releases.
