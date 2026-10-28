#!/usr/bin/env python3
"""Phase 9 — validate the tested portable release and compile Inno Setup installer.

Run from Windows PowerShell in the Converseen project root; by default this
script only checks inputs. Use --build to compile an installer with Inno Setup.
No modifications to the portable folder, development build, source or assets.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

EXE = "PixelShroomImageStudio.exe"
ISS = "PixelShroomImageStudio.iss"
ICO = "PixelShroom_icon.ico"
VERSION_RE = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
REQUIRED = (
    EXE,
    "qt.conf",
    "Qt6Core.dll", "Qt6Gui.dll", "Qt6Widgets.dll",
    "platforms/qwindows.dll",
    "modules/coders/jpeg.dll", "modules/coders/png.dll",
    "modules/coders/webp.dll", "modules/coders/magick.dll",
    "modules/coders/magick.la",
)

def is_within(path: Path, folder: Path) -> bool:
    try:
        path.relative_to(folder)
        return True
    except ValueError:
        return False


def locate_iscc(explicit: str | None) -> Path | None:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    on_path = shutil.which("ISCC.exe") or shutil.which("iscc")
    if on_path:
        candidates.append(Path(on_path))
    for program_files in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')):
        if not program_files:
            continue
        for version in ('7', '6'):
            candidates.append(Path(program_files) / f'Inno Setup {version}' / 'ISCC.exe')
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build Pixel Shroom Windows installer from tested portable app")
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Converseen repository root')
    parser.add_argument('--portable', type=Path, help='override portable folder (must already exist)')
    parser.add_argument('--version', default='1.0.0', help='installer version e.g. 1.0.0')
    parser.add_argument('--iscc', help='full path to Inno Setup ISCC.exe if not automatically found')
    parser.add_argument('--build', action='store_true', help='actually compile (otherwise check only)')
    args = parser.parse_args(argv)
    project = args.project.resolve()
    portable = (args.portable if args.portable else project / 'dist' / 'PixelShroomImageStudio-Portable').resolve()
    script = project / ISS
    icon = project / ICO
    output = project / 'dist' / 'installer'
    filename = f'PixelShroomImageStudio-Setup-{args.version}-Win64.exe'
    errors, warnings = [], []

    if not VERSION_RE.fullmatch(args.version):
        errors.append('Version must use three numeric parts (e.g. 1.0.0).')
    for p in (script, icon):
        if not p.is_file():
            errors.append(f'Missing installer kit file: {p}')
    if not portable.is_dir():
        errors.append(f'Missing portable distribution folder: {portable}')
    else:
        for rel in REQUIRED:
            if not (portable / rel).is_file():
                errors.append(f'Missing runtime file: {portable / rel}')
        if not (portable / 'imagemagick' / 'config').is_dir():
            errors.append('ImageMagick configuration folder missing: imagemagick/config')
        else:
            if not list((portable/'imagemagick'/'config').glob('*.xml')):
                errors.append('ImageMagick XML configuration is empty.')
        # Refuse external symlinks/reparse points that could leak local files.
        for p in portable.rglob('*'):
            if p.is_symlink():
                errors.append(f'Symlink in portable folder is not supported: {p}')
                if len(errors) > 15:
                    break
        lic = portable / 'licenses'
        if not lic.is_dir() or not any(p.is_file() for p in lic.iterdir()):
            warnings.append('No license files found in portable/licenses; add required third-party licenses before public distribution.')
        if not (portable / 'READ_ME_FIRST.txt').is_file():
            warnings.append('Portable README not found (not fatal).')
        count = sum(1 for p in portable.rglob('*') if p.is_file())
        size = sum(p.stat().st_size for p in portable.rglob('*') if p.is_file() and not p.is_symlink())
        print(f'Portable input: {portable}')
        print(f'Files: {count}; total: {size/(1024*1024):.1f} MiB')
    print(f'Installer source: {script}')
    print(f'Brand icon: {icon}')
    print(f'Installer destination: {output / filename}')
    if warnings:
        for msg in warnings:
            print('WARNING:', msg)
    if errors:
        for msg in errors:
            print('ERROR:', msg, file=sys.stderr)
        print('CHECK FAILED — nothing was changed.', file=sys.stderr)
        return 2
    if not args.build:
        print('CHECK PASSED — no changes made. Run again with --build to compile.')
        return 0
    if os.name != 'nt':
        print('ERROR: Actual installer compilation requires Windows with Inno Setup.', file=sys.stderr)
        return 3
    compiler = locate_iscc(args.iscc)
    if not compiler:
        print('ERROR: Inno Setup ISCC.exe not found. Install Inno Setup 7 or provide --iscc path.', file=sys.stderr)
        return 3
    target = output / filename
    if target.exists():
        print(f'ERROR: Refusing to overwrite existing installer: {target}\nUse a new --version or back up/remove the old installer.', file=sys.stderr)
        return 3
    # Prevent accidentally compiling source folders or reading artifact output as app payload.
    if is_within(portable, output) or is_within(output, portable):
        print('ERROR: Installer output and portable source must be separate.', file=sys.stderr)
        return 3
    output.mkdir(parents=True, exist_ok=True)
    cmd = [str(compiler),
           f'/DProductVersion={args.version}',
           f'/DPortableFolder={portable}',
           f'/DInstallerOutFolder={output}',
           f'/DBrandIconFile={icon}', str(script)]
    print('Building installer with:', compiler, flush=True)
    completed = subprocess.run(cmd, cwd=str(project), check=False)
    if completed.returncode != 0 or not target.is_file():
        print('ERROR: Inno Setup compile failed. See messages above.', file=sys.stderr)
        return completed.returncode or 4
    digest = hashlib.sha256()
    with target.open('rb') as fin:
        while block := fin.read(1024*1024):
            digest.update(block)
    hash_file = output / (target.name + '.sha256.txt')
    hash_file.write_text(f'{digest.hexdigest()}  {target.name}\n', encoding='utf-8')
    print('\nINSTALLER CREATED:', target)
    print('SHA256:', digest.hexdigest())
    print('Next: install on your PC, test images/300DPI, uninstall, then test on clean Windows.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
