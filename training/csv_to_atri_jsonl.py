#!/usr/bin/env python3
"""Turn Hyderabad daily weather CSV into Atri chat JSONL for QLoRA."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ATRI_PROMPT = (REPO / "packages/agents/saptarshi_agents/prompts/atri.md").read_text(
    encoding="utf-8"
).strip()
MONTHS = (
    "",
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
DISCLAIMER = "This is historical model data, not an IMD live forecast."


def fmt_num(value: str) -> str:
    n = float(value)
    if n == int(n):
        return str(int(n))
    return f"{n:.1f}"


def pretty_date(iso: str) -> str:
    y, m, d = (int(p) for p in iso.split("-"))
    return f"{d} {MONTHS[m]} {y}"


def rain_phrase(rain_mm: str, precip_mm: str) -> str:
    rain = float(rain_mm)
    precip = float(precip_mm)
    amount = rain if rain > 0 else precip
    if amount <= 0:
        return "no rain (0 mm)"
    return f"rain {fmt_num(str(amount))} mm"


def answer(row: dict) -> str:
    iso = row["date"]
    rain = rain_phrase(row["rain_mm"], row["precip_mm"])
    return (
        f"Hyderabad on {pretty_date(iso)}: high {fmt_num(row['temp_max_c'])}°C, "
        f"low {fmt_num(row['temp_min_c'])}°C, {rain}, "
        f"wind up to {fmt_num(row['wind_max_kmh'])} km/h. {DISCLAIMER}"
    )


def questions(iso: str) -> list[str]:
    spoken = pretty_date(iso)
    return [
        f"What was the weather in Hyderabad on {spoken}?",
        f"Did it rain in Hyderabad on {iso}?",
        f"High and low in Hyderabad on {spoken}?",
    ]


def example(system: str, user: str, assistant: str) -> dict:
    return {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ]
    }


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path(__file__).resolve().parent / "data/weather_hyderabad_2025.csv",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "data/atri_hyderabad_2025.jsonl",
    )
    parser.add_argument(
        "--mix",
        type=Path,
        default=Path(__file__).resolve().parent / "data/example.jsonl",
        help="Router / other-rishi rows mixed in so the adapter does not forget routing.",
    )
    args = parser.parse_args()

    rows: list[dict] = []
    with args.csv.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            assistant = answer(row)
            for q in questions(row["date"]):
                rows.append(example(ATRI_PROMPT, q, assistant))

    if args.mix.is_file():
        rows.extend(load_jsonl(args.mix))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    n_weather = len(rows) - (len(load_jsonl(args.mix)) if args.mix.is_file() else 0)
    print(f"wrote {len(rows)} examples ({n_weather} Atri weather) -> {args.out}")


if __name__ == "__main__":
    main()
