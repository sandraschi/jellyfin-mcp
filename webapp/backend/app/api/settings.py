"""Settings management API endpoints."""
import json
import os
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

_settings_file = Path(__file__).resolve().parent.parent.parent / ".env"


@router.get("/")
async def get_settings():
    """Get current backend settings (redacted API keys)."""
    keys = [
        "JELLYFIN_URL", "JELLYFIN_SERVER_URL", "JELLYFIN_API_KEY", "JELLYFIN_TOKEN",
        "JELLYFIN_WS_ENABLED", "LLM_BASE_URL", "LLM_API_KEY", "LLM_PROVIDER",
    ]
    values = {}
    for k in keys:
        v = os.getenv(k)
        if v:
            if "KEY" in k or "TOKEN" in k:
                values[k] = v[:4] + "..." if len(v) > 4 else "****"
            else:
                values[k] = v
    return {"success": True, "data": values}


@router.post("/")
async def update_settings(data: dict):
    """Update backend settings (writes to .env file)."""
    try:
        lines = []
        if _settings_file.exists():
            lines = _settings_file.read_text(encoding="utf-8").splitlines()

        updated_keys = set()
        new_lines = []
        for key, value in data.items():
            key_upper = key.upper()
            updated_keys.add(key_upper)
            os.environ[key_upper] = str(value)
            found = False
            for i, line in enumerate(lines):
                if line.startswith(f"{key_upper}="):
                    lines[i] = f"{key_upper}={value}"
                    found = True
                    break
            if not found:
                lines.append(f"{key_upper}={value}")

        _settings_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"success": True, "message": "Settings saved", "data": {"updated": list(updated_keys)}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
