# Onboarding — jellyfin-mcp

You need a running Jellyfin server (default http://localhost:8096) plus an API key. This MCP wraps it; without both, tools return "unavailable" and the webapp shows MOCK until onboarded.

## 1. Install Jellyfin
See docs/JELLYFIN_SERVER.md (Windows/Docker/Linux/NAS, HW accel, media folders).

## 2. API key
Dashboard > Administration > API Keys > New. Copy the key.

## 3. Configure
Copy `.env.example` to `.env`, set `JELLYFIN_URL` and `JELLYFIN_API_KEY`. Or pass env to Claude Desktop config (README snippet).

## 4. Sanity check
`uv run jellyfin-mcp` then `jellyfin_help(operation="discover")`. `GET :10934/health` must be 200.

## Pitfalls
- Wrong scheme (https vs http) or trailing slash on URL.
- Key with no admin scope cannot install plugins or manage LiveTV.
- Port 8096 in use by another Jellyfin install.
