from __future__ import annotations

import json
import os
import re
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="SAPTARSHI stub LLM")

LANES = {
    "atri": ("weather", "rain", "monsoon", "forecast", "heat", "cyclone", "imd", "humidity"),
    "bharadvaja": ("grocery", "kirana", "sabzi", "onion", "tomato", "dal", "ration", "mandi", "vegetable"),
    "gautama": ("bank", "upi", "neft", "imps", "kyc", "loan", "savings", "account", "otp"),
    "jamadagni": ("ecommerce", "flipkart", "amazon", "delivery", "return", "cod", "order", "parcel"),
    "kashyapa": ("farm", "crop", "kharif", "rabi", "paddy", "soil", "irrigation", "msp", "agriculture"),
    "vashistha": ("insurance", "premium", "claim", "irdai", "health policy", "motor insurance"),
    "vishvamitra": ("stock", "nifty", "sensex", "nse", "bse", "share", "ipo", "sip", "equity"),
}

DISPLAY = {
    "atri": "Atri",
    "bharadvaja": "Bharadvaja",
    "gautama": "Gautama",
    "jamadagni": "Jamadagni",
    "kashyapa": "Kashyapa",
    "vashistha": "Vashistha",
    "vishvamitra": "Vishvamitra",
}


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "saptarshi"
    messages: list[Message]
    temperature: float = 0.4
    max_tokens: int = 800


def _route(text: str) -> tuple[str, str | None, str]:
    lowered = text.lower()
    hits: list[tuple[int, str]] = []
    for rishi_id, words in LANES.items():
        score = sum(1 for word in words if word in lowered)
        if score:
            hits.append((score, rishi_id))
    hits.sort(reverse=True)
    if not hits:
        return "atri", None, "No domain keywords; defaulting to Atri."
    primary = hits[0][1]
    secondary = hits[1][1] if len(hits) > 1 and hits[1][0] == hits[0][0] else None
    if secondary:
        reason = f"Matched {primary} and {secondary}."
    else:
        reason = f"Matched {primary} from the utterance."
    return primary, secondary, reason


def _rishi_from_system(system: str) -> str | None:
    match = re.search(
        r"You are (Atri|Bharadvaja|Gautama|Jamadagni|Kashyapa|Vashistha|Vishvamitra)",
        system,
    )
    if not match:
        return None
    return match.group(1).lower()


def _complete(messages: list[Message]) -> str:
    system = next((m.content for m in messages if m.role == "system"), "")
    user = next((m.content for m in reversed(messages) if m.role == "user"), "")

    if "Supervisor of SAPTARSHI" in system or "Your only job is routing" in system:
        primary, secondary, reason = _route(user)
        payload: dict[str, Any] = {
            "primary": primary,
            "secondary": secondary,
            "cross_domain": secondary is not None,
            "reason": reason,
        }
        return json.dumps(payload)

    if "Combine the specialist answers" in system or "Summarize the specialist answer" in system:
        return "Here is the council's short answer: stay with the specialist guidance and take the next small step."

    rishi = _rishi_from_system(system) or "atri"
    name = DISPLAY.get(rishi, "Atri")
    return (
        f"This is {name} speaking through the local stub model. "
        f"You said: “{user[:240]}”. "
        "Connect a Hugging Face model on GPU via MODEL_BASE_URL to replace this placeholder."
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "saptarshi-stub-llm"}


@app.post("/v1/chat/completions")
async def chat_completions(body: ChatRequest) -> dict[str, Any]:
    content = _complete(body.messages)
    return {
        "id": "stub-1",
        "object": "chat.completion",
        "model": body.model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("STUB_PORT", "8001")))
