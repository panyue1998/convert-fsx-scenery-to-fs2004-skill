#!/usr/bin/env python3
"""Export a scenery BGL to an inspection format through ModelConverterX."""

from __future__ import annotations

import argparse
import importlib.util
import shutil
import threading
import time
from pathlib import Path


def load_conversion_helpers():
    script = Path(__file__).with_name("convert_scenery.py")
    spec = importlib.util.spec_from_file_location("convert_scenery", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load conversion helpers from {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--format", default="XML")
    parser.add_argument("--dotnet", type=Path, required=True)
    parser.add_argument("--mcx-dll", type=Path, required=True)
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument(
        "--capture-temp-xml",
        type=Path,
        help="Copy MCX's transient BGLComp XML before it is cleaned up",
    )
    args = parser.parse_args()

    for path in (args.source, args.dotnet, args.mcx_dll):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    helpers = load_conversion_helpers()
    command = [
        str(args.dotnet),
        str(args.mcx_dll),
        str(args.source),
        "-format",
        args.format,
        "-out",
        str(args.output),
    ]
    stop_capture = threading.Event()
    capture_thread = None
    if args.capture_temp_xml:
        args.capture_temp_xml.parent.mkdir(parents=True, exist_ok=True)
        transient_xml = args.output.with_suffix(".xml")

        def capture_xml() -> None:
            while not stop_capture.is_set():
                try:
                    if transient_xml.is_file() and transient_xml.stat().st_size:
                        shutil.copy2(transient_xml, args.capture_temp_xml)
                except (OSError, shutil.Error):
                    pass
                time.sleep(0.01)

        capture_thread = threading.Thread(target=capture_xml, daemon=True)
        capture_thread.start()

    returncode, log_text, clicks = helpers.run_mcx(command, args.log, 1800)
    stop_capture.set()
    if capture_thread:
        capture_thread.join(timeout=2)
    size = args.output.stat().st_size if args.output.is_file() else 0
    print(f"returncode={returncode} permission_clicks={clicks} output_bytes={size}")
    if returncode != 0 or size == 0:
        print(log_text[-4000:])
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
