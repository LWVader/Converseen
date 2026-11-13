#!/usr/bin/env python3
"""Pixel Shroom Image Studio branding assets installer.

Dry-run by default. Replaces only 2 source artwork assets and makes backups.
This intentionally does not modify existing application logic, CMake, or license.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import hashlib
import sys
import re

ASSETS = {
    'PixelShroom_icon.png': Path('res/icon.png'),
    'PixelShroom_icon.ico': Path('res/converseen.ico'),
}


def hash_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as fp:
        for part in iter(lambda: fp.read(1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description='Install Pixel Shroom app icons safely (dry run by default).')
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Converseen repository root')
    parser.add_argument('--assets', type=Path, default=Path(__file__).resolve().parent,
                        help='Directory holding PixelShroom_icon.png and .ico')
    parser.add_argument('--apply', action='store_true', help='Back up and replace the existing icons')
    args = parser.parse_args()
    root, asset_root = args.project.resolve(), args.assets.resolve()

    try:
        if not (root/'CMakeLists.txt').is_file() or not (root/'resources.qrc').is_file() or not (root/'converseen.rc').is_file():
            raise RuntimeError('Not the Converseen source root (missing CMakeLists.txt/resources.qrc/converseen.rc).')
        resources = (root/'resources.qrc').read_text(encoding='utf-8')
        windows_rc = (root/'converseen.rc').read_text(encoding='utf-8', errors='replace')
        cmake = (root/'CMakeLists.txt').read_text(encoding='utf-8',errors='replace')
        if '<file>res/icon.png</file>' not in resources:
            raise RuntimeError('resources.qrc does not reference res/icon.png; source layout changed. No files modified.')
        if not re.search(r'res\\+converseen\.ico',windows_rc,flags=re.I):
            raise RuntimeError('converseen.rc does not reference res\\converseen.ico; source layout changed. No files modified.')
        if 'resources.qrc' not in cmake or 'converseen.rc' not in cmake:
            raise RuntimeError('CMakeLists.txt is missing expected Qt/Windows resource references. No files modified.')

        changes = []
        for source_name, relative_target in ASSETS.items():
            src = asset_root / source_name
            dest = root / relative_target
            if not src.is_file():
                raise RuntimeError(f'Missing branding asset: {src}')
            if not dest.is_file():
                raise RuntimeError(f'Missing original source asset: {dest}')
            hdr = src.read_bytes()[:8]
            if src.suffix == '.png' and hdr != b'\x89PNG\r\n\x1a\n':
                raise RuntimeError(f'Not a PNG file: {src}')
            if src.suffix == '.ico' and not hdr.startswith(b'\x00\x00\x01\x00'):
                raise RuntimeError(f'Not an ICO file: {src}')
            if src.resolve() == dest.resolve():
                raise RuntimeError('Asset source and target are identical; choose an external asset directory.')
            if hash_file(src) != hash_file(dest):
                changes.append((src,dest,relative_target))
        if not changes:
            print('ALREADY INSTALLED: both app icons match. No files changed.')
            return 0
        print('Pixel Shroom icon installation plan:')
        for src, dest, rel in changes:
            print(f'  {src} -> {dest}')
        print('Source files / resources / executable / build directories: NOT modified by this script.')
        if not args.apply:
            print('DRY RUN PASSED. Run again with --apply to back up and install icons.')
            return 0
        backups = root / 'phase8-backups' / ('logo-assets-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
        for _, dest, rel in changes:
            target = backups / rel
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(dest,target)
        try:
            for src, dest, _ in changes:
                shutil.copy2(src,dest)
        except BaseException:
            for _, dest, rel in changes:
                shutil.copy2(backups/rel,dest)
            raise
        print('ICONS INSTALLED. Backup:',backups)
        print('Rebuild build-portable (and repackage) to embed the new Windows and Qt icons.')
        print('If not already applied, run the separate Phase 8.1 source branding patch before rebuilding.')
        return 0
    except Exception as exc:
        print('ERROR:',exc,file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
