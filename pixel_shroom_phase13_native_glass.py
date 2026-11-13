#!/usr/bin/env python3
"""Phase 13: add genuine Windows DWM Acrylic/Mica to Phase 12 Qt Widgets UI.

Dry run by default. --apply makes dated backups and modifies only:
  src/mainwindowimpl.cpp
  src/pixelshroom_native_glass.h (added)
No CMake, build, installer, converter or ImageMagick edits.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARKER = "Pixel Shroom Phase 13: native Windows Acrylic/Mica backdrop."
PHASE12 = "Pixel Shroom Phase 12: opal / smoke liquid-glass interface."
OLD_INCLUDE = '#include "pixelshroom_liquid_glass_theme.h"'

OLD_CONNECTION = '''    connect(glassMode, &QToolButton::toggled, this,
            [panel, glassMode](bool dark) {
        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark));
        panel->setStyleSheet(PixelShroomLiquidGlass::panel(dark));
        glassMode->setText(dark ? QObject::tr("Light glass") : QObject::tr("Dark glass"));
        QSettings settings("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        settings.setValue("appearance/darkGlass", dark);
    });'''

PICKER = '''    // Pixel Shroom Phase 13: native Windows Acrylic/Mica backdrop.
    // Material and dark/light are separate preferences, not duplicate controls.
    auto *glassMaterialRow = new QHBoxLayout();
    glassMaterialRow->setContentsMargins(2, 0, 2, 0);
    glassMaterialRow->setSpacing(10);
    auto *glassMaterialLabel = new QLabel(tr("Window backdrop"), panel);
    auto *glassMaterial = new QComboBox(panel);
    glassMaterial->setObjectName("psNativeGlassMaterial");
    glassMaterial->addItem(tr("Desktop Acrylic · blur"), 2);
    glassMaterial->addItem(tr("Mica · subtle"), 1);
    glassMaterial->addItem(tr("Off · Qt appearance"), 0);
    glassMaterial->setToolTip(tr("Windows 11 (build 22621+) native system backdrop. "
        "Other systems automatically use the existing Qt glass appearance."));
    const int savedBackdrop = glassSettings.value("appearance/nativeGlass", 2).toInt();
    const int backdropIndex = glassMaterial->findData(savedBackdrop);
    glassMaterial->setCurrentIndex(backdropIndex >= 0 ? backdropIndex : 0);
    glassMaterialRow->addWidget(glassMaterialLabel);
    glassMaterialRow->addWidget(glassMaterial);
    glassMaterialRow->addStretch(1);
    auto *glassNativeStatus = new QLabel(panel);
    glassNativeStatus->setObjectName("psNativeGlassStatus");
    glassNativeStatus->setWordWrap(true);
    auto *nativeGlass = new PixelShroomNativeGlass::BackdropController(
        this, centralwidget, panel, glassNativeStatus);'''

NEW_CONNECTION = '''    connect(glassMode, &QToolButton::toggled, this,
            [glassMode, glassMaterial, nativeGlass](bool dark) {
        glassMode->setText(dark ? QObject::tr("Light glass") : QObject::tr("Dark glass"));
        QSettings settings("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        settings.setValue("appearance/darkGlass", dark);
        nativeGlass->setAppearance(dark, static_cast<PixelShroomNativeGlass::Material>(
            glassMaterial->currentData().toInt()));
    });
    connect(glassMaterial, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [glassMode, glassMaterial, nativeGlass](int) {
        const int material = glassMaterial->currentData().toInt();
        QSettings settings("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        settings.setValue("appearance/nativeGlass", material);
        nativeGlass->setAppearance(glassMode->isChecked(),
            static_cast<PixelShroomNativeGlass::Material>(material));
    });
    // Apply after Qt has created the top-level native HWND.
    QTimer::singleShot(0, this, [glassMode, glassMaterial, nativeGlass]() {
        nativeGlass->setAppearance(glassMode->isChecked(),
            static_cast<PixelShroomNativeGlass::Material>(
                glassMaterial->currentData().toInt()));
    });'''


def replace_exact_once(src: str, old: str, new: str, desc: str) -> str:
    count = src.count(old)
    if count != 1:
        raise ValueError(f"{desc}: expected exactly one anchor, found {count}; source not changed")
    return src.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        raise ValueError("Phase 13 already applied: refusing to patch twice")
    for required in (PHASE12,
                     'Pixel Shroom Phase 11: upload-ready exports and premium glass UI.',
                     'glassSettings.value("appearance/darkGlass", false)',
                     'auto *glassMode = new QToolButton(panel);',
                     '    root->addLayout(heading);'):
        if required not in source:
            raise ValueError(f"Expected Phase 12 source marker absent: {required}")
    source = replace_exact_once(source, OLD_INCLUDE,
                                OLD_INCLUDE + '\n#include "pixelshroom_native_glass.h"',
                                "native glass header")
    source = replace_exact_once(source,
                                '    heading->addWidget(glassMode);',
                                '    heading->addWidget(glassMode);\n' + PICKER,
                                "glass material selector")
    source = replace_exact_once(source, OLD_CONNECTION, NEW_CONNECTION,
                                "appearance-toggle connection")
    source = replace_exact_once(source,
                                '    root->addLayout(heading);',
                                '    root->addLayout(heading);\n'
                                '    root->addLayout(glassMaterialRow);\n'
                                '    root->addWidget(glassNativeStatus);',
                                "non-overlapping material control layout")
    return source


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', type=Path, default=Path.cwd())
    ap.add_argument('--apply', action='store_true', help='Apply after dry-run succeeds')
    args = ap.parse_args()
    root = args.project.expanduser().resolve()
    cpp = root / 'src' / 'mainwindowimpl.cpp'
    previous = root / 'src' / 'pixelshroom_liquid_glass_theme.h'
    new_header = root / 'src' / 'pixelshroom_native_glass.h'
    kit_header = Path(__file__).resolve().with_name('pixelshroom_native_glass.h')

    try:
        for required in (cpp, previous, kit_header, root / 'CMakeLists.txt'):
            if not required.is_file():
                raise ValueError(f'Missing required file: {required}')
        if new_header.exists():
            raise ValueError(f'{new_header} already exists. Preserve local changes and inspect manually.')
        original = cpp.read_text(encoding='utf-8-sig')
        updated = transform(original)
        header = kit_header.read_text(encoding='utf-8')
        if 'DwmSetWindowAttribute' not in header or 'BackdropController' not in header:
            raise ValueError('The native glass header is incomplete')
        print('PHASE 13 SOURCE CHECK PASSED')
        print('  CHANGE src/mainwindowimpl.cpp')
        print('  ADD    src/pixelshroom_native_glass.h')
        print('  KEEP   Phase 12 UI, Phase 11 compression, 300 DPI, converter and installer')
        if not args.apply:
            print('DRY RUN PASSED — no changes made. Re-run with --apply.'); return 0
        backup_dir = root / 'phase13-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy2(cpp, backup_dir / 'mainwindowimpl.cpp')
        try:
            new_header.write_text(header, encoding='utf-8')
            cpp.write_text(updated, encoding='utf-8')
        except Exception:
            shutil.copy2(backup_dir / 'mainwindowimpl.cpp', cpp)
            new_header.unlink(missing_ok=True)
            raise
        print('APPLIED — backup:', backup_dir)
        print('Next: MSYS2 UCRT64 → cmake --build build-portable --parallel 4')
        print('Test Windows Acrylic, Mica, Off and Light/Dark before repackaging.')
        return 0
    except (ValueError, OSError, UnicodeError) as err:
        print('ERROR:', err, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
