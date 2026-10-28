#!/usr/bin/env python3
"""Prepare Converseen for a *separate* portable build. Dry run unless --apply.

GPL-3.0-or-later: modifications to the GPL Converseen source are covered by
Converseen's existing license terms. The developer retains the original license.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import re
import shutil

MARKER = 'PIXEL SHROOM PHASE 8 PORTABLE BOOTSTRAP'
HELPER = r'''
// PIXEL SHROOM PHASE 8 PORTABLE BOOTSTRAP
// Only compiled for the separate build-portable target; the normal build is unchanged.
#if defined(Q_OS_WIN) && defined(PIXELSHROOM_PORTABLE_BUILD)
static bool configurePixelShroomPortablePaths()
{
    wchar_t executablePath[32768] = {};
    const DWORD length = GetModuleFileNameW(nullptr, executablePath, 32768);
    if (length == 0 || length >= 32768)
        return false;

    const QDir applicationDir(QFileInfo(QString::fromWCharArray(executablePath,
                                        static_cast<int>(length))).absolutePath());
    const QString coderPath = applicationDir.filePath("modules/coders");
    const QString filterPath = applicationDir.filePath("modules/filters");
    const QString configPath = applicationDir.filePath("imagemagick/config");

    // Never accidentally use the developer's MSYS2 installation.
    if (!QDir(coderPath).exists() || !QDir(configPath).exists())
        return false;

    qputenv("MAGICK_HOME", QDir::toNativeSeparators(applicationDir.absolutePath()).toUtf8());
    qputenv("MAGICK_CONFIGURE_PATH", QDir::toNativeSeparators(configPath).toUtf8());
    qputenv("MAGICK_CODER_MODULE_PATH", QDir::toNativeSeparators(coderPath).toUtf8());
    if (QDir(filterPath).exists())
        qputenv("MAGICK_FILTER_MODULE_PATH", QDir::toNativeSeparators(filterPath).toUtf8());
    return true;
}
#endif
'''
STARTUP = r'''#if defined(Q_OS_WIN) && defined(PIXELSHROOM_PORTABLE_BUILD)
    restrictDllSearchPath();
    if (!configurePixelShroomPortablePaths()) {
        MessageBoxW(nullptr,
            L"Pixel Shroom Image Studio cannot find its bundled ImageMagick modules.\n"
            L"Please re-extract the complete portable ZIP; do not move the EXE alone.",
            L"Pixel Shroom Image Studio - Missing runtime files", MB_OK | MB_ICONERROR);
        return 2;
    }
#endif
    InitializeMagick(*argv);'''


def patch(content: str) -> str:
    if MARKER in content:
        raise ValueError('Phase 8 source marker already present; nothing to change.')
    if 'InitializeMagick(*argv);' not in content:
        raise ValueError('Could not find ImageMagick initialization in src/main.cpp.')
    if 'void restrictDllSearchPath()' not in content or '#include <windows.h>' not in content:
        raise ValueError('Windows DLL restriction helper differs from expected source.')
    if '#include <QFileInfo>' not in content:
        if '#include <QDir>' not in content:
            raise ValueError('Expected #include <QDir> is missing.')
        content = content.replace('#include <QDir>', '#include <QDir>\n#include <QFileInfo>', 1)
    if len(re.findall(r'\bint\s+main\s*\(', content)) != 1:
        raise ValueError('Could not find a unique main() entry point.')
    content = re.sub(r'(?=\bint\s+main\s*\()', HELPER + '\n', content, count=1)
    content = re.sub(r'^[ \t]*InitializeMagick\(\*argv\);',
                     lambda _: STARTUP, content, count=1, flags=re.MULTILINE)
    # If earlier patches left the Windows path overrides enabled, don't allow
    # later initialization to overwrite the portable module paths.
    start = content.index('InitializeMagick(*argv);')
    for line in content[start:].splitlines():
        if re.search(r'^\s*qputenv\("MAGICK_(?:HOME|CONFIGURE_PATH|CODER_MODULE_PATH)', line):
            # Mac OS configuration lines are preprocessor guarded; allow those,
            # but an active Windows coder-path override is unsafe in this build.
            if 'MAGICK_CODER_MODULE_PATH' in line or 'MAGICK_HOME' in line:
                raise ValueError('Active ImageMagick Windows override found after InitializeMagick.\n'
                                 'Leave it commented out as in the working Phase 7 build.')
    if 'QCoreApplication::setApplicationName("Converseen");' in content:
        content = content.replace('QCoreApplication::setApplicationName("Converseen");',
            '#if defined(PIXELSHROOM_PORTABLE_BUILD)\n'
            '    QCoreApplication::setApplicationName("Pixel Shroom Image Studio");\n'
            '#else\n'
            '    QCoreApplication::setApplicationName("Converseen");\n'
            '#endif', 1)
    assert content.count(MARKER) == 1
    return content


def main() -> None:
    ap = argparse.ArgumentParser(description='Prepare portable-only main.cpp entry points')
    ap.add_argument('--project', type=Path, default=Path.cwd())
    ap.add_argument('--apply', action='store_true', help='Back up and patch src/main.cpp')
    args = ap.parse_args()
    project = args.project.resolve()
    source = project / 'src/main.cpp'
    if not (project / 'CMakeLists.txt').is_file() or not source.is_file():
        ap.error(f'Invalid Converseen project directory: {project}')
    original = source.read_text(encoding='utf-8')
    try:
        new_text = patch(original)
    except ValueError as exc:
        ap.error(str(exc))
    if not args.apply:
        print('DRY RUN PASSED: src/main.cpp can be patched without changing the normal build.')
        print('Next: py -3 pixel_shroom_phase8_prepare.py --apply')
        return
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = project / 'phase8-backups' / f'main.cpp.before-phase8-{timestamp}.bak'
    backup.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, backup)
    try:
        source.write_text(new_text, encoding='utf-8')
    except Exception:
        shutil.copy2(backup, source)
        raise
    print(f'PHASE 8 READY: patched {source}')
    print(f'Backup: {backup}')
    print('The existing build/ folder and executable were not modified.')

if __name__ == '__main__':
    main()
