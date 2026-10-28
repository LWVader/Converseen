#!/usr/bin/env python3
"""Pixel Shroom Phase 8 - collect a Windows UCRT64 portable application.

Requires a successful separate CMake build-portable and current MSYS2 UCRT64.
Does not touch the working development build/ folder. Run on Windows Python 3.
"""
from __future__ import annotations
import argparse
from collections import deque
from datetime import datetime
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

# Only selected basic image modules are shipped for the *first* portable build.
# Avoid trying to bundle every third-party delegate (some, including FLIF,
# are known not to load reliably even on the development machine).
ESSENTIAL_CODERS = {'jpeg', 'png', 'webp', 'magick'}
EXTRA_CODERS = {
    'bmp', 'gif', 'tiff', 'ico', 'miff', 'meta', 'rgb', 'gray',
    'txt', 'label', 'gradient', 'xc', 'null', 'info', 'histogram'
}
SYSTEM_DLLS = {
    'ntdll.dll','kernel32.dll','kernelbase.dll','user32.dll','gdi32.dll',
    'gdi32full.dll','win32u.dll','advapi32.dll','sechost.dll','rpcrt4.dll',
    'ucrtbase.dll','msvcrt.dll','ole32.dll','oleaut32.dll','combase.dll',
    'comdlg32.dll','shell32.dll','shlwapi.dll','shcore.dll','uxtheme.dll',
    'dwmapi.dll','ws2_32.dll','wsock32.dll','winmm.dll','version.dll',
    'imm32.dll','msctf.dll','setupapi.dll','cfgmgr32.dll','dnsapi.dll',
    'crypt32.dll','bcrypt.dll','cryptbase.dll','ncrypt.dll','secur32.dll',
    'wtsapi32.dll','iphlpapi.dll','netapi32.dll','mpr.dll','winspool.drv',
    'uuid.dll','psapi.dll','powrprof.dll','userenv.dll','winhttp.dll',
    'wininet.dll','normaliz.dll','msimg32.dll','comctl32.dll','usp10.dll',
    'dwrite.dll','d2d1.dll','dxgi.dll','d3d11.dll','d3d12.dll',
    'd3dcompiler_47.dll','opengl32.dll','glu32.dll','cfgmgr32.dll',
    'mswsock.dll','cryptui.dll','wintrust.dll','msasn1.dll','dbghelp.dll',
    'propsys.dll','windows.storage.dll','avrt.dll','hid.dll','dinput8.dll',
    'mmdevapi.dll','mfplat.dll','mf.dll','mfreadwrite.dll','dxva2.dll',
    'msacm32.dll','wldap32.dll','winmm.dll','pdh.dll','ntmarta.dll',
    'netutils.dll','samcli.dll','wlanapi.dll','prntvpt.dll','msvcp_win.dll',
    'api-ms-win-crt-private-l1-1-0.dll',
    'authz.dll', 'd3d9.dll', 'mscms.dll',
}
DLL_PATTERN = re.compile(r'\bDLL Name:\s*(\S+)', flags=re.IGNORECASE)


def run(command: list[str], **kwargs) -> subprocess.CompletedProcess:
    print('>', ' '.join(str(part) for part in command), flush=True)
    completed = subprocess.run(command, text=True, errors='replace',
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               check=False, **kwargs)
    if completed.stdout:
        print(completed.stdout[-7000:], flush=True)
    if completed.returncode:
        raise RuntimeError(f'Command failed ({completed.returncode}): {command[0]}')
    return completed


def copy_file(source: Path, destination: Path) -> None:
    if not source.is_file():
        raise FileNotFoundError(f'Cannot find required file: {source}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def image_magick_location(ucrt: Path) -> Path:
    versions = [p for p in (ucrt / 'lib').glob('ImageMagick-*') if p.is_dir()]
    if not versions:
        raise FileNotFoundError(f'No ImageMagick module directory under {ucrt / "lib"}')
    # Don't silently guess if two versioned directories are installed.
    if len(versions) != 1:
        raise RuntimeError('Several ImageMagick library versions found: ' + ', '.join(str(p) for p in versions))
    return versions[0]


def copy_imagemagick(ucrt: Path, stage: Path) -> dict:
    base = image_magick_location(ucrt)
    module_dirs = sorted(p for p in base.glob('modules-*/coders') if p.is_dir())
    if len(module_dirs) != 1:
        raise RuntimeError(f'Expected exactly one ImageMagick coder directory in {base}, found {module_dirs}')
    modules = module_dirs[0]
    copied = []
    for coder in sorted(ESSENTIAL_CODERS | EXTRA_CODERS):
        source = modules / f'{coder}.dll'
        if not source.exists():
            if coder in ESSENTIAL_CODERS:
                raise FileNotFoundError(f'Missing required ImageMagick coder: {source}')
            continue
        copy_file(source, stage / 'modules' / 'coders' / source.name)
        la = modules / f'{coder}.la'
        if la.is_file():
            copy_file(la, stage / 'modules' / 'coders' / la.name)
        elif coder == 'magick':
            raise FileNotFoundError(f'Missing required ImageMagick module index: {la}')
        copied.append(coder)

    # Load PNG/JPEG/WebP and other formats without accessing C:\\msys64.
    # MSYS2 stores ImageMagick XML in several locations.
    config_dir = stage / 'imagemagick/config'
    config_dir.mkdir(parents=True, exist_ok=True)
    inputs = [
        ucrt / 'etc' / 'ImageMagick-7',
        ucrt / 'share' / 'ImageMagick-7',
        *base.glob('config-*'),
    ]
    config_files = []
    for input_dir in inputs:
        if not input_dir.is_dir():
            continue
        for xml in input_dir.glob('*.xml'):
            target = config_dir / xml.name
            if target.exists():
                continue  # Prefer etc/ over share/ over compiled config defaults.
            copy_file(xml, target)
            config_files.append(xml.name)
    if not config_files:
        raise RuntimeError('No ImageMagick XML config files were found.')

    # Module filters, if present, are typically not needed for basic conversion.
    return {'coders': copied, 'configs': config_files, 'imagemagick_version_dir': base.name}


def qt_plugins(ucrt: Path, stage: Path) -> None:
    plugins = ucrt / 'share' / 'qt6' / 'plugins'
    required = [('platforms', 'qwindows.dll')]
    optional = [('imageformats','qjpeg.dll'), ('imageformats','qgif.dll'),
                ('imageformats','qico.dll'), ('styles','qmodernwindowsstyle.dll')]
    for subdir, file_name in required:
        destination = stage / subdir / file_name
        if not destination.is_file():
            copy_file(plugins / subdir / file_name, destination)
    for subdir, file_name in optional:
        source = plugins / subdir / file_name
        if source.is_file():
            copy_file(source, stage / subdir / file_name)
    (stage / 'qt.conf').write_text('[Paths]\nPrefix=.\nPlugins=.\nTranslations=translations\n', encoding='utf-8')


def is_system(name: str) -> bool:
    name = name.lower()
    if name.startswith(('api-ms-win-', 'ext-ms-win-')):
        return True
    return name in SYSTEM_DLLS


def binary_imports(binary: Path, objdump: Path) -> set[str]:
    result = subprocess.run([str(objdump), '-p', str(binary)],
                            text=True, errors='replace',
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False)
    if result.returncode:
        raise RuntimeError(f'objdump could not inspect {binary}: {result.stderr[-1000:]}')
    return {match.group(1) for match in DLL_PATTERN.finditer(result.stdout)}


def collect_dlls(stage: Path, ucrt: Path, objdump: Path) -> dict:
    binaries = {p for p in stage.rglob('*') if p.suffix.lower() in ('.exe','.dll') and p.is_file()}
    queue = deque(sorted(binaries))
    scanned = set()
    copied = set()
    missing = set()
    ucrt_bin = ucrt / 'bin'
    while queue:
        binary = queue.popleft()
        if binary in scanned:
            continue
        scanned.add(binary)
        for name in binary_imports(binary, objdump):
            if is_system(name):
                continue
            local = stage / name
            if local.is_file():
                if local not in scanned:
                    queue.append(local)
                continue
            source = ucrt_bin / name
            if source.is_file():
                copy_file(source, local)
                copied.add(name)
                queue.append(local)
                continue
            # Any unknown import not in UCRT is a packaging blocker. It may
            # be available on the developer's PC, but not on a clean system.
            missing.add((binary.name, name))
    if missing:
        problems = '\n'.join(f'  {binary}: {dll}' for binary, dll in sorted(missing))
        raise RuntimeError('Unresolved imports (ZIP not created):\n' + problems)
    return {'scanned_binaries': len(scanned), 'copied_runtime_dlls': sorted(copied)}


def verify_staging(stage: Path, data: dict) -> None:
    required = [
        stage / 'PixelShroomImageStudio.exe',
        stage / 'Qt6Core.dll', stage / 'Qt6Gui.dll', stage / 'Qt6Widgets.dll',
        stage / 'platforms/qwindows.dll',
        stage / 'modules/coders/jpeg.dll', stage / 'modules/coders/png.dll',
        stage / 'modules/coders/webp.dll', stage / 'modules/coders/magick.dll',
        stage / 'modules/coders/magick.la', stage / 'qt.conf',
    ]
    missing = [str(path) for path in required if not path.is_file()]
    if missing:
        raise RuntimeError('Portable package is incomplete:\n' + '\n'.join(missing))
    if len(data['coders']) < 4:
        raise RuntimeError('Not all required ImageMagick coders were packaged.')


def write_support_files(stage: Path, project: Path, release_dir: Path, data: dict) -> None:
    shutil.copy2(release_dir / 'PORTABLE_README.txt', stage / 'READ_ME_FIRST.txt')
    license_dir = stage / 'licenses'
    license_dir.mkdir(exist_ok=True)
    licenses = []
    for pattern in ('COPYING*', 'LICENSE*'):
        licenses.extend([p for p in project.glob(pattern) if p.is_file()])
    if not licenses:
        print('WARNING: Converseen license file not found in source checkout.')
    for license_path in licenses:
        copy_file(license_path, license_dir / license_path.name)
    (stage / 'TEST_PORTABLE.cmd').write_text(
        '@echo off\r\n'
        'setlocal\r\n'
        'cd /d "%~dp0"\r\n'
        'set "PATH=%SystemRoot%\\System32;%SystemRoot%"\r\n'
        'echo Testing packaged Image Studio using a clean Windows PATH...\r\n'
        '"%~dp0PixelShroomImageStudio.exe" --supported-formats > "%TEMP%\\pixelshroom-formats.txt" 2> "%TEMP%\\pixelshroom-errors.txt"\r\n'
        'echo Exit code: %ERRORLEVEL%\r\n'
        'findstr /I "JPEG PNG WEBP" "%TEMP%\\pixelshroom-formats.txt"\r\n'
        'echo Error log: %TEMP%\\pixelshroom-errors.txt\r\n'
        'echo Then double-click PixelShroomImageStudio.exe and test actual conversions.\r\n'
        'pause\r\n', encoding='utf-8')
    (stage / 'PHASE8_PACKAGING_REPORT.txt').write_text(
        f"ImageMagick package: {data['imagemagick_version_dir']}\n"
        f"Included coder modules: {', '.join(data['coders'])}\n"
        f"Configuration XML: {', '.join(data['configs'])}\n"
        f"Runtime DLL copies: {len(data['copied_runtime_dlls'])}\n"
        f"Total inspected EXE/DLL files: {data['scanned_binaries']}\n"
        "The ZIP has not been validated on a clean Windows machine.\n",
        encoding='utf-8')


def archive_tree(root: Path, target_zip: Path) -> None:
    with zipfile.ZipFile(target_zip, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as z:
        for file in sorted(p for p in root.rglob('*') if p.is_file()):
            z.write(file, arcname=Path(root.name) / file.relative_to(root))


def main() -> None:
    ap = argparse.ArgumentParser(description='Package the Phase 8 portable build, on Windows only')
    ap.add_argument('--project', type=Path, default=Path.cwd())
    ap.add_argument('--ucrt', type=Path, default=Path(r'C:\msys64\ucrt64'))
    ap.add_argument('--replace', action='store_true', help='Replace an existing Phase 8 dist folder')
    args = ap.parse_args()
    if os.name != 'nt':
        ap.error('Run this script on your Windows computer, not inside Linux or WSL.')
    project = args.project.resolve()
    ucrt = args.ucrt.resolve()
    build = project / 'build-portable/converseen.exe'
    if not build.is_file():
        ap.error(f'Portable CMake executable not built yet: {build}')
    if not (project / 'src/main.cpp').is_file() or not (project / 'CMakeLists.txt').is_file():
        ap.error(f'Not a Converseen source project: {project}')
    if 'PIXEL SHROOM PHASE 8 PORTABLE BOOTSTRAP' not in (project / 'src/main.cpp').read_text(encoding='utf-8'):
        ap.error('Run the Phase 8 prepare script before building the portable target.')
    windeploy = ucrt / 'bin/windeployqt6.exe'
    if not windeploy.is_file():
        windeploy = ucrt / 'bin/windeployqt.exe'
    objdump = ucrt / 'bin/objdump.exe'
    if not objdump.is_file():
        objdump = ucrt.parent / 'usr/bin/objdump.exe'
    for binary in (windeploy, objdump):
        if not binary.is_file():
            ap.error(f'Missing required MSYS2 tool: {binary}')
    dist = project / 'dist'
    dist.mkdir(parents=True, exist_ok=True)
    final = dist / 'PixelShroomImageStudio-Portable'
    final_zip = dist / 'PixelShroomImageStudio-Portable-Win64.zip'
    if (final.exists() or final_zip.exists()) and not args.replace:
        ap.error(f'Distribution already exists. To intentionally replace it, use --replace: {dist}')
    with tempfile.TemporaryDirectory(prefix='phase8-', dir=dist) as tmp:
        stage = Path(tmp) / final.name
        stage.mkdir(parents=True)
        copy_file(build, stage / 'PixelShroomImageStudio.exe')
        env = os.environ.copy()
        env['PATH'] = str(ucrt / 'bin') + os.pathsep + env.get('PATH', '')
        # windeployqt captures Qt plugins and Qt's deployment-time patching.
        run([str(windeploy), '--release', '--dir', str(stage),
             str(stage / 'PixelShroomImageStudio.exe')], env=env)
        qt_plugins(ucrt, stage)
        data = copy_imagemagick(ucrt, stage)
        data.update(collect_dlls(stage, ucrt, objdump))
        verify_staging(stage, data)
        write_support_files(stage, project, Path(__file__).resolve().parent, data)
        staged_zip = Path(tmp) / final_zip.name
        archive_tree(stage, staged_zip)
        if args.replace:
            if final.exists():
                shutil.rmtree(final)
            if final_zip.exists():
                final_zip.unlink()
        shutil.copytree(stage, final)
        shutil.copy2(staged_zip, final_zip)
    print('\nPHASE 8 PACKAGING COMPLETE (not yet runtime-tested on another PC)')
    print('Portable folder:', final)
    print('ZIP:', final_zip)
    print('Double-click:', final / 'PixelShroomImageStudio.exe')
    print('First run TEST_PORTABLE.cmd, then test JPEG/PNG/WebP and 300-DPI export.')

if __name__ == '__main__':
    main()
