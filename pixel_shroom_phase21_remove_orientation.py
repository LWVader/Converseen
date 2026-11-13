#!/usr/bin/env python3
"""Phase 21: remove the non-working Orientation/Rotate/Flip dialog and button.

Run from the Pixel Shroom Converseen project root:
  py -3 pixel_shroom_phase21_remove_orientation.py
  py -3 pixel_shroom_phase21_remove_orientation.py --apply

Requires Phase 19+ source, including the Phase 20 single-window layout.
Only src/mainwindowimpl.cpp is changed. Dry run is the default.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import difflib
from pathlib import Path
import shutil
import sys

MARK = '// Pixel Shroom Phase 21: remove broken orientation UI.'
PHASE20_MARK = '// Pixel Shroom Phase 20: single-window Image Studio above Preview.'

ORIGINAL_ORIENTATION = '    // The original native Resize/DPI widgets stay alive (hidden) for the\n    // working conversion engine. Only the native Rotate / Flip UI is moved.\n    const int nativeDimensionsTab = tabWidget->indexOf(tab);\n    const int rotateFlipTab = tabWidget->indexOf(tab_2);\n    if (nativeDimensionsTab < 0 || rotateFlipTab < 0) {\n        qWarning("Pixel Shroom: could not move native orientation controls");\n    } else {\n        tabWidget->setTabVisible(nativeDimensionsTab, false);\n        tabWidget->removeTab(rotateFlipTab); // does not delete the widget\n        tabWidget->hide();                  // collapse empty Actions Panel tab strip\n\n        auto *orientationDialog = new QDialog(this);\n        orientationDialog->setObjectName("psOrientationDialog");\n        orientationDialog->setWindowTitle(tr("Orientation - Rotate / Flip"));\n        orientationDialog->setMinimumSize(440, 340);\n        auto *orientationLayout = new QVBoxLayout(orientationDialog);\n        orientationLayout->setContentsMargins(14, 14, 14, 14);\n        orientationLayout->setSpacing(10);\n        orientationLayout->addWidget(tab_2, 1); // reuse existing wired controls\n        auto *orientationClose = new QPushButton(tr("Back to Resize"), orientationDialog);\n        orientationLayout->addWidget(orientationClose, 0, Qt::AlignRight);\n        QObject::connect(orientationClose, &QPushButton::clicked,\n                         orientationDialog, &QDialog::hide);\n        auto *orientationOpen = new QPushButton(tr("Orientation...  Rotate / Flip"), resizeTab);\n        orientationOpen->setObjectName("psOrientationOpen");\n        sizeGrid->addWidget(orientationOpen, 6, 0, 1, 4);\n        QObject::connect(orientationOpen, &QPushButton::clicked,\n                         orientationDialog, [orientationDialog]() {\n            orientationDialog->show();\n            orientationDialog->raise();\n            orientationDialog->activateWindow();\n        });\n    }'

REPLACEMENT = '    // Pixel Shroom Phase 21: remove broken orientation UI.\n    // Keep the native Dimensions page and Rotate/Flip widgets alive, but\n    // hidden: other parts of the converter may still access their fields.\n    const int nativeDimensionsTab = tabWidget->indexOf(tab);\n    const int rotateFlipTab = tabWidget->indexOf(tab_2);\n    if (nativeDimensionsTab >= 0)\n        tabWidget->setTabVisible(nativeDimensionsTab, false);\n    if (rotateFlipTab >= 0)\n        tabWidget->setTabVisible(rotateFlipTab, false);\n    tabWidget->hide();\n\n    // Set the hidden native orientation options to neutral, even if the\n    // previous session saved a different selection. There is no visible\n    // orientation workflow in Pixel Shroom Image Studio anymore.\n    radioRotNo->setChecked(true);\n    radioFlipNo->setChecked(true);'


def transform(source: str) -> str:
    if MARK in source:
        raise ValueError('Phase 21 already applied; no source changes needed.')
    if PHASE20_MARK not in source:
        raise ValueError('Phase 20 single-window source not found; refusing to edit a different layout.')
    if source.count(ORIGINAL_ORIENTATION) != 1:
        raise ValueError('Expected exactly one Phase 19 Orientation implementation; got '
                         + str(source.count(ORIGINAL_ORIENTATION))
                         + '. No changes made. Use the actual current source for a targeted fix.')
    result = source.replace(ORIGINAL_ORIENTATION, REPLACEMENT, 1)
    # Confirm no implementation of the removed dialog or its launcher remains.
    for old in ('psOrientationDialog', 'psOrientationOpen', 'Back to Resize',
                'orientationDialog->show()'):
        if old in result:
            raise ValueError(f'Unexpected additional orientation UI remains: {old}. No changes made.')
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd(), help='Converseen project root')
    p.add_argument('--apply', action='store_true', help='Apply the source-only patch')
    p.add_argument('--show-diff', action='store_true', help='Show proposed change without applying')
    args = p.parse_args()
    root = args.project.expanduser().resolve()
    path = root / 'src' / 'mainwindowimpl.cpp'
    try:
        if not (root / 'CMakeLists.txt').is_file() or not path.is_file():
            raise ValueError('Not a Converseen project root: CMakeLists.txt and src/mainwindowimpl.cpp required.')
        before = path.read_text(encoding='utf-8-sig')
        after = transform(before)
        if args.show_diff:
            print('\n'.join(difflib.unified_diff(
                before.splitlines(), after.splitlines(),
                fromfile='before/mainwindowimpl.cpp',
                tofile='after/mainwindowimpl.cpp', lineterm='')))
        print('PHASE 21 SOURCE CHECK PASSED')
        print('  Removes: Orientation / Rotate / Flip launch button and empty dialog')
        print('  Preserves: Resize, Preview, image queue, Website exports, DPI engine')
        print('  Keeps hidden native orientation widgets neutral (No rotation / No flip)')
        if not args.apply:
            print('DRY RUN PASSED. No files changed. Apply with --apply.')
            return 0
        backups = root / 'phase21-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup_file = backups / 'src' / 'mainwindowimpl.cpp'
        backup_file.parent.mkdir(parents=True, exist_ok=False)
        shutil.copy2(path, backup_file)
        temp = path.with_name(path.name + '.phase21.tmp')
        try:
            temp.write_text(after, encoding='utf-8')
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)
        print('APPLIED. SOURCE BACKUP:', backup_file)
        print('Build in MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
