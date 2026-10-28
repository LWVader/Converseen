#!/usr/bin/env python3
"""Pixel Shroom Converseen Phase 3: hide duplicate native Dimensions UI.

This patch requires the already-working Phase 2 Image Studio source.
Dry run: py -3 pixel_shroom_converseen_phase3.py
Apply:   py -3 pixel_shroom_converseen_phase3.py --apply

It changes only src/mainwindowimpl.cpp. It NEVER deletes the native widgets,
which the Phase 2 processing UI still drives through their signal connections.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

FILE = Path('src/mainwindowimpl.cpp')
PHASE2_MARKER = 'Phase 2: Squoosh-inspired, accessible tabs; no changes to the batch engine.'
PHASE3_MARKER = 'Pixel Shroom Phase 3: hide the native Dimensions tab, not its widgets.'
IMPORT_ANCHOR = '#include <QTabWidget>'
IMPORT_REPLACEMENT = '#include <QTabWidget>\n#include <QTabBar>'
TAB_ANCHOR = '    tabs->setDocumentMode(true);'
TAB_REPLACEMENT = '''    tabs->setDocumentMode(true);
    // Fill the full tab header width rather than leaving a white empty strip.
    tabs->tabBar()->setExpanding(true);'''
UI_ANCHOR = '''    // Avoid the compressed single-row toolbar seen in Phase 1.
    verticalLayout_20->insertWidget(0, panel);'''
UI_REPLACEMENT = '''    // Avoid the compressed single-row toolbar seen in Phase 1.
    verticalLayout_20->insertWidget(0, panel);

    // Pixel Shroom Phase 3: hide the native Dimensions tab, not its widgets.
    // Phase 2 deliberately updates groupDimensions, spin_geoWidth/Height,
    // checkRelative, and groupResolution behind the scenes. Removing or
    // disabling them could break the already-working conversion logic.
    // Keep the Rotate and Flip page available in the Actions Panel.
    const int nativeDimensionsTab = tabWidget->indexOf(tab);
    const int rotateFlipTab = tabWidget->indexOf(tab_2);
    if (nativeDimensionsTab >= 0 && rotateFlipTab >= 0) {
        tabWidget->setCurrentIndex(rotateFlipTab);
        tabWidget->setTabVisible(nativeDimensionsTab, false);
        tabWidget->setTabText(rotateFlipTab, tr("Rotate / Flip"));
    }'''


def replace_one(content: str, old: str, new: str, desc: str) -> str:
    count = content.count(old)
    if count != 1:
        raise ValueError(f'{desc}: expected 1 matching location, found {count}; nothing changed.')
    return content.replace(old, new, 1)


def make_patch(original: str) -> str:
    if PHASE2_MARKER not in original:
        raise ValueError('Phase 2 Image Studio panel not detected. This update targets the Phase 2 build only.')
    if PHASE3_MARKER in original:
        raise ValueError('Phase 3 is already applied; refusing to patch twice.')
    result = replace_one(original, IMPORT_ANCHOR, IMPORT_REPLACEMENT, 'Qt tab-bar include')
    result = replace_one(result, TAB_ANCHOR, TAB_REPLACEMENT, 'full-width Image Studio tabs')
    result = replace_one(result, UI_ANCHOR, UI_REPLACEMENT, 'native Dimensions tab hiding')
    assert result.count(PHASE3_MARKER) == 1
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Apply after a full compatibility check and backup')
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Path to cloned Converseen project')
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    target = root / FILE
    exe = root / 'build/converseen.exe'
    if not (root / 'CMakeLists.txt').is_file() or not target.is_file() or not exe.is_file():
        print('ERROR: run from the Converseen project containing CMakeLists.txt, src/mainwindowimpl.cpp, and build/converseen.exe.', file=sys.stderr)
        return 2
    try:
        original = target.read_text(encoding='utf-8-sig')
        revised = make_patch(original)
    except (OSError, UnicodeError, ValueError) as err:
        print(f'ERROR: {err}', file=sys.stderr)
        return 2

    print('Verified: Phase 2 Image Studio present; exact Phase 3 insertion points found.')
    print('Will modify: src/mainwindowimpl.cpp ONLY.')
    print('Will preserve: native resize/DPI widgets and their bindings, Rotate/Flip, existing converter, DLL setup.')
    if not args.apply:
        print('\nDRY RUN PASSED — no changes made. To apply:')
        print('  py -3 pixel_shroom_converseen_phase3.py --apply')
        return 0

    backup = root.parent / f'{root.name}-phase3-working-backup-{datetime.now():%Y%m%d-%H%M%S}'
    if backup.exists():
        print('ERROR: backup directory exists; retry after one second.', file=sys.stderr)
        return 3
    try:
        (backup / 'src').mkdir(parents=True)
        shutil.copy2(target, backup / FILE)
        shutil.copy2(exe, backup / 'converseen.exe')
        (backup / 'README.txt').write_text(
            'Phase 3 backup of working Converseen Phase 2 source and executable.\n'
            'To restore: close Converseen; copy src/mainwindowimpl.cpp from this backup\n'
            'to the corresponding project path; then recompile with\n'
            '    cmake --build build --parallel 4\n'
            'If compilation fails, restore converseen.exe from this folder to build/.\n'
            'No changes were made to main.cpp or your converter files.\n', encoding='utf-8')
        # Atomic replacement keeps the original on disk if writing fails.
        pending = target.with_name(target.name + '.pixelshroom-phase3-tmp')
        pending.write_text(revised, encoding='utf-8', newline='\n')
        pending.replace(target)
    except Exception as err:
        print(f'ERROR applying patch: {err}', file=sys.stderr)
        # Don't destroy the previously working main source on partial writes.
        saved = backup / FILE
        if saved.is_file():
            shutil.copy2(saved, target)
        return 3

    print('\nPHASE 3 SOURCE UPDATE APPLIED; previous executable remains in place until rebuild.')
    print(f'Backup: {backup}')
    print('\nIn MSYS2 UCRT64:')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    print('Test a copy of one image before processing full batches.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
