#!/usr/bin/env python3
"""Validate one Pixel Shroom website upload image (read-only).

Example:
    py -3 tests/verify_website_export.py \
      --source "C:\\art\\source.png" --original "C:\\output\\source__original.jpg"

Requires ImageMagick's "magick" executable in PATH. The original image is
expected to retain source pixel dimensions and embedded source DPI.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys

MIB = 1024 * 1024


def identify(path: Path) -> tuple[int, int, float | None]:
    command = shutil.which("magick")
    if not command:
        raise RuntimeError("ImageMagick 'magick' command is not in PATH")
    result = subprocess.run(
        [command, "identify", "-ping", "-format",
         "%w %h %x %y %[units]", str(path)],
        check=True, capture_output=True, text=True,
    )
    fields = result.stdout.strip().split()
    if len(fields) != 5:
        raise RuntimeError("Unexpected ImageMagick output: " + result.stdout)
    width, height = int(fields[0]), int(fields[1])
    x, y = float(fields[2]), float(fields[3])
    units = fields[4]
    dpi = None
    if units == "PixelsPerInch":
        dpi = (x + y) / 2.0
    elif units == "PixelsPerCentimeter":
        dpi = (x + y) * 1.27
    return width, height, dpi


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--original", required=True, type=Path,
                        help="Single website upload image; no preview required")
    args = parser.parse_args()

    for path in (args.source, args.original):
        if not path.is_file():
            parser.error(f"File not found: {path}")

    sw, sh, sdpi = identify(args.source)
    ow, oh, odpi = identify(args.original)
    file_size = args.original.stat().st_size
    errors: list[str] = []
    if (sw, sh) != (ow, oh):
        errors.append(f"Pixel dimensions changed: {sw}x{sh} -> {ow}x{oh}")
    if file_size >= 50 * MIB:
        errors.append(f"Output is not strictly below 50 MiB: {file_size / MIB:.2f} MiB")
    if sdpi is not None and (odpi is None or abs(sdpi - odpi) > 1.5):
        errors.append(f"Print DPI changed or disappeared: {sdpi} -> {odpi}")

    print(f"Source: {sw} x {sh}, DPI: {sdpi}")
    print(f"Upload: {ow} x {oh}, size: {file_size / MIB:.2f} MiB, DPI: {odpi}")
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS: single upload image meets full-resolution, 50 MiB and known-DPI checks.")
    print("NOTE: This does not verify ICC/EXIF profiles or pixel equivalence.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (RuntimeError, OSError, subprocess.CalledProcessError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(2)
