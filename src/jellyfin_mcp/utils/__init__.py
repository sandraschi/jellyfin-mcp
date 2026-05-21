"""Utility modules for jellyfin-mcp."""

import logging
import sys


def get_logger(name: str) -> logging.Logger:
    """Get a logger that writes to stderr (safe for stdio MCP mode)."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
