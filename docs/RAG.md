# RAG Semantic Search

Natural-language search over Jellyfin media metadata using LanceDB + sentence-transformers.

## How It Works

1. **Sync** — crawls Jellyfin libraries, extracts metadata (name, overview, genres, year), generates embeddings
2. **Search** — converts query to embedding, finds nearest neighbors in vector space
3. **Results** — returns items ranked by semantic similarity, not keyword matching

## Usage

### MCP Tool

```python
# Index metadata (one-time or periodic)
await jellyfin_rag(operation="sync")

# Search
await jellyfin_rag(operation="search", query="dark sci-fi with strong female lead", limit=10)

# Check status
await jellyfin_rag(operation="status")

# Reindex from scratch
await jellyfin_rag(operation="reindex")

# Purge index
await jellyfin_rag(operation="purge")
```

### Webapp

Visit `/rag` in the webapp:
1. Click **Sync Metadata** to index (progress indicator while running)
2. Type natural-language queries in the search box
3. Results show item name, type, relevance score

## Configuration

Index stored at `~/.jellyfin-mcp/rag/` by default. Uses LanceDB for storage and `all-MiniLM-L6-v2` for embeddings.

## Example Queries

| Query | Finds |
|-------|-------|
| "animated movies about family" | Finding Nemo, The Incredibles, Encanto |
| "mind-bending thriller with twists" | Inception, Shutter Island, Fight Club |
| "feel-good comedies from the 90s" | Groundhog Day, Clueless, The Big Lebowski |
| "music documentaries about rock" | Woodstock, The Last Waltz, Amy |

No exact keyword matching needed — the embedding model captures semantic meaning.
