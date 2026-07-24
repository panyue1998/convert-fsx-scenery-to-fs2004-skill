#!/usr/bin/env python3
"""Rewrite SCASM ground-polygon texture references for FS2004."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


DDS_REFERENCE = re.compile(r"(?i)\.dds(?=\")")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    if not args.source.is_file():
        parser.error(f"File not found: {args.source}")
    args.output.parent.mkdir(parents=True, exist_ok=True)

    text = args.source.read_text(encoding="cp1252", errors="strict")
    rewritten, count = DDS_REFERENCE.subn(".bmp", text)
    if count == 0:
        raise SystemExit(f"No DDS texture references found in {args.source}")
    args.output.write_text(rewritten, encoding="cp1252", errors="strict")
    print(f"rewritten_references={count} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
