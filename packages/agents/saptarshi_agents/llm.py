from __future__ import annotations

import os
from typing import Any

import httpx


class LLMClient:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        raw = (base_url or os.getenv("MODEL_BASE_URL", "http://127.0.0.1:8001/v1")).rstrip("/")
        self.base_url = raw if raw.endswith("/v1") else f"{raw}/v1"
        self.api_key = api_key if api_key is not None else os.getenv("MODEL_API_KEY", "")
        self.model = model or os.getenv("MODEL_NAME") or os.getenv("HF_MODEL_ID") or "saptarshi"
        self.timeout = timeout

    async def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.4,
        max_tokens: int = 800,
    ) -> str:
        url = f"{self.base_url}/chat/completions"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]
