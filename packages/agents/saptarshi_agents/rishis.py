from __future__ import annotations

from pathlib import Path

PROMPTS_DIR = Path(__file__).parent / "prompts"

RISHI_IDS = (
    "atri",
    "bharadvaja",
    "gautama",
    "jamadagni",
    "kashyapa",
    "vashistha",
    "vishvamitra",
)

DISPLAY_NAMES = {
    "atri": "Atri",
    "bharadvaja": "Bharadvaja",
    "gautama": "Gautama",
    "jamadagni": "Jamadagni",
    "kashyapa": "Kashyapa",
    "vashistha": "Vashistha",
    "vishvamitra": "Vishvamitra",
}


def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    return path.read_text(encoding="utf-8").strip()


def rishi_system_prompt(rishi_id: str) -> str:
    if rishi_id not in RISHI_IDS:
        raise KeyError(f"Unknown rishi: {rishi_id}")
    return load_prompt(rishi_id)
