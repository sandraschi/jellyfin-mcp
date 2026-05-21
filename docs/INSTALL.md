# Installation & Setup

## Prerequisites

- **Python 3.12+** — required for FastMCP 3.2+
- **Jellyfin Server** — installed and running (port 8096 default)
- **uv** — Python package manager (`pip install uv` or `winget install uv`)
- **Node.js 20+** — for webapp frontend (optional, MCP tools work without it)

## Jellyfin Server Setup

**→ Full guide:** [Jellyfin Server Installation Guide](JELLYFIN_SERVER.md) — Windows, Docker, Linux, macOS, NAS, hardware acceleration, media folder structure, remote access, post-install checklist.

Quick reference:
```powershell
# Windows: Download installer from https://jellyfin.org/downloads/windows

# Docker (recommended for dev):
docker run -d --name jellyfin -p 8096:8096 \
  -v /path/to/config:/config -v /path/to/media:/media:ro \
  jellyfin/jellyfin:latest

# Linux (Debian/Ubuntu):
curl https://repo.jellyfin.org/install-debuntu.sh | sudo bash
```

## API Key

Jellyfin provides API keys through the dashboard — no browser devtools needed:

1. Open Jellyfin: `http://localhost:8096`
2. **Dashboard** → **Users** → click your user
3. **API Keys** tab → **Create Key** (name it "jellyfin-mcp")
4. Copy the key

Or via curl:
```bash
curl -X POST "http://localhost:8096/Users/AuthenticateByName" \
  -H "Content-Type: application/json" \
  -H 'X-Emby-Authorization: MediaBrowser Client="mcp", Device="server", DeviceId="mcp-001", Version="1.0"' \
  -d '{"Username": "your-user", "Pw": "your-password"}'
```

## jellyfin-mcp Installation

```powershell
git clone https://github.com/sandraschi/jellyfin-mcp
cd jellyfin-mcp

# Install Python deps
uv sync

# Configure
cp .env.example .env
# Edit .env — set JELLYFIN_URL and JELLYFIN_API_KEY

# Verify install
uv run python -c "from jellyfin_mcp import __version__; print(__version__)"
```

## Webapp Setup (optional)

```powershell
cd webapp/frontend
npm install

# Then start from repo root:
just webapp
```

## Verify

```powershell
# STDIO mode (for Claude Desktop)
uv run jellyfin-mcp --stdio

# HTTP mode (for MCP Inspector)
uv run jellyfin-mcp --http --port 10934
# Visit http://localhost:10934/health
```
