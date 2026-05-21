# Contributing

## Quick Start

```powershell
git clone https://github.com/sandraschi/jellyfin-mcp
cd jellyfin-mcp
uv sync
cd webapp/frontend && npm install && cd ../..
```

## Justfile

```powershell
just lint      # Ruff (Python) + Biome (JS/TS)
just fix       # Auto-fix lint issues
just fmt       # Format all
just test      # Pytest with coverage
just ci        # Lint + test
```

## Commit Convention

```
feat: add playback control tool
fix: handle Jellyfin auth timeout
docs: update webapp guide
refactor: extract WebSocketService
test: add library tool tests
```

## Pull Requests

1. Fork the repo
2. Create feature branch: `feat/your-feature`
3. Write code following existing patterns
4. Run `just ci` — must pass
5. Open PR against `master`

## Code Patterns

- **MCP tools**: Portmanteau pattern — one tool per domain, `operation` param dispatches
- **Services**: Async executor pattern — blocking calls run in thread pool via `_run_in_executor()`
- **Models**: Pydantic v2 — `model_dump()` never `.dict()`
- **Tool returns**: Always `ToolResult(content={"success": True, "data": ..., "operation": str})`
- **Docstrings**: No `Args:` section — use `Annotated[..., Field(description="...")]`
- **Annotations**: Dict form `{"readOnlyHint": True}` — not FastMCP constants

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed patterns.
