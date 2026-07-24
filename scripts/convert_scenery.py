#!/usr/bin/env python3
"""Build a non-destructive FS2004 scenery package from an FSX source folder."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PIL import Image, ImageOps
from pywinauto import Desktop


FSX_BGL_MAGIC = bytes.fromhex("01 02 92 19")


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


def ensure_layout(source: Path, output: Path) -> dict[str, Path]:
    source = source.resolve()
    output = output.resolve()
    forbidden = {source, source / "Scenery", source / "Texture", source / "Docs"}
    if output in forbidden:
        raise ValueError(f"Unsafe output path: {output}")
    paths = {
        "scenery": output / "scenery",
        "texture": output / "texture",
        "work": output / "work",
        "logs": output / "logs",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    (paths["work"] / "bgl").mkdir(exist_ok=True)
    (paths["work"] / "textures").mkdir(exist_ok=True)
    return paths


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def click_permission_dialog(process_id: int) -> int:
    """Advance only license/permission dialogs owned by the MCX process."""
    clicked = 0
    try:
        windows = Desktop(backend="uia").windows(process=process_id)
    except Exception:
        return 0
    for window in windows:
        title = window.window_text().casefold()
        if "usage license" not in title and "permission reminder" not in title:
            continue
        labels = {"next", "agree", "yes", "ok", "同意", "是"}
        for button in window.descendants(control_type="Button"):
            try:
                if button.window_text().replace("&", "").strip().casefold() in labels and button.is_enabled():
                    button.invoke()
                    clicked += 1
                    break
            except Exception:
                continue
    return clicked


def run_mcx(command: list[str], log_path: Path, timeout_seconds: int = 1800) -> tuple[int, str, int]:
    clicks = 0
    with log_path.open("w", encoding="utf-8", errors="replace") as log_stream:
        process = subprocess.Popen(command, stdout=log_stream, stderr=subprocess.STDOUT, text=True)
        started = time.monotonic()
        while process.poll() is None:
            clicks += click_permission_dialog(process.pid)
            if time.monotonic() - started > timeout_seconds:
                process.terminate()
                process.wait(timeout=30)
                break
            time.sleep(0.2)
    text = log_path.read_text(encoding="utf-8", errors="replace")
    if clicks:
        with log_path.open("a", encoding="utf-8") as log_stream:
            log_stream.write(f"\nAutomation: accepted {clicks} MCX permission reminder(s).\n")
    return process.returncode, text, clicks


def classify_bgl(path: Path) -> tuple[str, int | None]:
    header = path.read_bytes()[:32]
    if header.startswith(FSX_BGL_MAGIC):
        section_type = header[20] if len(header) > 20 else None
        if section_type == 2:
            return "fsx-object", section_type
        if section_type == 1:
            return "fsx-terrain", section_type
        return "fsx-airport-or-other", section_type
    if header.startswith(b"\x01\x00"):
        return "legacy-compatible", None
    return "unknown", None


def log_has_conversion_errors(text: str) -> bool:
    lowered = text.casefold()
    markers = (" error ", "error c", "failed to", "can not be exported", "cannot be exported")
    return any(marker in lowered for marker in markers)


def unused_path(folder: Path, name: str) -> Path:
    candidate = folder / name
    if not candidate.exists():
        return candidate
    stem, suffix = Path(name).stem, Path(name).suffix
    index = 2
    while True:
        candidate = folder / f"{stem}-{index}{suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def convert_bgls(source: Path, paths: dict[str, Path], dotnet: Path, mcx_dll: Path, pattern: str) -> list[dict]:
    records: list[dict] = []
    failed_dir = paths["work"] / "failed"
    failed_dir.mkdir(exist_ok=True)
    inputs = sorted((source / "Scenery").glob(pattern), key=lambda value: value.name.casefold())
    for index, input_path in enumerate(inputs, 1):
        kind, section_type = classify_bgl(input_path)
        record = {"source": input_path.name, "kind": kind, "section_type": section_type}
        print(f"BGL {index}/{len(inputs)} {input_path.name}: {kind}", flush=True)
        final_path = paths["scenery"] / input_path.name

        if kind == "legacy-compatible":
            if not final_path.exists():
                shutil.copy2(input_path, final_path)
            record.update(status="copied-compatible", output=final_path.name, bytes=final_path.stat().st_size)
            records.append(record)
            continue

        if kind != "fsx-object":
            record.update(status="skipped-unsupported", reason="Airport/terrain/unknown BGL is not safe for MCX object conversion")
            records.append(record)
            continue

        candidate = paths["work"] / "bgl" / input_path.name
        log_path = paths["logs"] / f"bgl-{input_path.stem}.log"
        if final_path.is_file() and final_path.stat().st_size > 0 and log_path.is_file():
            existing_log = log_path.read_text(encoding="utf-8", errors="replace")
            if not log_has_conversion_errors(existing_log):
                record.update(status="verified-existing", output=final_path.name, bytes=final_path.stat().st_size, log=log_path.name)
                records.append(record)
                continue

        if final_path.exists():
            final_path.replace(unused_path(failed_dir, final_path.name))

        command = [str(dotnet), str(mcx_dll), str(input_path), "-format", "BGL_9", "-out", str(candidate)]
        returncode, log_text, permission_clicks = run_mcx(command, log_path)
        log_is_clean = not log_has_conversion_errors(log_text)
        if candidate.is_file() and candidate.stat().st_size > 0 and log_is_clean:
            if not final_path.exists():
                shutil.copy2(candidate, final_path)
            record.update(status="converted", output=final_path.name, bytes=final_path.stat().st_size, log=log_path.name, permission_clicks=permission_clicks)
        else:
            if final_path.exists():
                final_path.replace(unused_path(failed_dir, final_path.name))
            record.update(status="failed", returncode=returncode, log=log_path.name, permission_clicks=permission_clicks)
        records.append(record)
    return records


def alpha_requires_dxt3(image: Image.Image) -> bool:
    if "A" not in image.getbands():
        return False
    minimum, maximum = image.getchannel("A").getextrema()
    if minimum == maximum == 255:
        return False
    colors = image.getchannel("A").getcolors(maxcolors=257)
    if colors is None:
        return True
    return any(value not in (0, 255) for _, value in colors)


def convert_textures(
    source: Path,
    paths: dict[str, Path],
    imagetool: Path,
    force: bool,
    max_texture_size: int,
) -> list[dict]:
    records: list[dict] = []
    inputs = sorted((source / "Texture").glob("*.dds"), key=lambda value: value.name.casefold())
    for index, input_path in enumerate(inputs, 1):
        print(f"TEX {index}/{len(inputs)} {input_path.name}", flush=True)
        tga_path = paths["work"] / "textures" / f"{input_path.stem}.tga"
        candidate = paths["work"] / "textures" / f"{input_path.stem}.bmp"
        final_path = paths["texture"] / f"{input_path.stem}.bmp"
        record = {"source": input_path.name, "output": final_path.name}
        try:
            with Image.open(input_path) as image:
                image.load()
                image = image.convert("RGBA")
                image = ImageOps.flip(image)
                original_size = image.size
                if max(image.size) > max_texture_size:
                    scale = max_texture_size / max(image.size)
                    resized = tuple(max(1, round(value * scale)) for value in image.size)
                    image = image.resize(resized, Image.Resampling.LANCZOS)
                texture_format = "DXT3" if alpha_requires_dxt3(image) else "DXT1"
                image.save(tga_path, format="TGA")
            command = [
                str(imagetool), "-batch", "-nogui", "-nobeep", "-brief", "-nowarning",
                "-bmp", f"-{texture_format}", "-mip", "-e", "bmp", "-o", str(candidate), str(tga_path),
            ]
            completed = run(command)
            log_path = paths["logs"] / f"texture-{input_path.stem}.log"
            if completed.stdout or completed.stderr:
                log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8", errors="replace")
            if candidate.is_file() and candidate.stat().st_size > 0 and candidate.read_bytes()[:2] == b"BM":
                if force or not final_path.exists():
                    shutil.copy2(candidate, final_path)
                record.update(
                    status="converted-flipped",
                    format=texture_format,
                    original_size=list(original_size),
                    output_size=list(image.size),
                    bytes=final_path.stat().st_size,
                )
            else:
                record.update(status="failed", format=texture_format, returncode=completed.returncode)
        except Exception as exc:
            record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        records.append(record)
    return records


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dotnet", type=Path, default=Path(r"C:\Program Files\dotnet\dotnet.exe"))
    parser.add_argument("--mcx-dll", type=Path, required=True)
    parser.add_argument("--imagetool", type=Path, required=True)
    parser.add_argument("--only", choices=("all", "bgl", "texture"), default="all")
    parser.add_argument("--bgl-pattern", default="*.bgl")
    parser.add_argument("--force-textures", action="store_true")
    parser.add_argument("--max-texture-size", type=int, default=1024)
    args = parser.parse_args()

    source = args.source.resolve()
    if not (source / "Scenery").is_dir() or not (source / "Texture").is_dir():
        parser.error("Source must contain Scenery and Texture folders")
    for tool in (args.dotnet, args.mcx_dll, args.imagetool):
        if not tool.is_file():
            parser.error(f"Missing tool: {tool}")

    paths = ensure_layout(source, args.output)
    before = source_hashes(source)
    report_path = paths["logs"] / "conversion-report.json"
    existing_report = {}
    if report_path.is_file():
        try:
            existing_report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing_report = {}
    report: dict = {
        "started": datetime.now().astimezone().isoformat(),
        "source": str(source),
        "output": str(args.output.resolve()),
        "source_hashes_before": before,
    }
    if args.only == "texture" and existing_report.get("bgl"):
        report["bgl"] = existing_report["bgl"]
    if args.only == "bgl" and existing_report.get("textures"):
        report["textures"] = existing_report["textures"]
    if args.only in ("all", "bgl"):
        report["bgl"] = convert_bgls(source, paths, args.dotnet, args.mcx_dll, args.bgl_pattern)
    if args.only in ("all", "texture"):
        if args.max_texture_size < 1:
            parser.error("--max-texture-size must be positive")
        report["textures"] = convert_textures(
            source,
            paths,
            args.imagetool,
            args.force_textures,
            args.max_texture_size,
        )

    after = source_hashes(source)
    report["source_unchanged"] = before == after
    report["finished"] = datetime.now().astimezone().isoformat()
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    if before != after:
        print("ERROR: source hashes changed", file=sys.stderr)
        return 2
    failures = sum(item.get("status") == "failed" for key in ("bgl", "textures") for item in report.get(key, []))
    print(f"Completed with {failures} conversion failures. Report: {report_path}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
