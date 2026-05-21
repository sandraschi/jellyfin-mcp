# Configuration Reference

## Environment Variables

### Required

| Variable | Default | Description |
|----------|---------|-------------|
| `JELLYFIN_URL` | `http://localhost:8096` | Jellyfin server URL |
| `JELLYFIN_API_KEY` | — | Jellyfin API key (Dashboard → Users → API Keys) |

### Transport

| Variable | Default | Options | Description |
|----------|---------|---------|-------------|
| `JELLYFIN_MCP_TRANSPORT` | `stdio` | `stdio`, `http`, `sse` | Transport mode |
| `JELLYFIN_MCP_PORT` | `10934` | — | HTTP/SSE port |
| `JELLYFIN_MCP_HOST` | `127.0.0.1` | — | Bind address |
| `JELLYFIN_MCP_PATH` | `/mcp` | — | HTTP endpoint path |

### Sampling (LLM)

| Variable | Default | Description |
|----------|---------|-------------|
| `JELLYFIN_SAMPLING_BASE_URL` | `http://127.0.0.1:11434/v1` | OpenAI-compatible LLM endpoint |
| `JELLYFIN_SAMPLING_MODEL` | `llama3.2` | Model name |
| `JELLYFIN_SAMPLING_API_KEY` | — | Optional API key for LLM |
| `JELLYFIN_SAMPLING_USE_CLIENT_LLM` | — | Set `1` to prefer host LLM |

### Arr Stack (optional)

| Variable | Default | Description |
|----------|---------|-------------|
| `RADARR_URL` | — | Radarr server URL |
| `SONARR_URL` | — | Sonarr server URL |
| `LIDARR_URL` | — | Lidarr server URL |
| `ARR_API_KEY` | — | Shared Arr API key |

### WebApp

| Variable | Default | Description |
|----------|---------|-------------|
| `TMDB_API_KEY` | — | TMDB API key for metadata enrichment |
| `LLM_BASE_URL` | Same as sampling | LLM for webapp chat |
| `LLM_MODEL` | Same as sampling | Model for webapp chat |

## `.env` File

```bash
# jellyfin-mcp/.env
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=abc123yourkey

# Transport
JELLYFIN_MCP_TRANSPORT=stdio
JELLYFIN_MCP_PORT=10934

# LLM
JELLYFIN_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1
JELLYFIN_SAMPLING_MODEL=llama3.2

# Optional
JELLYFIN_SAMPLING_USE_CLIENT_LLM=0
RADARR_URL=http://localhost:7878
ARR_API_KEY=arr-key
TMDB_API_KEY=tmdb-key
```

## CLI Arguments

```powershell
# Override .env values
uv run jellyfin-mcp --http --port 10934 --host 0.0.0.0 --debug

# Full help
uv run jellyfin-mcp --help
```
