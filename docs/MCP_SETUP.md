# Claude Desktop Setup

## Quick Config

Add to your Claude Desktop `mcp.json`:

```json
{
  "mcpServers": {
    "jellyfin-mcp": {
      "command": "uv",
      "args": ["run", "jellyfin-mcp", "--stdio"],
      "cwd": "D:/Dev/repos/jellyfin-mcp",
      "env": {
        "JELLYFIN_URL": "http://localhost:8096",
        "JELLYFIN_API_KEY": "your-api-key-here",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Alternative: Python direct

```json
{
  "jellyfin-mcp": {
    "command": "python",
    "args": ["-m", "jellyfin_mcp", "--stdio"],
    "cwd": "D:/Dev/repos/jellyfin-mcp",
    "env": {
      "JELLYFIN_URL": "http://localhost:8096",
      "JELLYFIN_API_KEY": "your-api-key-here",
      "PYTHONPATH": "D:/Dev/repos/jellyfin-mcp/src",
      "PYTHONUNBUFFERED": "1"
    }
  }
}
```

## HTTP Mode (for remote agents)

```json
{
  "jellyfin-mcp": {
    "url": "http://your-server:10934/mcp"
  }
}
```

Start the HTTP server first:
```powershell
uv run jellyfin-mcp --http --port 10934 --host 0.0.0.0
```

## Verify

After adding to Claude Desktop config and restarting, ask:
> "Use jellyfin_help with operation discover to show available tools"

Or run directly:
```powershell
uv run jellyfin-mcp --stdio
# Type a valid JSON-RPC message or use MCP Inspector for testing
```

## Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot connect to Jellyfin" | Check `JELLYFIN_URL` — must include `http://` |
| "Invalid API key" | Generate a new key in Dashboard → Users → API Keys |
| Tool returns empty | Ensure the API key user has library access |
| STDIO mode hangs | Start with `--http` mode first to verify server works |
| `ruff` errors in logs | Set `JELLYFIN_ALLOW_LOGGING=1` to see full output |
