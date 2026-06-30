"""Start webapp backend for Playwright e2e (loads .env, port 10934)."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "webapp" / "backend"
SRC_DIR = PROJECT_ROOT / "src"

sys.path[:0] = [str(SRC_DIR), str(BACKEND_DIR)]

from dotenv import load_dotenv

load_dotenv(PROJECT_ROOT / ".env")

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=10934, log_level="warning")
