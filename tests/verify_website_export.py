#!/usr/bin/env python3
"""Check an existing Pixel Shroom website export pair (no files are changed).

Example:
    py -3 tests/verify_website_export.py --source art.png \
        --original exports/art__original.jpg --preview exports/art__preview.webp \
        --max-width 2048 --max-height 2048
Requires ImageMagick's 'magick' command in PATH.
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

MIB = 1024 * 1024


def identify(path: pathlib.Path) -> tuple[int, int, float | None]:
    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick 'magick' must be available in PATH")
    result = subprocess.run(
        [magick, "identify", "-ping", "-format", "%w %h %x %y %[units]", str(path)],
        check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    parts = result.stdout.strip().split()
    if len(parts) != 5:
        raise RuntimeError(f"Unexpected identify output for {path}: {result.stdout!r}")
    width, height = map(int, parts[:2])
    x, y = map(float, parts[2:4])
    units = parts[4]
    if units == "PixelsPerCentimeter":
        density = (x + y) * 1.27
    elif units == "PixelsPerInch":
        density = (x + y) / 2.0
    else:
        density = None
    return width, height, density


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("source", "original", "preview"):
        parser.add_argument("--" + flag, required=True, type=pathlib.Path)
    parser.add_argument("--max-width", type=int, default=None)
    parser.add_argument("--max-height", type=int, default=None)
    args = parser.parse_args()

    for p in (args.source, args.original, args.preview):
        if not p.is_file():
            parser.error(f"File does not exist: {p}")

    source_w, source_h, source_dpi = identify(args.source)
    original_w, original_h, original_dpi = identify(args.original)
    preview_w, preview_h, _ = identify(args.preview)
    original_bytes = args.original.stat().st_size
    preview_bytes = args.preview.stat().st_size
    problems: list[str] = []

    if original_bytes >= 50 * MIB:
        problems.append(f"Original is NOT under 50 MiB: {original_bytes / MIB:.2f} MiB")
    if preview_bytes >= 10 * MIB:
        problems.append(f"Preview is NOT under 10 MiB: {preview_bytes / MIB:.2f} MiB")
    if (source_w, source_h) != (original_w, original_h):
        problems.append("Original pixel dimensions differ from the source")
    if preview_w > source_w or preview_h > source_h:
        problems.append("Preview unexpectedly exceeds original dimensions")
    if args.max_width is not None and preview_w > args.max_width:
        problems.append("Preview exceeds Resize width")
    if args.max_height is not None and preview_h > args.max_height:
        problems.append("Preview exceeds Resize height")
    if source_dpi is not None:
        if original_dpi is None or abs(source_dpi - original_dpi) > 1.5:
            problems.append("Original print DPI differs or is missing")

    print(f"Source:   {source_w} x {source_h}, DPI: {source_dpi}")
    print(f"Original: {original_w} x {original_h}, {original_bytes / MIB:.2f} MiB, DPI: {original_dpi}")
    print(f"Preview:  {preview_w} x {preview_h}, {preview_bytes / MIB:.2f} MiB")
    if problems:
        for item in problems:
            print("FAIL:", item)
        return 1
    print("PASS: Sizes, dimensions and available DPI metadata meet website export rules")
    print("NOTE: This script does not prove pixel equivalence or ICC profile preservation.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
