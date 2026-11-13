#!/usr/bin/env python3
"""Pixel Shroom Image Studio Phase 10 — local, opt-in release assembly.

Default action: --check. Nothing here publishes files, tags Git, changes source,
installs software, or modifies the existing installer/portable application.

Requires Python 3.9+ and Git. Use from the Converseen project root.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

APP = "PixelShroomImageStudio"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")

# Required in *the committed repository* to make the released fork rebuildable.
# Do not silently package a stale commit while shipping a newer installer.
REQUIRED_TRACKED = (
    "CMakeLists.txt",
    "src/main.cpp",
    "src/mainwindowimpl.cpp",
    "src/mainwindowimpl.h",
    "src/converter.cpp",
    "src/dialoginfo.cpp",
    "ui/dialoginfo.ui",
    "src/pixelshroom_phase6.h",
    "src/pixelshroom_phase7.h",
    "res/icon.png",
    "res/converseen.ico",
    "PixelShroomImageStudio.iss",
    "build_pixel_shroom_installer.py",
    "pixel_shroom_phase8_prepare.py",
    "pixel_shroom_phase8_package.py",
    "PixelShroom_icon.ico",
)
REQUIRED_PORTABLE = (
    "PixelShroomImageStudio.exe",
    "qt.conf",
    "Qt6Core.dll",
    "Qt6Gui.dll",
    "Qt6Widgets.dll",
    "platforms/qwindows.dll",
    "modules/coders/jpeg.dll",
    "modules/coders/png.dll",
    "modules/coders/webp.dll",
)
LICENSE_NAMES = ("LICENSE", "LICENSE.txt", "LICENSE.md", "COPYING", "COPYING.txt", "COPYING.md")


def cmd(args: list[str], cwd: Path, binary=False) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=str(cwd), check=False, capture_output=True,
                          **({} if binary else {"text": True, "errors": "replace"}))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def archive_exe_matches(portable_zip: Path, standalone_exe: Path) -> bool:
    expected = sha256(standalone_exe)
    with zipfile.ZipFile(portable_zip) as zf:
        matches = [name for name in zf.namelist()
                   if name.replace('\\', '/').split('/')[-1].lower() == 'pixelshroomimagestudio.exe']
        if len(matches) != 1:
            raise ValueError("Portable ZIP must contain exactly one PixelShroomImageStudio.exe")
        digest = hashlib.sha256()
        with zf.open(matches[0]) as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest() == expected


def preflight(root: Path, version: str, kit: Path):
    errors, warnings = [], []
    installer = root / 'dist' / 'installer' / f'{APP}-Setup-{version}-Win64.exe'
    portable = root / 'dist' / f'{APP}-Portable'
    portable_zip = root / 'dist' / f'{APP}-Portable-Win64.zip'
    notes = kit / 'RELEASE_NOTES_v1.0.0.md'

    if not VERSION_RE.fullmatch(version):
        errors.append('Version should have numeric major.minor.patch form (e.g., 1.0.0).')
    if not installer.is_file():
        errors.append(f'Installer not found: {installer}')
    else:
        if installer.stat().st_size < 100000:
            errors.append('Installer is unexpectedly small (<100 KB).')
        existing = installer.with_name(installer.name + '.sha256.txt')
        if existing.is_file():
            digest = sha256(installer)
            declared = existing.read_text(encoding='utf-8-sig', errors='replace').strip().split()
            if not declared or declared[0].lower() != digest:
                errors.append(f'Existing installer checksum disagrees with actual bytes: {existing}')
    if not portable.is_dir():
        errors.append(f'Tested portable directory missing: {portable}')
    else:
        for rel in REQUIRED_PORTABLE:
            if not (portable / rel).is_file():
                errors.append(f'Portable runtime file missing: {rel}')
        license_dir = portable / 'licenses'
        if not license_dir.is_dir() or not any(p.is_file() for p in license_dir.iterdir()):
            errors.append('The portable distribution needs actual license files under licenses/.')
        else:
            warnings.append('Review all bundled Qt, ImageMagick, and other library license/notice obligations; license directory existence alone is not enough.')
    if portable_zip.exists() and portable.is_dir() and (portable / f'{APP}.exe').is_file():
        try:
            if not archive_exe_matches(portable_zip, portable / f'{APP}.exe'):
                errors.append('Portable ZIP contains a DIFFERENT EXE from portable folder: rebuild portable ZIP before releasing.')
        except (ValueError, zipfile.BadZipFile, OSError) as exc:
            errors.append(f'Could not validate portable ZIP: {exc}')
    elif not portable_zip.exists():
        warnings.append('Portable ZIP not found; installer-only binary release is possible.')
    if not notes.is_file():
        errors.append(f'Release notes template not found beside script: {notes}')

    if not shutil.which('git'):
        errors.append('Git is not on PATH. Source archive must come from a committed repository.')
        return errors, warnings, {}, installer, portable, portable_zip, notes
    repo = cmd(['git', 'rev-parse', '--show-toplevel'], root)
    if repo.returncode or Path(repo.stdout.strip()).resolve() != root:
        errors.append('Project folder must be the Git repository root containing the final modified source.')
        return errors, warnings, {}, installer, portable, portable_zip, notes
    revision = cmd(['git', 'rev-parse', 'HEAD'], root)
    dirty = cmd(['git', 'status', '--porcelain', '--untracked-files=no'], root)
    if revision.returncode:
        errors.append('Git has no accessible HEAD commit.')
    if dirty.returncode or dirty.stdout.strip():
        errors.append('Tracked source has uncommitted changes. Commit final source AND build scripts before preparing a release.')
        if dirty.stdout.strip():
            warnings.append('Tracked changes:\n' + '\n'.join('  ' + line for line in dirty.stdout.splitlines()[:20]))
    tracked = cmd(['git', 'ls-files', '--cached', '--full-name'], root)
    tracked_set = set(tracked.stdout.splitlines()) if tracked.returncode == 0 else set()
    missing = [file for file in REQUIRED_TRACKED if file not in tracked_set]
    if missing:
        errors.append('Required release source/build files are not committed:\n  ' + '\n  '.join(missing))
    if not any(name in tracked_set for name in LICENSE_NAMES):
        errors.append('No tracked root license file (LICENSE/COPYING). Include the genuine Converseen GPL license text.')

    untracked = cmd(['git', 'ls-files', '--others', '--exclude-standard'], root)
    if untracked.returncode == 0:
        risk = [s for s in untracked.stdout.splitlines()
                if s.startswith(('src/', 'ui/', 'res/', 'tools/')) or
                s.lower().endswith(('.iss', '.qrc', '.rc')) or
                s.startswith(('pixel_shroom_phase8_', 'build_pixel_shroom_'))]
        if risk:
            errors.append('Untracked source/build resources might be excluded from Git source archive:\n  '
                          + '\n  '.join(risk[:25]))
    tag = 'v' + version
    tag_sha = cmd(['git', 'rev-list', '-n', '1', tag], root)
    if tag_sha.returncode == 0 and tag_sha.stdout.strip() and revision.returncode == 0:
        if tag_sha.stdout.strip() != revision.stdout.strip():
            errors.append(f'Tag {tag} exists but points to a different commit. Never silently retag a release.')
    meta = {
        'commit': revision.stdout.strip() if revision.returncode == 0 else None,
        'git_remote': '', 'version': version, 'tag': tag,
    }
    remote = cmd(['git', 'remote', 'get-url', 'origin'], root)
    if remote.returncode == 0:
        meta['git_remote'] = remote.stdout.strip()
    warnings.append('Source/installer correspondence and clean-Windows compatibility require manual confirmation; this script cannot establish them automatically.')
    return errors, warnings, meta, installer, portable, portable_zip, notes


def prepare(root: Path, version: str, kit: Path, meta: dict,
            installer: Path, portable_zip: Path, notes: Path):
    target = root / 'dist' / f'release-v{version}'
    if target.exists():
        raise RuntimeError(f'Refusing to replace an existing release folder: {target}')
    target.parent.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(dir=target.parent, prefix='.release-staging-') as tmp:
        stage = Path(tmp) / f'release-v{version}'
        stage.mkdir()
        assets = []
        def add_copy(file: Path):
            dest = stage / file.name
            shutil.copy2(file, dest)
            assets.append(dest)

        add_copy(installer)
        if portable_zip.is_file():
            add_copy(portable_zip)
        source_name = f'{APP}-v{version}-source.zip'
        source = stage / source_name
        archive_cmd = cmd(['git', 'archive', '--format=zip', f'--output={source}',
                           f'--prefix={APP}-v{version}-source/', 'HEAD'], root)
        if archive_cmd.returncode != 0:
            raise RuntimeError(f'git archive failed: {archive_cmd.stderr}')
        with zipfile.ZipFile(source) as zf:
            names = set(zf.namelist())
            for required in REQUIRED_TRACKED:
                if f'{APP}-v{version}-source/{required}' not in names:
                    raise RuntimeError(f'Git source archive omitted: {required}')
            if not any(f'{APP}-v{version}-source/{lic}' in names for lic in LICENSE_NAMES):
                raise RuntimeError('Archive is missing tracked GPL license file.')
        assets.append(source)
        add_copy(notes)

        lines = []
        artifact_info = []
        for p in assets:
            digest = sha256(p)
            lines.append(f'{digest}  {p.name}')
            artifact_info.append({'name': p.name, 'size_bytes': p.stat().st_size, 'sha256': digest})
        (stage / 'SHA256SUMS.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
        manifest = {
            'application': 'Pixel Shroom Image Studio',
            'version': version,
            'prepared_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
            'git_commit': meta.get('commit'),
            'git_tag_intended': meta.get('tag'),
            'origin_url': meta.get('git_remote'),
            'artifacts': artifact_info,
            'public_release_validated': False,
            'manual_gates': ['Corresponding source confirmed', 'License notices reviewed',
                             'Clean Windows PC tested', 'Installation and uninstall verified',
                             'Installer checksum verified'],
        }
        (stage / 'RELEASE_MANIFEST.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        shutil.copy2(kit / 'RELEASE_CHECKLIST.md', stage / 'RELEASE_CHECKLIST.md')
        stage.rename(target)
    return target


def verify(directory: Path) -> bool:
    checksums = directory / 'SHA256SUMS.txt'
    if not checksums.is_file():
        print(f'FAIL: no SHA256SUMS.txt in {directory}')
        return False
    good = True
    for line in checksums.read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([a-fA-F0-9]{64})  ([^\\/]+)', line)
        if not match:
            print('FAIL: malformed checksum entry:', line)
            good = False
            continue
        digest, name = match.groups()
        file = directory / name
        if not file.is_file() or sha256(file).lower() != digest.lower():
            print('FAIL:', name)
            good = False
        else:
            print('PASS:', name)
    return good


def main() -> int:
    ap = argparse.ArgumentParser(description='Prepare/check release artifacts; does not publish GitHub releases')
    ap.add_argument('--project', type=Path, default=Path.cwd())
    ap.add_argument('--version', default='1.0.0')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--check', action='store_true', help='safe default: read-only validation')
    group.add_argument('--prepare', action='store_true', help='assemble draft release files')
    group.add_argument('--verify', action='store_true', help='verify existing release folder checksums')
    args = ap.parse_args()
    root = args.project.resolve()
    kit = Path(__file__).resolve().parent
    if args.verify:
        target = root / 'dist' / f'release-v{args.version}'
        return 0 if verify(target) else 2
    errors, warnings, meta, installer, portable, portable_zip, notes = preflight(root, args.version, kit)
    print(f'Project: {root}')
    print(f'Installer: {installer}')
    print(f'Portable: {portable}')
    print(f'Git commit: {meta.get("commit") or "unknown"}')
    print(f'Git origin: {meta.get("git_remote") or "not detected"}')
    for warning in warnings:
        print('NOTE:', warning)
    for error in errors:
        print('BLOCKER:', error, file=sys.stderr)
    if errors:
        print(f'NOT READY: {len(errors)} release-preparation blocker(s). No release files created.')
        return 2
    if not args.prepare:
        print('CHECK PASSED. Review RELEASE_CHECKLIST.md and run with --prepare to assemble release files.')
        return 0
    try:
        target = prepare(root, args.version, kit, meta, installer, portable_zip, notes)
    except (OSError, RuntimeError, zipfile.BadZipFile) as exc:
        print(f'PREPARE FAILED: {exc}', file=sys.stderr)
        return 3
    print(f'RELEASE ARTIFACTS PREPARED: {target}')
    print('Release remains UNPUBLISHED and NOT yet validated on a clean Windows PC.')
    print('Run --verify, complete checklist, then manually create GitHub draft release.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
