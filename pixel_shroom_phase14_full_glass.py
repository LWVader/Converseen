#!/usr/bin/env python3
"""Phase 14: app-wide Qt glass surfaces + Settings-tab appearance controls.

Dry run is default. --apply creates timestamped backups and modifies only:
  src/mainwindowimpl.cpp
  src/pixelshroom_native_glass.h
  src/pixelshroom_phase6.h
  src/pixelshroom_phase7.h
  src/pixelshroom_appwide_glass.h (new)
Requires installed Phase 13; never touches converter, DPI, optimizer or build tree.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import re
import shutil
import sys

MARK = 'Pixel Shroom Phase 14: application-wide glass and appearance Settings tab.'


def replace_one(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise ValueError(f'{label}: expected exactly one source anchor, found {n}')
    return text.replace(old, new, 1)


def replace_regex(text: str, pattern: str, replacement: str, count: int, label: str) -> str:
    out, n = re.subn(pattern, lambda _: replacement, text, flags=re.DOTALL)
    if n != count:
        raise ValueError(f'{label}: expected {count} matches, found {n}')
    return out


SETTINGS_TAB = '''    // Pixel Shroom Phase 14: application-wide glass and appearance Settings tab.
    // Keep visual preferences separate from image-processing settings.
    auto *settingsTab = new QWidget(tabs);
    settingsTab->setObjectName("psSettingsTab");
    auto *settingsLayout = new QVBoxLayout(settingsTab);
    settingsLayout->setContentsMargins(16, 15, 16, 14);
    settingsLayout->setSpacing(12);
    auto *appearanceCard = new QFrame(settingsTab);
    appearanceCard->setObjectName("psAppearanceCard");
    auto *appearanceCardLayout = new QVBoxLayout(appearanceCard);
    appearanceCardLayout->setContentsMargins(16, 16, 16, 16);
    appearanceCardLayout->setSpacing(12);
    auto *appearanceTitle = new QLabel(tr("Appearance"), appearanceCard);
    appearanceTitle->setObjectName("psAppearanceTitle");
    appearanceCardLayout->addWidget(appearanceTitle);
    auto *themeLine = new QHBoxLayout();
    themeLine->addWidget(new QLabel(tr("Color theme"), appearanceCard));
    themeLine->addStretch(1);
    themeLine->addWidget(glassMode);  // Reuse existing checked state and signals.
    appearanceCardLayout->addLayout(themeLine);
    appearanceCardLayout->addLayout(glassMaterialRow);  // Reuse native DWM selector.
    appearanceCardLayout->addWidget(glassNativeStatus);
    auto *appearanceHint = new QLabel(
        tr("These settings apply to the whole application, including the image canvas, "
           "menus, dialogs and buttons. Windows-native blur is the window backdrop; "
           "controls use coordinated translucent Qt materials."), appearanceCard);
    appearanceHint->setWordWrap(true);
    appearanceCardLayout->addWidget(appearanceHint);
    settingsLayout->addWidget(appearanceCard);
    settingsLayout->addStretch(1);
    tabs->addTab(settingsTab, tr("Settings"));
    // Settings is also accessible from the Edit menu, not only image controls.
    auto *settingsMenuAction = new QAction(tr("Appearance settings..."), this);
    menu_Edit->addAction(settingsMenuAction);
    connect(settingsMenuAction, &QAction::triggered, this,
            [tabs, settingsTab, collapse]() {
        if (!tabs->isVisible()) collapse->setChecked(true);
        tabs->setCurrentWidget(settingsTab);
    });'''


def transform_main(source: str) -> str:
    if MARK in source:
        raise ValueError('Phase 14 already applied to mainwindowimpl.cpp')
    if 'Pixel Shroom Phase 13: native Windows Acrylic/Mica backdrop.' not in source:
        raise ValueError('Phase 13 source marker not found; apply Phase 13 before Phase 14')
    source = replace_one(source, '    heading->addWidget(glassMode);\n',
                         '    // Appearance toggle now lives under Settings.\n',
                         'remove appearance toggle from image header')
    source = replace_one(source,
                         '    root->addLayout(glassMaterialRow);\n    root->addWidget(glassNativeStatus);',
                         '    // Native backdrop controls now belong to Settings, not the image page.',
                         'move native-backdrop controls')
    source = replace_one(source, '    tabs->addTab(uploadTab, tr("Website"));',
                         '    tabs->addTab(uploadTab, tr("Website"));\n' + SETTINGS_TAB,
                         'create Settings tab')
    return source


def transform_native(source: str) -> str:
    if 'PixelShroomAppGlass::widgets(dark_)' in source:
        raise ValueError('Phase 14 already applied to native backdrop header')
    source = replace_one(source,
                         '#include "pixelshroom_liquid_glass_theme.h"',
                         '#include "pixelshroom_liquid_glass_theme.h"\n#include "pixelshroom_appwide_glass.h"',
                         'include universal style')
    source = replace_one(source,
                         '''        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark_) +
                            (active ? nativeWindowOverrides() : QString()));''',
                         '''        // Preserve native DWM backdrop while styling the entire Qt app.
        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark_) +
                            PixelShroomAppGlass::widgets(dark_) +
                            (active ? nativeWindowOverrides() : QString()));''',
                         'app-wide style hook')
    source = replace_one(source,
                         '        panel_->setStyleSheet(PixelShroomLiquidGlass::panel(dark_));',
                         '        panel_->setStyleSheet(PixelShroomLiquidGlass::panel(dark_) +\n'
                         '                              PixelShroomAppGlass::settingsPanel(dark_));',
                         'Settings panel styling')
    return source


def transform_phase7(source: str) -> str:
    source = replace_regex(source,
        r'        setStyleSheet\(R"PS7\(.*?\)PS7"\);',
        '        setObjectName("psGlassLivePreview");  // Inherit global Phase 14 theme.',
        1, 'remove hard-coded modeless preview theme')
    source = replace_one(source,
        '            view->setStyleSheet("background:#11171e; border:1px solid #566b78;");',
        '            view->setObjectName("psGlassImageCanvas");',
        'modeless image canvas')
    return source


def transform_phase6(source: str) -> str:
    source = replace_regex(source,
        r'    dlg\.setStyleSheet\(R"PS6\(.*?\)PS6"\);',
        '    dlg.setObjectName("psGlassCompareDialog");  // Phase 14 global glass.',
        2, 'remove hard-coded comparison and legacy preview theme')
    # There are two dialogs: ensure the second has a distinct object name.
    pos = source.find('dlg.setObjectName("psGlassCompareDialog")')
    pos2 = source.find('dlg.setObjectName("psGlassCompareDialog")', pos+1)
    if pos < 0 or pos2 < 0:
        raise ValueError('Expected two legacy Phase 6 dialogs')
    source = source[:pos2] + source[pos2:].replace(
        'dlg.setObjectName("psGlassCompareDialog")',
        'dlg.setObjectName("psGlassLegacyPreviewDialog")', 1)
    source = replace_one(source,
        '        image->setStyleSheet("background:#10161c; border:1px solid #506070;");',
        '        image->setObjectName("psGlassImageCanvas");',
        'legacy preview image canvas')
    source = replace_one(source,
        '        view->setRenderHint(QPainter::SmoothPixmapTransform, true);',
        '        view->setObjectName("psGlassImageCanvas");\n'
        '        view->setRenderHint(QPainter::SmoothPixmapTransform, true);',
        'comparison image canvas')
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    files = {
        Path('src/mainwindowimpl.cpp'): transform_main,
        Path('src/pixelshroom_native_glass.h'): transform_native,
        Path('src/pixelshroom_phase6.h'): transform_phase6,
        Path('src/pixelshroom_phase7.h'): transform_phase7,
    }
    new_header = root / 'src/pixelshroom_appwide_glass.h'
    kit_header = Path(__file__).with_name('pixelshroom_appwide_glass.h')
    try:
        if new_header.exists():
            raise ValueError('App-wide glass header already exists; refusing to overwrite local work')
        if not kit_header.is_file():
            raise ValueError(f'Missing kit header: {kit_header}')
        updates = {}
        for rel, transform in files.items():
            path = root / rel
            if not path.is_file():
                raise ValueError(f'Missing required file: {rel}')
            before = path.read_text(encoding='utf-8-sig')
            updates[path] = transform(before)
        header = kit_header.read_text(encoding='utf-8')
        if 'namespace PixelShroomAppGlass' not in header or 'settingsPanel(bool dark)' not in header:
            raise ValueError('Theme header failed validation')
        print('PHASE 14 CHECK PASSED:')
        for path in updates:
            print('  UPDATE', path.relative_to(root))
        print('  ADD   ', new_header.relative_to(root))
        print('  KEEP   conversion engine, 300 DPI, upload limits, installer, main.cpp')
        if not args.apply:
            print('DRY RUN PASSED — nothing modified. Re-run with --apply.')
            return 0
        backup = root / 'phase14-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        for path in updates:
            target = backup / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        written = []
        try:
            for path, content in updates.items():
                path.write_text(content, encoding='utf-8')
                written.append(path)
            new_header.write_text(header, encoding='utf-8')
        except Exception:
            for path in written:
                shutil.copy2(backup / path.relative_to(root), path)
            new_header.unlink(missing_ok=True)
            raise
        print('APPLIED — source backup:', backup)
        print('Build in MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        print('Do not overwrite your stable release before a full visual + conversion test.')
        return 0
    except (OSError, ValueError, UnicodeError) as error:
        print('ERROR:', error, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
