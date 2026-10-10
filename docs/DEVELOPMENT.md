# Development Guide

## Setup

```powershell
git clone https://github.com/sandraschi/jellyfin-mcp
cd jellyfin-mcp

# Python
uv sync

# Frontend
cd webapp/frontend
npm install
cd ../..

# Pre-commit hooks
pre-commit install
```

## Justfile

```powershell
just install    # uv sync + pre-commit
just start      # MCP server (STDIO)
just webapp     # Webapp (backend + frontend)
just lint       # Ruff (Python) + Biome (JS/TS)
just fix        # Auto-fix lint
just fmt        # Format all
just test       # Pytest with coverage
just e2e        # Playwright smoke tests
just ci         # Lint + test
just clean      # Remove caches and build artifacts
just version    # Print version from pyproject.toml
```

## Project Structure

```
jellyfin-mcp/
├── src/jellyfin_mcp/           # MCP server Python package
│   ├── app.py                  # FastMCP instance
│   ├── config.py               # JellyfinConfig (Pydantic v2)
│   ├── transport.py            # STDIO/HTTP/SSE transport
│   ├── server.py               # Entry point + tool imports
│   ├── prefabs.py              # Prefab card builders
│   ├── tools/
│   │   ├── agentic.py          # Agentic tool registration
│   │   └── portmanteau/        # 21 portmanteau tool modules
│   ├── services/               # JellyfinService, WS, Plugin, RAG
│   ├── models/                 # Pydantic v2 data models
│   ├── sampling/               # LLM sampling handler
│   └── utils/                  # Logger, helpers
├── webapp/
│   ├── backend/app/            # FastAPI backend
│   │   ├── main.py             # App with lazy MCP mount
│   │   └── api/                # 15 API route modules
│   ├── frontend/               # Next.js 15.2 app
│   │   ├── app/                # 12 pages (App Router)
│   │   ├── components/         # Layout + reusable components
│   │   └── utils/              # API + media helpers
│   ├── start.ps1               # Dev launcher
│   └── start.bat
├── native/                     # Tauri 2.0 wrapper
├── tests/                      # Pytest tests
├── docs/                       # Documentation
├── pyproject.toml
├── justfile
└── .env.example
```

## Adding a New Portmanteau Tool

1. Create `src/jellyfin_mcp/tools/portmanteau/your_tool.py`:
```python
from typing import Annotated, Literal
from fastmcp.tools import ToolResult
from pydantic import Field
from ...app import mcp


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def jellyfin_yourtool(
    operation: Annotated[Literal["op1", "op2"], Field(description="...")],
    param: Annotated[str | None, Field(description="...")] = None,
) -> ToolResult:
    """Summary docstring."""
    try:
        jf = _get_jellyfin_service()
        await jf.connect()
        # dispatch on operation
        return ToolResult(content={"success": True, "data": ..., "operation": operation})
    except Exception as e:
        return ToolResult(content={"success": False, "error": str(e)})
```

2. Add to `tools/portmanteau/__init__.py`:
```python
from .your_tool import jellyfin_yourtool
# Add to __all__
```

## Committing

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`
- Pre-commit runs Ruff + Biome
- CI runs lint + test

## Fleet Standards

This project follows the [SOTA 2026 fleet standards](https://github.com/sandraschi/mcp-central-docs):
- FastMCP 3.2+ with portmanteau tools
- Pydantic v2 (never `.dict()`, use `.model_dump()`)
- Docstring SOTA (no `Args:`, use `Field(description=...)`)
- Ports: 10934/10935 from reserved range 10700-11000
- PowerShell native syntax (no `&&`, no `grep`)
- `uv` package manager, `hatchling` build backend
