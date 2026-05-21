# FAQ & Troubleshooting

## Installation

**Q: `uv sync` fails with "No module named fastmcp"?**
A: Python 3.12+ required. Check: `python --version`. If lower, install 3.12+ from python.org.

**Q: Jellyfin says "Connection refused" on localhost:8096?**
A: Jellyfin service may not be running. Check: `Get-Service jellyfin` (Windows) or `systemctl status jellyfin` (Linux).

**Q: Where do I get the Jellyfin API key?**
A: Dashboard → Users → click your user → API Keys tab → Create Key. No browser devtools needed.

**Q: Can I run without Docker / without installing Jellyfin?**
A: You need Jellyfin server running somewhere. It can be on the same machine, a NAS, a VPS, or another PC on your network. Set `JELLYFIN_URL=http://that-machine:8096`.

## Connection

**Q: "Invalid API key" error?**
A: Regenerate the key in Jellyfin Dashboard → Users → API Keys. Ensure no trailing spaces in `.env`. Verify the user has "Allow media playback" permission.

**Q: "Cannot connect to Jellyfin at http://..." error?**
A: 
1. Verify Jellyfin is running: open `http://your-url:8096` in browser
2. Check URL format: must include `http://` or `https://`
3. Firewall blocking port 8096? Temporarily disable to test
4. Docker: container running? `docker ps | grep jellyfin`

**Q: Tools return empty data but Jellyfin web UI works?**
A: The API key user may not have access to all libraries. Check user permissions in Jellyfin Dashboard → Users → (user) → Access. Enable access to all libraries.

**Q: WebSocket dashboard shows "Disconnected"?**
A: WebSocket proxy needs `/ws` path. If using reverse proxy (Nginx), ensure WebSocket upgrade headers are configured. See `docs/JELLYFIN_SERVER.md` Remote Access section.

## Tools

**Q: `jellyfin_media(operation="get")` returns "Resource not found"?**
A: Item ID may have changed after a library refresh. Use `browse` to find the item first.

**Q: `jellyfin_playback(operation="play")` does nothing?**
A: Playback requires an active session. Use `list_sessions` first to get the `session_id`. The target device must be actively connected to Jellyfin.

**Q: `jellyfin_plugin(operation="install")` fails?**
A: Plugin catalog is fetched from GitHub. If GitHub is blocked or rate-limited, try again later. Some plugins require a server restart after installation.

**Q: `jellyfin_rag(operation="search")` returns empty?**
A: Run `jellyfin_rag(operation="sync")` first to index metadata. Sync may take minutes for large libraries.

## Webapp

**Q: "Failed to fetch" on all pages?**
A: Backend not running. Start with `just webapp`. Check `http://localhost:10934/health` responds.

**Q: No poster images showing?**
A: Image proxy uses `follow_redirects=True` but check:
1. Backend at localhost:10934 is running
2. Jellyfin server is reachable from the backend
3. Image paths match: `/image/Items/{id}/Images/Primary/0`

**Q: Playback dashboard shows nothing?**
A: No active sessions. Play something in Jellyfin (web player, mobile app) and it appears in real-time.

## Claude Desktop

**Q: Jellyfin tools don't appear in Claude?**
A: 
1. Restart Claude Desktop after adding mcp.json config
2. Check Claude → Developer → MCP Servers → jellyfin-mcp status
3. Run `uv run jellyfin-mcp --stdio` manually to see errors
4. Check `JELLYFIN_API_KEY` is set in env

**Q: "STDIO mode hangs" or "No response from server"?**
A: Set `JELLYFIN_ALLOW_LOGGING=1` env var to see full output. Common causes: invalid API key, Jellyfin server unreachable, Python path issues.

## Performance

**Q: RAG sync is slow?**
A: Embedding generation is CPU-bound. With `all-MiniLM-L6-v2`, expect ~50 items/second on modern CPU. For large libraries (50k+ items), sync may take 15-20 minutes. This is a one-time operation.

**Q: Search is slow?**
A: Full-text search goes to Jellyfin directly — check Jellyfin server load. Semantic search via RAG uses LanceDB which is very fast (<100ms) once indexed.

## Jellyfin Server

**Q: Where are Jellyfin logs?**
- Windows: `C:\ProgramData\Jellyfin\Server\log\`
- Linux: `/var/log/jellyfin/`
- Docker: `docker logs jellyfin`

**Q: How to backup Jellyfin config?**
```bash
# Docker
cp -r /opt/jellyfin/config /backup/jellyfin-config-$(date +%Y%m%d)

# Windows
Copy-Item -Recurse "C:\ProgramData\Jellyfin\Server" "D:\backup\jellyfin-$(Get-Date -Format yyyyMMdd)"
```

**Q: Jellyfin updates — safe to upgrade?**
A: Yes. Jellyfin 10.x updates are backward compatible. Docker: `docker compose pull && docker compose up -d`. Windows: run new installer (preserves config). Always backup `/config` first.

## Still Stuck?

- [Jellyfin Documentation](https://jellyfin.org/docs/)
- [Jellyfin Matrix Chat](https://matrix.to/#/#jellyfinorg:matrix.org)
- [jellyfin-mcp GitHub Issues](https://github.com/sandraschi/jellyfin-mcp/issues)
