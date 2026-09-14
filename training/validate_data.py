#!/usr/bin/env python3
"""Check JSONL before you spend GPU time."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALLOWED_ROLES = {"system", "user", "assistant"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    if not args.path.is_file():
        print(f"missing file: {args.path}", file=sys.stderr)
        return 1

    n = 0
    for i, line in enumerate(args.path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            print(f"line {i}: invalid JSON ({exc})", file=sys.stderr)
            return 1
        messages = row.get("messages")
        if not isinstance(messages, list) or len(messages) < 2:
            print(f"line {i}: need messages list with at least 2 turns", file=sys.stderr)
            return 1
        roles = []
        for msg in messages:
            if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                print(f"line {i}: each message needs role and content", file=sys.stderr)
                return 1
            if msg["role"] not in ALLOWED_ROLES:
                print(f"line {i}: bad role {msg['role']!r}", file=sys.stderr)
                return 1
            if not str(msg["content"]).strip():
                print(f"line {i}: empty content", file=sys.stderr)
                return 1
            roles.append(msg["role"])
        if roles[-1] != "assistant":
            print(f"line {i}: last message must be assistant (the target)", file=sys.stderr)
            return 1
        n += 1

    print(f"ok: {n} examples in {args.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
