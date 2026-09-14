from __future__ import annotations

import json
import re
from typing import Any

from saptarshi_agents.llm import LLMClient
from saptarshi_agents.rishis import DISPLAY_NAMES, RISHI_IDS, load_prompt, rishi_system_prompt


def _extract_json(text: str) -> dict[str, Any]:
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", stripped)
    if fence:
        stripped = fence.group(1).strip()
    try:
        data = json.loads(stripped)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", stripped)
    if match:
        data = json.loads(match.group(0))
        if isinstance(data, dict):
            return data
    return {}


def _normalize_rishi(value: Any) -> str | None:
    if not value or not isinstance(value, str):
        return None
    key = value.strip().lower().replace(" ", "")
    aliases = {
        "vasishtha": "vashistha",
        "vasiṣṭha": "vashistha",
        "vishwamitra": "vishvamitra",
        "viśvāmitra": "vishvamitra",
        "bharadwaja": "bharadvaja",
        "bhāradvāja": "bharadvaja",
    }
    key = aliases.get(key, key)
    return key if key in RISHI_IDS else None


async def run_turn(user_text: str, llm: LLMClient | None = None) -> dict[str, Any]:
    client = llm or LLMClient()
    route_raw = await client.chat(
        [
            {"role": "system", "content": load_prompt("supervisor")},
            {"role": "user", "content": user_text},
        ],
        temperature=0.1,
        max_tokens=300,
    )
    route = _extract_json(route_raw)
    primary = _normalize_rishi(route.get("primary")) or "atri"
    secondary = _normalize_rishi(route.get("secondary"))
    if secondary == primary:
        secondary = None
    reason = str(route.get("reason") or "Defaulted to Atri.").strip()

    agents_used = [primary]
    primary_answer = await client.chat(
        [
            {"role": "system", "content": rishi_system_prompt(primary)},
            {"role": "user", "content": user_text},
        ],
        temperature=0.5,
        max_tokens=800,
    )

    secondary_answer = None
    if secondary:
        agents_used.append(secondary)
        secondary_answer = await client.chat(
            [
                {"role": "system", "content": rishi_system_prompt(secondary)},
                {"role": "user", "content": user_text},
            ],
            temperature=0.5,
            max_tokens=800,
        )

    if secondary_answer:
        spoken = await client.chat(
            [
                {
                    "role": "system",
                    "content": (
                        "You are SAPTARSHI's supervisor. Combine the specialist answers into one "
                        "spoken reply of 1–2 short sentences. Do not list the specialists. "
                        "Plain speech, no markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Question: {user_text}\n\n"
                        f"{DISPLAY_NAMES[primary]}:\n{primary_answer}\n\n"
                        f"{DISPLAY_NAMES[secondary]}:\n{secondary_answer}"
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=200,
        )
        reply = (
            f"{DISPLAY_NAMES[primary]}:\n{primary_answer.strip()}\n\n"
            f"{DISPLAY_NAMES[secondary]}:\n{secondary_answer.strip()}"
        )
        spoken = spoken.strip()
    else:
        reply = primary_answer.strip()
        spoken = reply
        if len(spoken) > 420:
            spoken = await client.chat(
                [
                    {
                        "role": "system",
                        "content": (
                            "Summarize the specialist answer as 1–2 spoken sentences. "
                            "Plain speech, no markdown."
                        ),
                    },
                    {"role": "user", "content": reply},
                ],
                temperature=0.2,
                max_tokens=160,
            )
            spoken = spoken.strip()

    return {
        "reply": reply,
        "spoken": spoken,
        "agents_used": agents_used,
        "agents_display": [DISPLAY_NAMES[a] for a in agents_used],
        "route_reason": reason,
        "primary": primary,
    }
