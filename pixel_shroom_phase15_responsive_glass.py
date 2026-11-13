#!/usr/bin/env python3
"""Phase 15: fix windowed/fullscreen clipping, glass cards and workspace colors.

Compatible with the Phase 14 source patch. Default is dry run.
Updates only src/mainwindowimpl.cpp, src/pixelshroom_native_glass.h;
adds src/pixelshroom_phase15_theme.h. Leaves conversion, DPI, image IO, original
release and installer untouched. Requires rebuild in MSYS2 UCRT64.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARK = 'Pixel Shroom Phase 15: resizable workspace, scrollable settings, custom glass colors.'


def replace_one(s: str, old: str, new: str, label: str) -> str:
    occurrences = s.count(old)
    if occurrences != 1:
        raise ValueError(f'{label}: expected exactly one anchor, found {occurrences}')
    return s.replace(old, new, 1)

SETTINGS = r'''    // Pixel Shroom Phase 15: resizable workspace, scrollable settings, custom glass colors.
    // Settings scrolls independently; maximization must not clip these controls.
    auto *settingsTab = new QWidget(tabs);
    settingsTab->setObjectName("psSettingsTab");
    auto *settingsLayout = new QVBoxLayout(settingsTab);
    settingsLayout->setContentsMargins(2, 2, 2, 2);
    settingsLayout->setSpacing(0);
    auto *settingsScroll = new QScrollArea(settingsTab);
    settingsScroll->setObjectName("psSettingsScroll");
    settingsScroll->setWidgetResizable(true);
    settingsScroll->setFrameShape(QFrame::NoFrame);
    settingsScroll->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    settingsScroll->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    auto *settingsContent = new QWidget(settingsScroll);
    settingsContent->setObjectName("psSettingsContent");
    auto *contentLayout = new QVBoxLayout(settingsContent);
    contentLayout->setContentsMargins(12, 12, 12, 15);
    contentLayout->setSpacing(16);

    auto *appearanceCard = new QFrame(settingsContent);
    appearanceCard->setObjectName("psAppearanceCard");
    auto *appearanceCardLayout = new QVBoxLayout(appearanceCard);
    appearanceCardLayout->setContentsMargins(20, 17, 20, 19);
    appearanceCardLayout->setSpacing(13);
    auto *appearanceTitle = new QLabel(tr("Appearance"), appearanceCard);
    appearanceTitle->setObjectName("psAppearanceTitle");
    appearanceCardLayout->addWidget(appearanceTitle);
    auto *themeLine = new QHBoxLayout();
    themeLine->setSpacing(14);
    themeLine->addWidget(new QLabel(tr("Light / dark glass"), appearanceCard));
    themeLine->addStretch(1);
    themeLine->addWidget(glassMode);
    appearanceCardLayout->addLayout(themeLine);
    appearanceCardLayout->addLayout(glassMaterialRow);
    appearanceCardLayout->addWidget(glassNativeStatus);
    auto *appearanceHint = new QLabel(
        tr("Native Acrylic or Mica is behind the main window. The cards use "
           "translucent Qt materials and preserve readability."), appearanceCard);
    appearanceHint->setWordWrap(true);
    appearanceCardLayout->addWidget(appearanceHint);
    auto *appearanceShadow = new QGraphicsDropShadowEffect(appearanceCard);
    appearanceShadow->setBlurRadius(24);
    appearanceShadow->setOffset(0, 4);
    appearanceShadow->setColor(QColor(8, 25, 51, 38));
    appearanceCard->setGraphicsEffect(appearanceShadow);
    contentLayout->addWidget(appearanceCard);

    auto *personalCard = new QFrame(settingsContent);
    personalCard->setObjectName("psPersonalizationCard");
    auto *personalLayout = new QVBoxLayout(personalCard);
    personalLayout->setContentsMargins(20, 17, 20, 19);
    personalLayout->setSpacing(12);
    auto *personalTitle = new QLabel(tr("Workspace personalization"), personalCard);
    personalTitle->setObjectName("psPersonalizationTitle");
    personalLayout->addWidget(personalTitle);
    auto *personalHint = new QLabel(
        tr("Choose an accent for controls and a canvas-mat color. "
           "These changes never alter the images you export."), personalCard);
    personalHint->setWordWrap(true);
    personalLayout->addWidget(personalHint);
    auto *personalGrid = new QGridLayout();
    personalGrid->setHorizontalSpacing(12);
    personalGrid->setVerticalSpacing(12);
    auto *accentBox = new QComboBox(personalCard);
    accentBox->setObjectName("psAccentChoice");
    accentBox->addItem(tr("Ice blue"), QStringLiteral("#78b6f7"));
    accentBox->addItem(tr("Amethyst"), QStringLiteral("#b99bff"));
    accentBox->addItem(tr("Sea glass"), QStringLiteral("#66d5c3"));
    accentBox->addItem(tr("Coral"), QStringLiteral("#ff9c88"));
    accentBox->addItem(tr("Champagne"), QStringLiteral("#e9c889"));
    auto *accentCustom = new QPushButton(tr("Custom..."), personalCard);
    accentCustom->setObjectName("psCustomAccent");
    personalGrid->addWidget(new QLabel(tr("Accent color"), personalCard), 0, 0);
    personalGrid->addWidget(accentBox, 0, 1);
    personalGrid->addWidget(accentCustom, 0, 2);

    auto *canvasBox = new QComboBox(personalCard);
    canvasBox->setObjectName("psCanvasChoice");
    canvasBox->addItem(tr("Automatic glass"), QStringLiteral("auto"));
    canvasBox->addItem(tr("Midnight"), QStringLiteral("#142239"));
    canvasBox->addItem(tr("Slate"), QStringLiteral("#334b60"));
    canvasBox->addItem(tr("Warm charcoal"), QStringLiteral("#303036"));
    canvasBox->addItem(tr("Soft ivory"), QStringLiteral("#f0ede6"));
    auto *canvasCustom = new QPushButton(tr("Custom..."), personalCard);
    canvasCustom->setObjectName("psCustomCanvas");
    personalGrid->addWidget(new QLabel(tr("Image canvas mat"), personalCard), 1, 0);
    personalGrid->addWidget(canvasBox, 1, 1);
    personalGrid->addWidget(canvasCustom, 1, 2);
    personalGrid->setColumnStretch(1, 1);
    personalLayout->addLayout(personalGrid);

    QSettings appearanceSettings("Pixel Shroom Studio", "Pixel Shroom Image Studio");
    const QString savedAccent = appearanceSettings.value(
        "appearance/accentColor", "#78b6f7").toString();
    const QString savedCanvas = appearanceSettings.value(
        "appearance/canvasColor", "auto").toString();
    auto selectSaved = [](QComboBox *box, const QString &stored) {
        int index = box->findData(stored);
        if (index < 0 && QColor(stored).isValid()) {
            box->addItem(QObject::tr("Custom (%1)").arg(stored), stored);
            index = box->count() - 1;
        }
        box->setCurrentIndex(index >= 0 ? index : 0);
    };
    selectSaved(accentBox, savedAccent);
    selectSaved(canvasBox, savedCanvas);

    // One immediate refresh path: the backdrop controller recomposes both
    // the native backdrop and Qt widget colors without touching image state.
    auto refreshGlass = [glassMode, glassMaterial, nativeGlass]() {
        nativeGlass->setAppearance(glassMode->isChecked(),
            static_cast<PixelShroomNativeGlass::Material>(
                glassMaterial->currentData().toInt()));
    };
    connect(accentBox, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [accentBox, refreshGlass](int index) {
        if (index < 0) return;
        QSettings s("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        s.setValue("appearance/accentColor", accentBox->itemData(index).toString());
        refreshGlass();
    });
    connect(canvasBox, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [canvasBox, refreshGlass](int index) {
        if (index < 0) return;
        QSettings s("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        s.setValue("appearance/canvasColor", canvasBox->itemData(index).toString());
        refreshGlass();
    });
    auto applyCustom = [this, refreshGlass](QComboBox *box,
                                             const QString &key, const QString &title) {
        QColor current(box->currentData().toString());
        if (!current.isValid()) current = QColor(QStringLiteral("#78b6f7"));
        const QColor chosen = QColorDialog::getColor(current, this, title);
        if (!chosen.isValid()) return;
        const QString hex = chosen.name();
        int customIndex = -1;
        for (int i = 0; i < box->count(); ++i) {
            if (box->itemText(i).startsWith(QObject::tr("Custom ("))) {
                customIndex = i;
                break;
            }
        }
        if (customIndex < 0) {
            box->addItem(QObject::tr("Custom (%1)").arg(hex), hex);
            customIndex = box->count() - 1;
        } else {
            box->setItemText(customIndex, QObject::tr("Custom (%1)").arg(hex));
            box->setItemData(customIndex, hex);
        }
        box->setCurrentIndex(customIndex);
        QSettings s("Pixel Shroom Studio", "Pixel Shroom Image Studio");
        s.setValue(key, hex);
        refreshGlass();
    };
    connect(accentCustom, &QPushButton::clicked, this,
            [accentBox, applyCustom]() {
        applyCustom(accentBox, QStringLiteral("appearance/accentColor"),
                    QObject::tr("Choose accent color"));
    });
    connect(canvasCustom, &QPushButton::clicked, this,
            [canvasBox, applyCustom]() {
        applyCustom(canvasBox, QStringLiteral("appearance/canvasColor"),
                    QObject::tr("Choose canvas mat color"));
    });
    auto *personalShadow = new QGraphicsDropShadowEffect(personalCard);
    personalShadow->setBlurRadius(24);
    personalShadow->setOffset(0, 4);
    personalShadow->setColor(QColor(8, 25, 51, 38));
    personalCard->setGraphicsEffect(personalShadow);
    contentLayout->addWidget(personalCard);
    contentLayout->addStretch(1);
    settingsScroll->setWidget(settingsContent);
    settingsLayout->addWidget(settingsScroll);
    tabs->addTab(settingsTab, tr("Settings"));'''

LAYOUT = r'''    // Pixel Shroom Phase 15: the Studio and file list share a resizable area.
    // This prevents the file list from stealing height and crushing Settings.
    auto *workspaceSplitter = new QSplitter(Qt::Vertical, centralwidget);
    workspaceSplitter->setObjectName("psWorkspaceSplitter");
    workspaceSplitter->setChildrenCollapsible(false);
    workspaceSplitter->setHandleWidth(8);
    verticalLayout_20->removeWidget(treeWidget);
    verticalLayout_20->insertWidget(0, workspaceSplitter);
    workspaceSplitter->addWidget(panel);
    workspaceSplitter->addWidget(treeWidget);
    panel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    treeWidget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    treeWidget->setMinimumHeight(98);
    tabs->setMinimumHeight(215);
    workspaceSplitter->setStretchFactor(0, 3);
    workspaceSplitter->setStretchFactor(1, 1);
    verticalLayout_20->setStretch(0, 1);
    QTimer::singleShot(0, this, [workspaceSplitter]() {
        const int available = workspaceSplitter->height();
        if (available > 0)
            workspaceSplitter->setSizes({qMax(255, (available * 3) / 4),
                                         qMax(98, available / 4)});
    });'''


def transform_main(src: str) -> str:
    if MARK in src:
        raise ValueError('Phase 15 already installed in mainwindowimpl.cpp')
    if 'Pixel Shroom Phase 14: application-wide glass and appearance Settings tab.' not in src:
        raise ValueError('Phase 14 Settings source is required; do not apply to older version')
    src = replace_one(src, '#include "pixelshroom_native_glass.h"',
                      '#include "pixelshroom_native_glass.h"\n#include <QScrollArea>\n#include <QSplitter>',
                      'Qt includes')
    src = replace_one(src, '    auto *tabs = new QTabWidget(panel);\n    tabs->setDocumentMode(true);',
                      '    auto *tabs = new QTabWidget(panel);\n    tabs->setObjectName("psStudioTabs");\n    tabs->setDocumentMode(true);',
                      'tab object name')
    start = src.find('    auto *settingsTab = new QWidget(tabs);')
    stop_anchor = '    tabs->addTab(settingsTab, tr("Settings"));'
    end = src.find(stop_anchor, start)
    if start < 0 or end < 0 or src.count(stop_anchor) != 1:
        raise ValueError('Phase 14 settings block not found (expected one block)')
    end += len(stop_anchor)
    existing = src[start:end]
    for must in ('auto *appearanceCard', 'appearanceCardLayout->addLayout(glassMaterialRow)',
                 'settingsLayout->addWidget(appearanceCard)', 'settingsLayout->addStretch(1)'):
        if must not in existing:
            raise ValueError('Settings block differs from expected Phase 14: ' + must)
    src = src[:start] + SETTINGS + src[end:]
    src = replace_one(src,
                      '    verticalLayout_20->insertWidget(0, panel);',
                      LAYOUT,
                      'responsive workspace splitter')
    return src


def transform_controller(src: str) -> str:
    if '#include "pixelshroom_phase15_theme.h"' in src:
        raise ValueError('Phase 15 already installed in native-glass header')
    src = replace_one(src, '#include "pixelshroom_appwide_glass.h"',
                      '#include "pixelshroom_appwide_glass.h"\n#include "pixelshroom_phase15_theme.h"',
                      'new theme include')
    src = replace_one(src,
        '''        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark_) +
                            PixelShroomAppGlass::widgets(dark_) +
                            (active ? nativeWindowOverrides() : QString()));''',
        '''        qApp->setStyleSheet(PixelShroomLiquidGlass::window(dark_) +
                            PixelShroomAppGlass::widgets(dark_) +
                            PixelShroomPhase15Theme::app(dark_) +
                            (active ? nativeWindowOverrides() : QString()));''',
        'global glass styling')
    src = replace_one(src,
        '''        panel_->setStyleSheet(PixelShroomLiquidGlass::panel(dark_) +
                              PixelShroomAppGlass::settingsPanel(dark_));''',
        '''        panel_->setStyleSheet(PixelShroomLiquidGlass::panel(dark_) +
                              PixelShroomAppGlass::settingsPanel(dark_) +
                              PixelShroomPhase15Theme::panel(dark_));''',
        'local Studio panel styling')
    return src


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd())
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    root = args.project.expanduser().resolve()
    targets = {
        root / 'src/mainwindowimpl.cpp': transform_main,
        root / 'src/pixelshroom_native_glass.h': transform_controller,
    }
    new_header = root / 'src/pixelshroom_phase15_theme.h'
    kit_header = Path(__file__).with_name('pixelshroom_phase15_theme.h')
    try:
        if not (root / 'CMakeLists.txt').is_file():
            raise ValueError('Project root must contain CMakeLists.txt')
        if new_header.exists():
            raise ValueError('Phase 15 header already exists; refusing to overwrite')
        if not kit_header.is_file():
            raise ValueError('Kit missing pixelshroom_phase15_theme.h')
        new_contents = kit_header.read_text(encoding='utf-8')
        if 'namespace PixelShroomPhase15Theme' not in new_contents:
            raise ValueError('Missing Phase 15 header namespace')
        updates = {}
        for path, fn in targets.items():
            if not path.is_file():
                raise ValueError(f'Missing {path.relative_to(root)}')
            updates[path] = fn(path.read_text(encoding='utf-8-sig'))
        print('PHASE 15 CHECK PASSED')
        for path in updates: print('  UPDATE:', path.relative_to(root))
        print('  ADD:', new_header.relative_to(root))
        print('  KEEP: converter, DPI, upload optimizer, installer, existing dist')
        if not args.apply:
            print('DRY RUN PASSED — no changes. Use --apply to proceed.')
            return 0
        backup = root / 'phase15-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
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
            new_header.write_text(new_contents, encoding='utf-8')
        except Exception:
            for path in written:
                shutil.copy2(backup / path.relative_to(root), path)
            new_header.unlink(missing_ok=True)
            raise
        print('APPLIED — backups:', backup)
        print('Rebuild using MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        print('Test windowed, maximized, glass colors, DPI and website export before repackaging.')
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
