#!/usr/bin/env python3
"""Phase 18: unified accent coloring + full Settings window with live preview.

Run from Converseen root. By default, checks compatibility without modifying files.
--apply backs up and modifies only two sources, adding one header. Does not touch
conversion, 300-DPI metadata, upload optimization, installer, or working builds.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARK = '// Pixel Shroom Phase 18: independent settings window with live theme preview.'
HEADER_NAME = 'pixelshroom_phase18_theme.h'


def replace_one(text: str, before: str, after: str, label: str) -> str:
    n = text.count(before)
    if n != 1:
        raise ValueError(f'{label}: expected one source anchor; found {n}. Nothing changed.')
    return text.replace(before, after, 1)


SETTINGS_WINDOW = r'''    // Pixel Shroom Phase 18: independent settings window with live theme preview.
    // The original settings widgets/signals are reused, not duplicated.
    auto *settingsDialog = new QDialog(this);
    settingsDialog->setObjectName("psAppearanceDialog");
    settingsDialog->setWindowTitle(tr("Appearance · Pixel Shroom Image Studio"));
    settingsDialog->setAttribute(Qt::WA_DeleteOnClose, false);
    settingsDialog->setMinimumSize(740, 510);
    settingsDialog->resize(1060, 700);
    settingsDialog->setSizeGripEnabled(true);

    auto *settingsWindowLayout = new QVBoxLayout(settingsDialog);
    settingsWindowLayout->setContentsMargins(20, 18, 20, 18);
    settingsWindowLayout->setSpacing(13);
    auto *settingsHeader = new QHBoxLayout();
    auto *settingsHeadingBlock = new QVBoxLayout();
    settingsHeadingBlock->setSpacing(3);
    auto *settingsHeading = new QLabel(tr("Appearance & personalization"), settingsDialog);
    settingsHeading->setObjectName("psAppearanceDialogTitle");
    settingsHeadingBlock->addWidget(settingsHeading);
    auto *settingsDescription = new QLabel(tr("Customize the entire workspace. Changes appear immediately."), settingsDialog);
    settingsDescription->setObjectName("psAppearanceDialogHint");
    settingsHeadingBlock->addWidget(settingsDescription);
    settingsHeader->addLayout(settingsHeadingBlock, 1);
    auto *returnTop = new QPushButton(tr("Back to editor"), settingsDialog);
    returnTop->setObjectName("psSettingsBackTop");
    settingsHeader->addWidget(returnTop);
    settingsWindowLayout->addLayout(settingsHeader);

    auto *settingsPages = new QSplitter(Qt::Horizontal, settingsDialog);
    settingsPages->setObjectName("psAppearancePages");
    settingsPages->setChildrenCollapsible(false);
    settingsPages->setHandleWidth(10);
    // Re-parent the existing Settings page, including all controls and saved
    // preferences, rather than introducing a second competing set of widgets.
    settingsPages->addWidget(settingsTab);
    settingsTab->setMinimumWidth(345);
    settingsPages->setStretchFactor(0, 3);

    auto *themePreview = new QFrame(settingsPages);
    themePreview->setObjectName("psThemePreviewCard");
    themePreview->setAttribute(Qt::WA_StyledBackground, true);
    auto *previewLayout = new QVBoxLayout(themePreview);
    previewLayout->setContentsMargins(18, 19, 18, 19);
    previewLayout->setSpacing(12);
    auto *previewTitle = new QLabel(tr("Live workspace preview"), themePreview);
    previewTitle->setObjectName("psAppearanceTitle");
    previewLayout->addWidget(previewTitle);
    auto *previewExplanation = new QLabel(tr("Colors update as you make changes. This preview never modifies an image."), themePreview);
    previewExplanation->setWordWrap(true);
    previewExplanation->setObjectName("psThemePreviewCaption");
    previewLayout->addWidget(previewExplanation);

    auto *sampleHeader = new QFrame(themePreview);
    sampleHeader->setObjectName("psThemePreviewHeader");
    auto *sampleHeaderLayout = new QHBoxLayout(sampleHeader);
    sampleHeaderLayout->setContentsMargins(12, 8, 12, 8);
    sampleHeaderLayout->addWidget(new QLabel(tr("Image Studio"), sampleHeader), 1);
    sampleHeaderLayout->addWidget(new QLabel(tr("Resize   ·   Compress   ·   Enhance"), sampleHeader));
    previewLayout->addWidget(sampleHeader);

    auto *sampleCanvas = new QFrame(themePreview);
    sampleCanvas->setObjectName("psThemePreviewCanvas");
    sampleCanvas->setMinimumHeight(150);
    auto *sampleCanvasLayout = new QVBoxLayout(sampleCanvas);
    auto *sampleCanvasText = new QLabel(tr("Image canvas color"), sampleCanvas);
    sampleCanvasText->setAlignment(Qt::AlignCenter);
    sampleCanvasText->setObjectName("psThemePreviewCaption");
    sampleCanvasLayout->addWidget(sampleCanvasText);
    previewLayout->addWidget(sampleCanvas, 1);
    auto *sampleButtons = new QHBoxLayout();
    auto *samplePrimary = new QLabel(tr("  Optimize images  "), themePreview);
    samplePrimary->setObjectName("psThemePreviewPrimary");
    samplePrimary->setAlignment(Qt::AlignCenter);
    auto *sampleSecondary = new QLabel(tr("  Compare output  "), themePreview);
    sampleSecondary->setObjectName("psThemePreviewSecondary");
    sampleSecondary->setAlignment(Qt::AlignCenter);
    sampleButtons->addWidget(samplePrimary);
    sampleButtons->addWidget(sampleSecondary);
    previewLayout->addLayout(sampleButtons);
    auto *sampleProgress = new QProgressBar(themePreview);
    sampleProgress->setTextVisible(false);
    sampleProgress->setRange(0, 100);
    sampleProgress->setValue(68);
    sampleProgress->setFixedHeight(12);
    previewLayout->addWidget(sampleProgress);
    auto *sampleFooter = new QLabel(tr("Window materials and accent colors are cosmetic. Exported artwork stays unchanged."), themePreview);
    sampleFooter->setObjectName("psThemePreviewCaption");
    sampleFooter->setWordWrap(true);
    previewLayout->addWidget(sampleFooter);

    settingsPages->addWidget(themePreview);
    settingsPages->setStretchFactor(1, 2);
    settingsPages->setSizes({590, 390});
    settingsWindowLayout->addWidget(settingsPages, 1);
    auto *settingsFooter = new QHBoxLayout();
    settingsFooter->addStretch(1);
    auto *returnBottom = new QPushButton(tr("Back to editor"), settingsDialog);
    returnBottom->setObjectName("psSettingsBackBottom");
    settingsFooter->addWidget(returnBottom);
    settingsWindowLayout->addLayout(settingsFooter);
    QObject::connect(returnTop, &QPushButton::clicked, settingsDialog, &QDialog::close);
    QObject::connect(returnBottom, &QPushButton::clicked, settingsDialog, &QDialog::close);
    auto openSettingsWindow = [settingsDialog]() {
        settingsDialog->show();
        settingsDialog->raise();
        settingsDialog->activateWindow();
    };
    // The image editor has no Settings tab anymore. It remains available
    // from Edit > Appearance settings and the editor's header button.
    auto *appearanceOpenButton = new QPushButton(tr("Appearance..."), panel);
    appearanceOpenButton->setObjectName("psAppearanceOpenButton");
    heading->addWidget(appearanceOpenButton);
    QObject::connect(appearanceOpenButton, &QPushButton::clicked,
                     settingsDialog, openSettingsWindow);'''

OLD_MENU_CONNECT = '''    connect(settingsMenuAction, &QAction::triggered, this,
            [tabs, settingsTab, collapse]() {
        if (!tabs->isVisible()) collapse->setChecked(true);
        tabs->setCurrentWidget(settingsTab);
    });'''
NEW_MENU_CONNECT = '''    connect(settingsMenuAction, &QAction::triggered,
            settingsDialog, openSettingsWindow);'''


def transform_main(text: str) -> str:
    if MARK in text:
        raise ValueError('Phase 18 was already applied. Refusing to apply twice.')
    required = [
        'Pixel Shroom Phase 17: stable compositing and separate image queue.',
        'auto *settingsTab = new QWidget(tabs);',
        '    auto *settingsScroll = new QScrollArea(settingsTab);',
        '    auto *personalCard = new QFrame(settingsContent);',
        '    auto *settingsMenuAction = new QAction(',
        '    auto *tabs = new QTabWidget(panel);',
        '    heading->addWidget(',
    ]
    for r in required:
        if r not in text:
            raise ValueError('Current source is not the expected Phase 17 layout: missing ' + r)
    text = replace_one(text, '#include <QSplitter>',
        '#include <QSplitter>\n#include <QDialog>\n#include <QProgressBar>', 'required Qt headers')
    text = replace_one(text, '    tabs->addTab(settingsTab, tr("Settings"));',
                       SETTINGS_WINDOW, 'move Settings to dedicated window')
    text = replace_one(text, OLD_MENU_CONNECT, NEW_MENU_CONNECT,
                       'Edit menu Settings navigation')
    return text


def transform_native(text: str) -> str:
    if '#include "pixelshroom_phase18_theme.h"' in text:
        raise ValueError('Phase 18 native theme is already connected.')
    if 'PixelShroomPhase17Theme::app(dark_) +' not in text:
        raise ValueError('Phase 17 app theme hook not found.')
    text = replace_one(text,
                       '#include "pixelshroom_phase17_theme.h"',
                       '#include "pixelshroom_phase17_theme.h"\n#include "pixelshroom_phase18_theme.h"',
                       'include new theme header')
    text = replace_one(text,
                       '                            PixelShroomPhase17Theme::app(dark_) +',
                       '                            PixelShroomPhase17Theme::app(dark_) +\n'
                       '                            PixelShroomPhase18Theme::app(dark_) +',
                       'global accent/theme coverage')
    text = replace_one(text,
                       '                              PixelShroomPhase17Theme::panel(dark_));',
                       '                              PixelShroomPhase17Theme::panel(dark_) +\n'
                       '                              PixelShroomPhase18Theme::panel(dark_));',
                       'panel/overlay accent coverage')
    return text


def run() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd())
    p.add_argument('--apply', action='store_true', help='Apply after successful dry run')
    args = p.parse_args()
    root = args.project.expanduser().resolve()
    header_kit = Path(__file__).with_name(HEADER_NAME)
    targets = {
        root / 'src/mainwindowimpl.cpp': transform_main,
        root / 'src/pixelshroom_native_glass.h': transform_native,
    }
    new_header = root / 'src' / HEADER_NAME
    try:
        if not (root / 'CMakeLists.txt').is_file():
            raise ValueError('Run this script from the Converseen project root.')
        if new_header.exists():
            raise ValueError('New theme header already exists; refusing to replace it.')
        if not header_kit.is_file():
            raise ValueError('Place the included .h file next to this patch script.')
        header_content = header_kit.read_text(encoding='utf-8')
        if 'namespace PixelShroomPhase18Theme' not in header_content:
            raise ValueError('Companion theme header failed validation.')
        updates = {}
        for target, fn in targets.items():
            if not target.is_file():
                raise ValueError(f'Missing source: {target}')
            updates[target] = fn(target.read_text(encoding='utf-8-sig'))
        print('PHASE 18 SOURCE COMPATIBILITY PASSED')
        for target in updates:
            print('  UPDATE:', target.relative_to(root))
        print('  ADD   :', new_header.relative_to(root))
        print('  PRESERVE: conversion, 300-DPI output, upload optimization, installed release')
        if not args.apply:
            print('DRY RUN PASSED — no files changed. Run with --apply to install.')
            return 0
        backup = root / 'phase18-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        for target in updates:
            destination = backup / target.relative_to(root)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, destination)
        written = []
        try:
            for target, content in updates.items():
                target.write_text(content, encoding='utf-8')
                written.append(target)
            new_header.write_text(header_content, encoding='utf-8')
        except Exception:
            for target in written:
                shutil.copy2(backup / target.relative_to(root), target)
            new_header.unlink(missing_ok=True)
            raise
        print('APPLIED. Source backup:', backup)
        print('Build using MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(run())
