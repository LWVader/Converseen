#!/usr/bin/env python3
"""Phase 12 — Apple-inspired opal/smoke glass UI for Pixel Shroom Image Studio.

Dry-run by default. Requires Phase 11's existing upload workflow. Visual-only:
no change to converter, DPI, file-size optimizer, CMake or the installer.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARK = "Pixel Shroom Phase 12: opal / smoke liquid-glass interface."
OLD_THEME = '#include "pixelshroom_glass_theme.h"'
NEW_THEME = '#include "pixelshroom_liquid_glass_theme.h"'


def once(src: str, old: str, new: str, label: str) -> str:
    count = src.count(old)
    if count != 1:
        raise ValueError(f'{label}: expected one anchor, found {count}. No changes made.')
    return src.replace(old, new, 1)


def transform(source: str) -> str:
    if MARK in source:
        raise ValueError('Phase 12 already installed. Nothing changed.')
    for marker in (
        'Pixel Shroom Phase 11: upload-ready exports and premium glass UI.',
        'Pixel Shroom Phase 7: unified output settings',
        'PixelShroomUpload::start(this, sources, destination,',
        'uploadAction->setObjectName("psUploadAction");',
    ):
        if marker not in source:
            raise ValueError(f'Expected Phase 11 source marker not found: {marker!r}')
    source = once(source, OLD_THEME,
        NEW_THEME + '\n#include <QSettings>\n#include <QGraphicsDropShadowEffect>\n#include <QColor>',
        'theme include')
    source = once(source,
        '    qApp->setStyleSheet(PixelShroomGlass::window());',
        '''    // Pixel Shroom Phase 12: opal / smoke liquid-glass interface.
    // Appearance setting is saved independently of conversion settings.
    QSettings glassSettings("Pixel Shroom Studio", "Pixel Shroom Image Studio");
    const bool glassDark = glassSettings.value("appearance/darkGlass", false).toBool();
    qApp->setStyleSheet(PixelShroomLiquidGlass::window(glassDark));''',
        'global theme initialization')
    source = once(source,
        '    panel->setStyleSheet(PixelShroomGlass::panel());',
        '''    panel->setStyleSheet(PixelShroomLiquidGlass::panel(glassDark));
    // Soft glass elevation. Only the small control panel receives a shadow.
    auto *glassShadow = new QGraphicsDropShadowEffect(panel);
    glassShadow->setBlurRadius(23);
    glassShadow->setOffset(0, 6);
    glassShadow->setColor(QColor(22, 42, 72, 58));
    panel->setGraphicsEffect(glassShadow);''',
        'panel theme')
    source = once(source,
        '    heading->addWidget(title, 1);',
        '''    // Clear title hierarchy without adding duplicate processing controls.
    title->setText(tr("Image Studio"));
    title->setObjectName("psStudioTitle");
    auto *glassSubtitle = new QLabel(tr("PIXEL SHROOM  /  CREATE  ·  REFINE  ·  EXPORT"), panel);
    glassSubtitle->setObjectName("psStudioSubtitle");
    auto *brandStack = new QVBoxLayout();
    brandStack->setSpacing(1);
    brandStack->setContentsMargins(0, 0, 0, 0);
    brandStack->addWidget(title);
    brandStack->addWidget(glassSubtitle);
    heading->addLayout(brandStack, 1);
    // A single appearance switch, with persisted choice.
    auto *glassMode = new QToolButton(panel);
    glassMode->setObjectName("psGlassModeToggle");
    glassMode->setToolTip(tr("Switch between light and dark glass"));
    glassMode->setCheckable(true);
    glassMode->setChecked(glassDark);
    glassMode->setText(glassDark ? tr("Light glass") : tr("Dark glass"));
    heading->addWidget(glassMode);
    connect(glassMode, &QToolButton::toggled, this,
            [panel, glassMode](bool dark) {
        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark));
        panel->setStyleSheet(PixelShroomLiquidGlass::panel(dark));
        glassMode->setText(dark ? QObject::tr("Light glass") : QObject::tr("Dark glass"));
        QSettings settings("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        settings.setValue("appearance/darkGlass", dark);
    });''',
        'header title and appearance switch')
    for widget in ('root',):
        source = once(source,
            f'    {widget}->setContentsMargins(12, 10, 12, 9);',
            f'    {widget}->setContentsMargins(18, 16, 18, 16);',
            'main panel breathing room')
        source = once(source, f'    {widget}->setSpacing(7);',
                            f'    {widget}->setSpacing(12);', 'main panel spacing')
    for layout in ('sizeGrid', 'compressGrid', 'enhanceGrid'):
        source = once(source,
            f'    {layout}->setContentsMargins(8, 12, 8, 10);',
            f'    {layout}->setContentsMargins(16, 18, 16, 16);',
            f'{layout} content padding')
    source = once(source,
        '    uploadLayout->setContentsMargins(15, 15, 15, 12);',
        '    uploadLayout->setContentsMargins(16, 18, 16, 16);',
        'upload spacing')
    source = once(source,
        '    tabs->addTab(uploadTab, tr("Upload-ready"));',
        '    tabs->addTab(uploadTab, tr("Website"));',
        'short website tab label')
    source = once(source,
        '    auto *uploadTitle = new QLabel(tr("Website upload • automatic lossless optimization"), uploadTab);',
        '    auto *uploadTitle = new QLabel(tr("Website exports"), uploadTab);',
        'website tab heading')
    source = once(source,
        '    auto *uploadAction = new QPushButton(tr("Create upload-ready files for imported images"), uploadTab);',
        '    auto *uploadAction = new QPushButton(tr("Optimize for website"), uploadTab);',
        'primary action label')
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    root = args.project.resolve()
    cpp = root / 'src' / 'mainwindowimpl.cpp'
    existing = root / 'src' / 'pixelshroom_glass_theme.h'
    new_header = root / 'src' / 'pixelshroom_liquid_glass_theme.h'
    kit_header = Path(__file__).resolve().parent / 'pixelshroom_liquid_glass_theme.h'
    try:
        for required in (cpp, existing, kit_header):
            if not required.is_file():
                raise ValueError(f'Missing required file: {required}')
        if new_header.exists():
            raise ValueError(f'{new_header.name} already exists. Refusing to overwrite.')
        original = cpp.read_text(encoding='utf-8-sig')
        result = transform(original)
        contents = kit_header.read_text(encoding='utf-8')
        if 'namespace PixelShroomLiquidGlass {' not in contents or 'panel(bool dark' not in contents:
            raise ValueError('Theme header failed validation.')
        print('PHASE 12 SOURCE CHECK PASSED')
        print('  UPDATE src/mainwindowimpl.cpp')
        print('  ADD    src/pixelshroom_liquid_glass_theme.h')
        print('  KEEP   Phase 11 upload optimizer, converter, 300 DPI, portable build, installer')
        if not args.apply:
            print('DRY RUN PASSED — No changes made. Re-run with --apply.'); return 0
        backup = root / 'phase12-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(cpp, backup / 'mainwindowimpl.cpp')
        shutil.copy2(existing, backup / 'pixelshroom_glass_theme.h')
        try:
            new_header.write_text(contents, encoding='utf-8')
            cpp.write_text(result, encoding='utf-8')
        except Exception:
            shutil.copy2(backup / 'mainwindowimpl.cpp', cpp)
            new_header.unlink(missing_ok=True)
            raise
        print('APPLIED. Backup:', backup)
        print('MSYS2 UCRT64 build: cmake --build build-portable --parallel 4')
        print('Test BEFORE repackaging or changing the stable installed release.')
        return 0
    except (ValueError, OSError, UnicodeError) as error:
        print('ERROR:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
