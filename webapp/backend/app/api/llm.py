"""LLM chat and model listing API endpoints."""
import logging
import os

import httpx
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()


class ChatRequest(BaseModel):
    model: str = "llama3.2"
    messages: list[dict]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: int = 2048


class ChatResponse(BaseModel):
    model: str
    message: dict
    usage: dict | None = None


@router.post("/chat")
async def chat(body: ChatRequest):
    """Send chat messages to the configured LLM (OpenAI-compatible API)."""
    base_url = (os.getenv("LLM_BASE_URL") or "http://127.0.0.1:11434/v1").strip().rstrip("/")
    api_key = os.getenv("LLM_API_KEY") or ""

    try:
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {
            "model": body.model,
            "messages": body.messages,
            "stream": body.stream,
            "temperature": body.temperature,
            "max_tokens": body.max_tokens,
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{base_url}/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()

        choice = (data.get("choices") or [{}])[0] or {}
        msg = choice.get("message") or {}
        return {
            "success": True,
            "data": {
                "model": data.get("model", body.model),
                "message": {"role": msg.get("role", "assistant"), "content": msg.get("content", "")},
                "usage": data.get("usage"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_models():
    """List available LLM models from the configured provider."""
    base_url = (os.getenv("LLM_BASE_URL") or "http://127.0.0.1:11434/v1").strip().rstrip("/")
    api_key = os.getenv("LLM_API_KEY") or ""

    try:
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{base_url}/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()

        return {"success": True, "data": data.get("data", data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
