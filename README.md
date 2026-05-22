# jellyfin-mcp · Jellyfin++

FastMCP 3.2+ server + React webapp for [Jellyfin](https://jellyfin.org) Media Server — the open-source Plex alternative. 22 portmanteau MCP tools, plugin management, Live TV/DVR, WebSocket real-time dashboard, Tauri 2.0 native desktop wrapper.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE) [![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org) [![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Why Jellyfin over Plex?

| | Plex | Jellyfin |
|---|---|---|
| Hardware transcoding | $120/lifetime | **Free** |
| Plugins | Deprecated | **100+ plugins** |
| Real-time API | Polling only | **WebSocket events** |
| Live TV / DVR | Plex Pass | **Free** |
| Cloud dependency | plex.tv required | **Fully air-gappable** |
| Telemetry | Mandatory | **None** |

## Quickstart

```powershell
# Clone
git clone https://github.com/sandraschi/jellyfin-mcp
cd jellyfin-mcp

# Install
uv sync

# Configure
cp .env.example .env
# Edit .env with your Jellyfin URL and API key

# Start MCP server (STDIO for Claude Desktop)
uv run jellyfin-mcp

# Or start the webapp (backend 10934 + frontend 10935)
just webapp
```

## Claude Desktop Config

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "command": "uv",
      "args": ["run", "jellyfin-mcp", "--stdio"],
      "cwd": "D:/Dev/repos/jellyfin-mcp",
      "env": {
        "JELLYFIN_URL": "http://localhost:8096",
        "JELLYFIN_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Documentation

### For Users
| Doc | Content |
|---|---|
| [Jellyfin Server Install](docs/JELLYFIN_SERVER.md) | Full Jellyfin setup — Windows, Docker, Linux, NAS, HW acceleration, media folders |
| [jellyfin-mcp Install](docs/INSTALL.md) | Python deps, API key, uv install, verify |
| [Claude Desktop Config](docs/MCP_SETUP.md) | MCP client configuration, transport modes, env vars, troubleshooting |
| [Configuration](docs/CONFIG.md) | All environment variables, `.env` format, CLI args |
| [MCP Tools Reference](docs/TOOLS.md) | All 22 portmanteau tools with operations, params, examples |
| [Webapp Guide](docs/WEBAPP.md) | Dashboard pages, WebSocket live playback, theme |
| [Plugin Management](docs/PLUGINS.md) | Catalog, install/configure/uninstall, top plugins |
| [Live TV & DVR](docs/LIVE_TV.md) | EPG guide, recordings, tuners, channel management |
| [RAG Semantic Search](docs/RAG.md) | Metadata indexing, natural-language search |
| [LLM & Agentic](docs/SAMPLING.md) | Sampling config, agentic workflows, webapp chat |
| [Plex Migration](docs/PLEX_MIGRATION.md) | Phase-by-phase conversion walkthrough, watch state sync, pitfalls |
| [Tauri Desktop App](docs/TAURI.md) | Native wrapper, sidecar, installer, build pipeline |
| [FAQ](docs/FAQ.md) | Common issues, troubleshooting, performance tips |

### For Developers
| Doc | Content |
|---|---|
| [Architecture](docs/ARCHITECTURE.md) | System diagram, components, data flow, plex-mcp comparison |
| [Development](docs/DEVELOPMENT.md) | Dev setup, justfile commands, adding tools, fleet standards |
| [Deep Dive PRD](https://github.com/sandraschi/mcp-central-docs/blob/main/projects/jellyfin-mcp/PRD.md) | Full product requirements, politicolegal analysis (in mcp-central-docs) |
| [Full Architecture](https://github.com/sandraschi/mcp-central-docs/blob/main/projects/jellyfin-mcp/ARCHITECTURE.md) | Complete 340-line architecture doc (in mcp-central-docs) |

## Ports

| Port | Service |
|---|---|
| **10934** | Backend — FastAPI + FastMCP HTTP `/mcp` + WebSocket `/ws` |
| **10935** | Frontend — Next.js 15.2 dev (proxies `/api` → 10934) |
| 8096 | Jellyfin Server (external, not managed by this project) |

## Tech Stack

- **MCP Server**: Python 3.12+, FastMCP 3.2+, `jellyfin-apiclient-python`, httpx, aiohttp
- **Webapp Backend**: FastAPI, uvicorn, Starlette
- **Webapp Frontend**: Next.js 15.2, React 18, Tailwind CSS 3, Lucide icons, Recharts
- **RAG**: LanceDB + sentence-transformers (all-MiniLM-L6-v2)
- **Native**: Tauri 2.0 (Rust), PyInstaller sidecar — `just tauri-build`, `just tauri-dev`, `just tauri-sidecar`
- **Quality**: Ruff, Biome, Playwright, pytest

## Project Status

Pre-release v0.1.0. Core tool surface complete, webapp scaffolded. Active development.

## License

MIT © Sandra Schipal 2026. Jellyfin is GPL-2.0 — this MCP server communicates via HTTP, no derivative code.
