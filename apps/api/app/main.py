from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from httpx import HTTPError

from saptarshi_agents.llm import LLMClient
from saptarshi_agents.rishis import DISPLAY_NAMES, RISHI_IDS
from saptarshi_agents.supervisor import run_turn

from app.schemas import ChatRequest, ChatResponse
from app.settings import settings

app = FastAPI(title="SAPTARSHI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _client() -> LLMClient:
    return LLMClient(
        base_url=settings.model_base_url,
        api_key=settings.model_api_key,
        model=settings.model_name,
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "saptarshi-api"}


@app.get("/v1/rishis")
async def rishis() -> dict[str, list[dict[str, str]]]:
    return {
        "rishis": [{"id": rishi_id, "name": DISPLAY_NAMES[rishi_id]} for rishi_id in RISHI_IDS]
    }


@app.get("/v1/model")
async def model_ping() -> dict[str, object]:
    client = _client()
    try:
        sample = await client.chat(
            [{"role": "user", "content": "Reply with the single word pong."}],
            temperature=0,
            max_tokens=8,
        )
        return {
            "ok": True,
            "model": client.model,
            "base_url": client.base_url,
            "sample": sample.strip(),
        }
    except HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Model unreachable: {exc}") from exc


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(body: ChatRequest) -> ChatResponse:
    try:
        result = await run_turn(body.text.strip(), llm=_client())
    except HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Model call failed: {exc}") from exc
    return ChatResponse(**result)
