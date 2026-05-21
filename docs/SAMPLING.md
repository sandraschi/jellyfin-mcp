# LLM Sampling & Agentic Tools

jellyfin-mcp supports server-side LLM sampling for agentic workflows and natural-language media queries.

## Configuration

```bash
# .env
JELLYFIN_SAMPLING_BASE_URL=http://127.0.0.1:11434/v1   # Ollama default
JELLYFIN_SAMPLING_MODEL=llama3.2
JELLYFIN_SAMPLING_API_KEY=                               # optional for cloud LLMs
JELLYFIN_SAMPLING_USE_CLIENT_LLM=0                       # 1 = prefer host LLM
```

Supports any OpenAI-compatible endpoint: Ollama, LM Studio, vLLM, OpenAI, Groq, etc.

## Tools

### jellyfin_agentic (workflow)

Multi-step agentic workflows using FastMCP `sample_step` — the LLM plans steps and executes tools:

```python
await jellyfin_agentic(operation="workflow", prompt="""
  Find all unwatched sci-fi movies from my library.
  For each, check if it has a rating above 7.0.
  Create a "Weekend Sci-Fi" playlist with the top 5.
""")
```

### jellyfin_agentic (natural_query)

Single-turn natural language query — no tool execution:

```python
await jellyfin_agentic(operation="natural_query",
    query="What are the most popular movies in my library right now?")
```

### jellyfin_agentic (batch)

Run a batch operation across items matching a description:

```python
await jellyfin_agentic(operation="batch",
    prompt="Refresh metadata for all movies released in 2023")
```

## Webapp Chat

The webapp at `/chat` uses the same LLM endpoint. Features:
- Model selector (pulls from LLM API)
- Input with send/Ctrl+Enter
- Bouncing dot animation during response
- Markdown rendering in responses
- Conversation history (in-memory, page session)

## Fallback Behavior

If `JELLYFIN_SAMPLING_USE_CLIENT_LLM=1`, the MCP host (Claude) handles sampling instead. If no LLM is available at all, sampling-dependent tools gracefully return an error message with setup instructions.

## No LLM? No Problem

All 19 non-agentic tools work without sampling. Only `jellyfin_agentic` and the webapp chat require an LLM endpoint.
