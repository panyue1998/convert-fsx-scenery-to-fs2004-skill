#!/usr/bin/env python3
"""Validate an FS2004 scenery package produced by convert_scenery.py."""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from datetime import datetime
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_hashes(source: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for folder_name in ("Scenery", "Texture", "Docs"):
        folder = source / folder_name
        if not folder.is_dir():
            continue
        for path in sorted(item for item in folder.rglob("*") if item.is_file()):
            result[str(path.relative_to(source))] = sha256(path)
    return result


def log_has_errors(text: str) -> bool:
    lowered = text.casefold()
    markers = (" error ", "error c", "failed to", "can not be exported", "cannot be exported")
    return any(marker in lowered for marker in markers)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package", type=Path, required=True)
    parser.add_argument("--source", type=Path)
    args = parser.parse_args()

    package = args.package.resolve()
    scenery = package / "scenery"
    texture = package / "texture"
    logs = package / "logs"
    errors: list[str] = []
    warnings: list[str] = []

    bgl_files = sorted(scenery.glob("*.bgl"), key=lambda value: value.name.casefold())
    zero_bgl = [path.name for path in bgl_files if path.stat().st_size == 0]
    if zero_bgl:
        errors.append(f"Zero-byte BGL files: {zero_bgl}")

    bad_logs: list[str] = []
    logged_bgl = 0
    for bgl in bgl_files:
        log_path = logs / f"bgl-{bgl.stem}.log"
        if not log_path.is_file():
            continue
        logged_bgl += 1
        if log_has_errors(log_path.read_text(encoding="utf-8", errors="replace")):
            bad_logs.append(bgl.name)
    if bad_logs:
        errors.append(f"Final BGL files with compiler errors: {bad_logs}")

    texture_formats: Counter[str] = Counter()
    bad_textures: list[str] = []
    dimensions: Counter[str] = Counter()
    bmp_files = sorted(texture.glob("*.bmp"), key=lambda value: value.name.casefold())
    for path in bmp_files:
        data = path.read_bytes()
        if len(data) < 34 or data[:2] != b"BM":
            bad_textures.append(path.name)
            continue
        compression = data[30:34]
        if compression not in (b"DXT1", b"DXT3"):
            bad_textures.append(path.name)
            continue
        width, height = struct.unpack_from("<ii", data, 18)
        if (
            width <= 0
            or height == 0
            or width > 1024
            or abs(height) > 1024
            or width & (width - 1)
            or abs(height) & (abs(height) - 1)
        ):
            bad_textures.append(path.name)
            continue
        texture_formats[compression.decode("ascii")] += 1
        dimensions[f"{width}x{abs(height)}"] += 1
    if bad_textures:
        errors.append(f"Invalid FS2004 BMP textures: {bad_textures}")

    dds_references = [
        path.name
        for path in bgl_files
        if b".dds" in path.read_bytes().lower()
    ]
    if dds_references:
        errors.append(f"Final BGL files still reference DDS textures: {dds_references}")

    conversion_report_path = logs / "conversion-report.json"
    conversion_report = json.loads(conversion_report_path.read_text(encoding="utf-8")) if conversion_report_path.is_file() else {}
    failed = [item["source"] for item in conversion_report.get("bgl", []) if item.get("status") == "failed"]
    skipped = [item["source"] for item in conversion_report.get("bgl", []) if item.get("status") == "skipped-unsupported"]
    final_names = {path.name.casefold() for path in bgl_files}
    leaked = [name for name in failed + skipped if name.casefold() in final_names]
    if leaked:
        errors.append(f"Failed or unsupported BGL files present in final scenery: {leaked}")

    source_unchanged = None
    if args.source:
        expected = conversion_report.get("source_hashes_before", {})
        source_unchanged = bool(expected) and expected == source_hashes(args.source.resolve())
        if not source_unchanged:
            errors.append("Source hash verification failed")

    if skipped:
        warnings.append(f"Unsupported airport/terrain BGL files skipped: {skipped}")
    if failed:
        warnings.append(f"Object BGL files that could not be converted: {failed}")

    report = {
        "validated": datetime.now().astimezone().isoformat(),
        "package": str(package),
        "valid": not errors,
        "source_unchanged": source_unchanged,
        "bgl_count": len(bgl_files),
        "bgl_with_clean_logs": logged_bgl,
        "bmp_count": len(bmp_files),
        "texture_formats": dict(texture_formats),
        "texture_dimensions": dict(sorted(dimensions.items())),
        "bgl_with_dds_references": dds_references,
        "errors": errors,
        "warnings": warnings,
    }
    output = logs / "validation-report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
