#!/usr/bin/env python3
"""Adjust MCX-exported SCASM ground-polygon visibility distances."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


VISIBILITY = re.compile(r"(?i)(\bv1\s*=\s*)(\d+)(\b)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--distance", type=int, required=True, help="Visibility in meters")
    parser.add_argument("--expected-current", type=int, default=10000)
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"File not found: {args.source}")
    if args.distance <= 0:
        parser.error("Visibility distance must be positive")

    text = args.source.read_text(encoding="cp1252", errors="strict")
    seen: list[int] = []

    def replace(match: re.Match[str]) -> str:
        current = int(match.group(2))
        seen.append(current)
        if current != args.expected_current:
            return match.group(0)
        return f"{match.group(1)}{args.distance}{match.group(3)}"

    adjusted = VISIBILITY.sub(replace, text)
    changed = sum(value == args.expected_current for value in seen)
    unexpected = sorted({value for value in seen if value != args.expected_current})
    if not seen:
        raise SystemExit(f"No RefPoint visibility values found in {args.source}")
    if unexpected:
        raise SystemExit(f"Unexpected existing visibility values: {unexpected}")
    if changed == 0:
        raise SystemExit("No visibility values were changed")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(adjusted, encoding="cp1252", errors="strict")
    print(f"adjusted_visibility_records={changed} distance_m={args.distance} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
