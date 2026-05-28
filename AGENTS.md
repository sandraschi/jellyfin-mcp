# jellyfin-mcp — Agent Guide

## Overview
FastMCP 3.2+ server for Jellyfin Media Server — open-source Plex alternative with plugins, WebSocket real-time events, and full OpenAPI. Includes React webapp + Tauri native wrapper.

## Entry Points
- `uv run jellyfin-mcp` → `jellyfin_mcp.server:main`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `CLAUDE.md` — Claude Code context (if present)
