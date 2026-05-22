"""FastAPI application for jellyfin-mcp webapp."""
import logging
import logging.handlers
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import (
    help_api,
    images,
    library,
    livetv,
    llm,
    media,
    playback,
    plugins,
    rag,
    search,
    server,
    settings,
    streaming,
    users,
    ws,
)
from .config import settings as app_settings

# 1. Path & Logging setup
_current_file = Path(__file__).resolve()
project_root = _current_file.parent.parent.parent.parent
src_path = project_root / "src"

try:
    from dotenv import load_dotenv

    load_dotenv(project_root / ".env")
except ImportError:
    pass

if src_path.exists():
    src_str = str(src_path)
    if src_str not in sys.path:
        sys.path.insert(0, src_str)

_log_dir = project_root / "logs"
_log_dir.mkdir(parents=True, exist_ok=True)
_log_file = _log_dir / "webapp.log"


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if not any(isinstance(h, logging.handlers.RotatingFileHandler) for h in root_logger.handlers):
        handler = logging.handlers.RotatingFileHandler(
            _log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        root_logger.addHandler(handler)

        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(logging.Formatter("%(levelname)s:     %(message)s"))
        root_logger.addHandler(console)

        for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
            logger_obj = logging.getLogger(logger_name)
            logger_obj.addHandler(handler)
            logger_obj.propagate = True


setup_logging()
logger = logging.getLogger(__name__)


# 2. Lazy FastMCP mount
@asynccontextmanager
async def lifespan(_app: FastAPI):
    import asyncio as _asyncio

    _asyncio.create_task(_lazy_mount_mcp())
    yield


app = FastAPI(
    title=app_settings.API_TITLE,
    description=app_settings.API_DESCRIPTION,
    version=app_settings.API_VERSION,
    lifespan=lifespan,
)

import asyncio as _asyncio

_mcp_loaded = False


async def _lazy_mount_mcp():
    try:
        from jellyfin_mcp.app import http_app

        mcp_app = http_app()
        if mcp_app:
            app.mount("/mcp", mcp_app)
            global _mcp_loaded
            _mcp_loaded = True
            logger.info("FastMCP mounted at /mcp (lazy-loaded)")
        else:
            logger.error("FastMCP http_app() returned None")
    except Exception as e:
        logger.error("Could not mount FastMCP HTTP app: %s", e, exc_info=True)


app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Route Registration
app.include_router(images.router, prefix="/api/image", tags=["images"])
app.include_router(images.router, prefix="/image", tags=["images"])
app.include_router(library.router, prefix="/api/libraries", tags=["libraries"])
app.include_router(server.router, prefix="/api/server", tags=["server"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(media.router, prefix="/api/media", tags=["media"])
app.include_router(playback.router, prefix="/api/playback", tags=["playback"])
app.include_router(plugins.router, prefix="/api/plugins", tags=["plugins"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(streaming.router, prefix="/api/streaming", tags=["streaming"])
app.include_router(rag.router, prefix="/api/rag", tags=["rag"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(help_api.router, prefix="/api/help", tags=["help"])
app.include_router(livetv.router, prefix="/api/livetv", tags=["livetv"])
app.include_router(ws.router, tags=["ws"])


@app.get("/")
async def root():
    return {
        "message": "jellyfin-mcp Webapp API",
        "version": app_settings.API_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/mcp/status")
async def mcp_status():
    return {"loaded": _mcp_loaded, "message": "FastMCP mounts in background ~90s after startup"}
