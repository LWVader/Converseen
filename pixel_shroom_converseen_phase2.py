#!/usr/bin/env python3
"""Pixel Shroom Converseen Phase 2: legible conversion status + Squoosh-inspired controls.

Run from existing, already Phase-1-patched Converseen repository:
  py -3 pixel_shroom_converseen_phase2.py          # dry run
  py -3 pixel_shroom_converseen_phase2.py --apply  # backup then apply

No source files are changed unless every compatibility check succeeds.
"""
from __future__ import annotations
import argparse
import datetime as dt
import pathlib
import shutil
import sys

PANEL_BEGIN = "void MainWindowImpl::setupPixelShroomControls()\n{"
PANEL_END = "MainWindowImpl::~MainWindowImpl()"
STATUS_ANCHOR = '    treeWidget->header()->setSectionResizeMode(1, QHeaderView::ResizeToContents);'
STATUS_REPLACEMENT = '''    // Pixel Shroom: readable, separate columns for long artwork filenames.
    setMinimumSize(640, 340);
    resize(760, 420);
    treeWidget->header()->setStretchLastSection(false);
    treeWidget->header()->setMinimumSectionSize(105);
    treeWidget->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    treeWidget->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    treeWidget->header()->resizeSection(1, 132);
    treeWidget->setTextElideMode(Qt::ElideMiddle);
    treeWidget->setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);'''
STATUS_TOOLTIP_ANCHOR = '    item->setText(1, m_msg);'
STATUS_TOOLTIP_REPLACEMENT = '''    item->setText(1, m_msg);
    item->setToolTip(0, fileName); // Hover to see a complete long name.
    item->setToolTip(1, m_msg);'''

IMPORT_ANCHOR = '#include <QSize>'
IMPORT_REPLACEMENT = '''#include <QSize>
#include <QTabWidget>
#include <QGridLayout>
#include <QSlider>
#include <QSignalBlocker>
#include <QFrame>
#include <QToolButton>
#include <QHeaderView>'''

PANEL_CODE = r'''void MainWindowImpl::setupPixelShroomControls()
{
    // Phase 2: Squoosh-inspired, accessible tabs; no changes to the batch engine.
    auto *panel = new QFrame(centralwidget);
    panel->setObjectName("psStudioPanel");
    panel->setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Maximum);
    panel->setStyleSheet(R"PSCSS(
        QFrame#psStudioPanel { background: #20252b; border: 1px solid #4a5662;
            border-radius: 8px; color: #f4f6f8; }
        QFrame#psStudioPanel QLabel, QFrame#psStudioPanel QCheckBox {
            color: #f4f6f8; border: none; background: transparent; }
        QFrame#psStudioPanel QTabWidget::pane { border: 0; background: #20252b; }
        QWidget#psResizeTab, QWidget#psCompressTab, QWidget#psEnhanceTab {
            background: #20252b; }
        QFrame#psStudioPanel QTabBar::tab { background: #303941; color: #e8eef4;
            min-width: 78px; padding: 9px 15px; border: 0; }
        QFrame#psStudioPanel QTabBar::tab:selected { background: #68b9e7; color: #121c28; }
        QFrame#psStudioPanel QComboBox, QFrame#psStudioPanel QSpinBox,
        QFrame#psStudioPanel QDoubleSpinBox { color: #f5f7f9; background: #323941;
            border: 1px solid #63717e; border-radius: 4px; min-height: 27px;
            padding: 2px 7px; }
        QFrame#psStudioPanel QPushButton, QFrame#psStudioPanel QToolButton {
            color: #f4f6f8; background: #364650; border: 1px solid #667a89;
            border-radius: 4px; padding: 5px 9px; }
        QFrame#psStudioPanel QSlider::groove:horizontal {
            height: 5px; background: #647783; border-radius: 2px; }
        QFrame#psStudioPanel QSlider::handle:horizontal { background: #68b9e7;
            border-radius: 8px; width: 16px; margin: -6px 0; }
    )PSCSS");
    auto *root = new QVBoxLayout(panel);
    root->setContentsMargins(12, 10, 12, 9);
    root->setSpacing(7);
    auto *heading = new QHBoxLayout();
    auto *title = new QLabel(tr("PIXEL SHROOM  |  IMAGE STUDIO"), panel);
    QFont titleFont = title->font();
    titleFont.setBold(true);
    title->setFont(titleFont);
    heading->addWidget(title, 1);
    auto *collapse = new QToolButton(panel);
    collapse->setText(tr("Hide controls"));
    collapse->setCheckable(true);
    collapse->setChecked(true);
    heading->addWidget(collapse);
    root->addLayout(heading);

    auto *tabs = new QTabWidget(panel);
    tabs->setDocumentMode(true);
    root->addWidget(tabs);
    connect(collapse, &QToolButton::toggled, this, [tabs, collapse](bool expanded) {
        tabs->setVisible(expanded);
        collapse->setText(expanded ? QObject::tr("Hide controls") : QObject::tr("Show controls"));
    });

    // Resize tab: exact pixel boxes, existing aspect-fit behavior, print DPI and filters.
    auto *resizeTab = new QWidget(tabs);
    resizeTab->setObjectName("psResizeTab");
    auto *sizeGrid = new QGridLayout(resizeTab);
    sizeGrid->setContentsMargins(8, 12, 8, 10);
    sizeGrid->setHorizontalSpacing(14);
    sizeGrid->setVerticalSpacing(10);
    auto *preset = new QComboBox(resizeTab);
    preset->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Fixed);
    preset->addItem(tr("Custom (use size below)"), QSize());
    preset->addItem(tr("16 x 16 in  |  4800 x 4800"), QSize(4800, 4800));
    preset->addItem(tr("16 x 20 in  |  4800 x 6000"), QSize(4800, 6000));
    preset->addItem(tr("24 x 24 in  |  7200 x 7200"), QSize(7200, 7200));
    preset->addItem(tr("24 x 30 in  |  7200 x 9000"), QSize(7200, 9000));
    preset->addItem(tr("Web  |  600 x 600"), QSize(600, 600));
    preset->addItem(tr("Web  |  2048 x 2048"), QSize(2048, 2048));
    sizeGrid->addWidget(new QLabel(tr("Preset"), resizeTab), 0, 0);
    sizeGrid->addWidget(preset, 0, 1, 1, 3);
    auto *width = new QSpinBox(resizeTab);
    auto *height = new QSpinBox(resizeTab);
    for (auto *spin : {width, height}) {
        spin->setRange(1, 100000);
        spin->setSingleStep(100);
        spin->setSuffix(tr(" px"));
        spin->setMinimumWidth(120);
    }
    width->setValue(comboResizeValues->currentText() == "px" && spin_geoWidth->value() > 1
                    ? qRound(spin_geoWidth->value()) : 2048);
    height->setValue(comboResizeValues->currentText() == "px" && spin_geoHeight->value() > 1
                     ? qRound(spin_geoHeight->value()) : 2048);
    sizeGrid->addWidget(new QLabel(tr("Width"), resizeTab), 1, 0);
    sizeGrid->addWidget(width, 1, 1);
    sizeGrid->addWidget(new QLabel(tr("Height"), resizeTab), 1, 2);
    sizeGrid->addWidget(height, 1, 3);
    auto *keepAspect = new QCheckBox(tr("Keep aspect ratio (fit inside, no crop)"), resizeTab);
    keepAspect->setChecked(checkRelative->isChecked());
    sizeGrid->addWidget(keepAspect, 2, 0, 1, 4);

    auto *filter = new QComboBox(resizeTab);
    filter->addItem(tr("Automatic"), static_cast<int>(UndefinedFilter));
    filter->addItem(tr("Lanczos - crisp detail"), static_cast<int>(LanczosFilter));
    filter->addItem(tr("Mitchell - smooth edges"), static_cast<int>(MitchellFilter));
    filter->addItem(tr("Catrom - sharp edges"), static_cast<int>(CatromFilter));
    filter->addItem(tr("Triangle - soft"), static_cast<int>(TriangleFilter));
    int currentFilter = filter->findData(static_cast<int>(m_resamplingFilter));
    filter->setCurrentIndex(currentFilter >= 0 ? currentFilter : 0);
    sizeGrid->addWidget(new QLabel(tr("Resize method"), resizeTab), 3, 0);
    sizeGrid->addWidget(filter, 3, 1, 1, 3);
    connect(filter, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [this, filter](int index) {
        if (index >= 0)
            m_resamplingFilter = static_cast<IMFilterType>(filter->itemData(index).toInt());
    });

    auto *printDpi = new QCheckBox(tr("Print resolution"), resizeTab);
    printDpi->setChecked(groupResolution->isChecked());
    auto *dpi = new QSpinBox(resizeTab);
    dpi->setRange(72, 1200);
    dpi->setValue(spin_resX->value() >= 72 ? qRound(spin_resX->value()) : 300);
    dpi->setSuffix(tr(" DPI"));
    dpi->setEnabled(printDpi->isChecked());
    sizeGrid->addWidget(printDpi, 4, 0);
    sizeGrid->addWidget(dpi, 4, 1);
    auto *note = new QLabel(tr("Print presets use 300 DPI. Aspect-fit prevents stretching; output may not fill a different-shaped canvas."), resizeTab);
    note->setWordWrap(true);
    sizeGrid->addWidget(note, 5, 0, 1, 4);
    sizeGrid->setColumnStretch(1, 1);
    sizeGrid->setColumnStretch(3, 1);
    tabs->addTab(resizeTab, tr("Resize"));

    auto applySize = [this, width, height, keepAspect]() {
        groupDimensions->setChecked(true);
        comboResizeValues->setCurrentText("px"); // Native control resets size when units change.
        checkRelative->setChecked(keepAspect->isChecked());
        spin_geoWidth->setValue(width->value());
        spin_geoHeight->setValue(height->value());
        showNewSizePreview();
    };
    connect(width, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [applySize](int) { applySize(); });
    connect(height, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [applySize](int) { applySize(); });
    connect(keepAspect, &QCheckBox::toggled, this,
            [applySize](bool) { applySize(); });
    connect(preset, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [this, preset, width, height, keepAspect, dpi, printDpi, applySize](int index) {
        if (index < 1)
            return;
        const QSize target = preset->itemData(index).toSize();
        if (!target.isValid())
            return;
        {
            const QSignalBlocker blockWidth(width);
            const QSignalBlocker blockHeight(height);
            width->setValue(target.width());
            height->setValue(target.height());
        }
        {
            const QSignalBlocker blockAspect(keepAspect);
            keepAspect->setChecked(true); // Presets fit the art without cropping/stretching.
        }
        const bool isPrint = index <= 4;
        if (isPrint)
            dpi->setValue(300);
        printDpi->setChecked(isPrint);
        applySize();
        statusBar()->showMessage(tr("Preset applied. Choose a matching aspect ratio for exact canvas dimensions."), 7000);
    });
    connect(printDpi, &QCheckBox::toggled, this, [this, dpi](bool enabled) {
        dpi->setEnabled(enabled);
        groupResolution->setChecked(enabled);
        if (enabled) {
            spin_resX->setValue(dpi->value());
            spin_resY->setValue(dpi->value());
        }
    });
    connect(dpi, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, printDpi](int value) {
        if (printDpi->isChecked()) {
            spin_resX->setValue(value);
            spin_resY->setValue(value);
        }
    });

    // Compress tab: Squoosh-style quality slider + exact value, opt-in.
    auto *compressTab = new QWidget(tabs);
    compressTab->setObjectName("psCompressTab");
    auto *compressGrid = new QGridLayout(compressTab);
    compressGrid->setContentsMargins(8, 12, 8, 10);
    compressGrid->setHorizontalSpacing(14);
    compressGrid->setVerticalSpacing(12);
    auto *overrideQuality = new QCheckBox(tr("Use custom quality for JPEG / WebP"), compressTab);
    auto *qualitySlider = new QSlider(Qt::Horizontal, compressTab);
    auto *qualityNumber = new QSpinBox(compressTab);
    qualitySlider->setRange(1, 100);
    qualitySlider->setValue(m_psQuality);
    qualityNumber->setRange(1, 100);
    qualityNumber->setValue(m_psQuality);
    qualityNumber->setMinimumWidth(75);
    qualitySlider->setEnabled(false);
    qualityNumber->setEnabled(false);
    compressGrid->addWidget(overrideQuality, 0, 0, 1, 3);
    compressGrid->addWidget(new QLabel(tr("Quality"), compressTab), 1, 0);
    compressGrid->addWidget(qualitySlider, 1, 1);
    compressGrid->addWidget(qualityNumber, 1, 2);
    auto *compressHint = new QLabel(tr("Higher quality = more detail and larger files. PNG stays lossless. WebP switches to lossy when this override is on."), compressTab);
    compressHint->setWordWrap(true);
    compressGrid->addWidget(compressHint, 2, 0, 1, 3);
    auto *advanced = new QPushButton(tr("Advanced compression / format settings..."), compressTab);
    compressGrid->addWidget(advanced, 3, 0, 1, 3);
    compressGrid->setColumnStretch(1, 1);
    connect(overrideQuality, &QCheckBox::toggled, this, [this, qualitySlider, qualityNumber](bool on) {
        m_psOverrideQuality = on;
        qualitySlider->setEnabled(on);
        qualityNumber->setEnabled(on);
    });
    connect(qualitySlider, &QSlider::valueChanged, qualityNumber, &QSpinBox::setValue);
    connect(qualityNumber, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, qualitySlider](int val) {
        qualitySlider->setValue(val);
        m_psQuality = val;
    });
    connect(advanced, &QPushButton::clicked, this, [this, filter]() {
        setQuality();
        const int idx = filter->findData(static_cast<int>(m_resamplingFilter));
        if (idx >= 0) {
            const QSignalBlocker b(filter);
            filter->setCurrentIndex(idx);
        }
    });
    tabs->addTab(compressTab, tr("Compress"));

    // Enhance tab: independent subtle blur / detail sharpening, both off by default.
    auto *enhanceTab = new QWidget(tabs);
    enhanceTab->setObjectName("psEnhanceTab");
    auto *enhanceGrid = new QGridLayout(enhanceTab);
    enhanceGrid->setContentsMargins(8, 12, 8, 10);
    enhanceGrid->setHorizontalSpacing(14);
    enhanceGrid->setVerticalSpacing(12);
    auto makeEnhancement = [this, enhanceTab, enhanceGrid](int row, const QString &label,
                                                            const QString &help, bool smoothing) {
        auto *caption = new QLabel(label, enhanceTab);
        auto *slider = new QSlider(Qt::Horizontal, enhanceTab);
        auto *number = new QDoubleSpinBox(enhanceTab);
        slider->setRange(0, 20);
        slider->setValue(0);
        slider->setSingleStep(1);
        number->setDecimals(1);
        number->setRange(0.0, 2.0);
        number->setSingleStep(0.1);
        number->setValue(0.0);
        number->setMinimumWidth(78);
        slider->setToolTip(help);
        number->setToolTip(help);
        enhanceGrid->addWidget(caption, row, 0);
        enhanceGrid->addWidget(slider, row, 1);
        enhanceGrid->addWidget(number, row, 2);
        connect(slider, &QSlider::valueChanged, this, [this, number, smoothing](int val) {
            const double sigma = val / 10.0;
            number->setValue(sigma);
            if (smoothing) m_psSmoothSigma = sigma;
            else m_psSharpenSigma = sigma;
        });
        connect(number, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
                [slider](double val) { slider->setValue(qRound(val * 10.0)); });
    };
    makeEnhancement(0, tr("Smoothing"), tr("Gaussian smoothing, 0 = off; try 0.2-0.4"), true);
    makeEnhancement(1, tr("Sharpen"), tr("Sharpen after resizing, 0 = off; try 0.3-0.7"), false);
    auto *enhanceHint = new QLabel(tr("Both are off at 0. Start gently: strong smoothing removes texture; strong sharpening adds halos."), enhanceTab);
    enhanceHint->setWordWrap(true);
    enhanceGrid->addWidget(enhanceHint, 2, 0, 1, 3);
    enhanceGrid->setColumnStretch(1, 1);
    tabs->addTab(enhanceTab, tr("Enhance"));

    // Honor native advanced editing (e.g., if user changes existing resize fields).
    connect(spin_geoWidth, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
            [this, width](double value) {
        if (comboResizeValues->currentText() != "px") return;
        const QSignalBlocker b(width);
        width->setValue(qMax(1, qRound(value)));
    });
    connect(spin_geoHeight, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
            [this, height](double value) {
        if (comboResizeValues->currentText() != "px") return;
        const QSignalBlocker b(height);
        height->setValue(qMax(1, qRound(value)));
    });
    connect(checkRelative, &QCheckBox::toggled, this, [keepAspect](bool on) {
        const QSignalBlocker b(keepAspect);
        keepAspect->setChecked(on);
    });

    // Avoid the compressed single-row toolbar seen in Phase 1.
    verticalLayout_20->insertWidget(0, panel);
}

'''


def only_once(s: str, old: str, new: str, name: str) -> str:
    n = s.count(old)
    if n != 1:
        raise ValueError(f"{name}: expected one anchor; found {n}. No files changed.")
    return s.replace(old, new, 1)


def patch_main(s: str) -> str:
    if 'Phase 2: Squoosh-inspired' in s:
        raise ValueError('Phase 2 was already applied to mainwindowimpl.cpp.')
    if 'm_psSmoothSigma' not in s or 'm_psOverrideQuality' not in s:
        raise ValueError('This repo does not appear to have the Phase 1 controls. Apply Phase 1 first.')
    start = s.find(PANEL_BEGIN)
    end = s.find(PANEL_END, start)
    if start < 0 or end < start:
        raise ValueError('The Phase 1 panel could not be located safely; no files changed.')
    if s.count(PANEL_BEGIN) != 1 or s.count(PANEL_END) != 1:
        raise ValueError('Unexpected duplicate panel boundary; no files changed.')
    s = s[:start] + PANEL_CODE + s[end:]
    s = only_once(s, IMPORT_ANCHOR, IMPORT_REPLACEMENT, 'Qt import section')
    return s


def patch_status(s: str) -> str:
    if 'Pixel Shroom: readable, separate columns' in s:
        raise ValueError('Status dialog was already patched with Phase 2.')
    s = only_once(s, STATUS_ANCHOR, STATUS_REPLACEMENT, 'status header')
    s = only_once(s, STATUS_TOOLTIP_ANCHOR, STATUS_TOOLTIP_REPLACEMENT, 'status tooltips')
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true', help='Back up the working build and apply Phase 2')
    ap.add_argument('--project', type=pathlib.Path, default=pathlib.Path.cwd())
    args = ap.parse_args()
    root = args.project.expanduser().resolve()
    main_src = root / 'src/mainwindowimpl.cpp'
    status_src = root / 'src/dialogconversionstatus.cpp'
    build = root / 'build'
    exe = build / 'converseen.exe'
    if not (root / 'CMakeLists.txt').is_file() or not exe.is_file():
        print('ERROR: Run in your Converseen project containing CMakeLists.txt and build/converseen.exe.', file=sys.stderr)
        return 2
    try:
        old_main = main_src.read_text(encoding='utf-8-sig')
        old_status = status_src.read_text(encoding='utf-8-sig')
        new_main = patch_main(old_main)
        new_status = patch_status(old_status)
    except (OSError, ValueError, UnicodeError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 2
    print('Validated: src/mainwindowimpl.cpp (new Squoosh-like tabbed controls)')
    print('Validated: src/dialogconversionstatus.cpp (non-overlapping status columns)')
    if not args.apply:
        print('\nDRY RUN PASSED; nothing was changed. Apply using:')
        print('  py -3 pixel_shroom_converseen_phase2.py --apply')
        return 0

    stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = root.parent / f'{root.name}-phase2-working-backup-{stamp}'
    if backup.exists():
        print('ERROR: backup path already exists.', file=sys.stderr)
        return 3
    try:
        backup.mkdir(parents=True)
        for src in (main_src, status_src):
            dest = backup / 'src' / src.name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        # Preserve the complete working build so rollback is possible even if recompilation fails.
        shutil.copytree(build, backup / 'build')
        (backup / 'RESTORE.txt').write_text(
            'Phase 2 working backup. To roll back: close Converseen, restore\n'
            'src/mainwindowimpl.cpp and src/dialogconversionstatus.cpp from this backup,\n'
            'then run: cmake --build build --parallel 4\n'
            'The complete pre-change build directory is saved as build/.\n',
            encoding='utf-8')
        # Only write after the entire backup succeeds.
        main_src.write_text(new_main, encoding='utf-8', newline='\n')
        status_src.write_text(new_status, encoding='utf-8', newline='\n')
    except Exception as e:
        print(f'ERROR applying Phase 2: {e}', file=sys.stderr)
        # Restore any partly written files from the backed-up originals.
        for src in (main_src, status_src):
            saved = backup / 'src' / src.name
            if saved.is_file():
                shutil.copy2(saved, src)
        return 3
    print('\nPHASE 2 APPLIED. Backup of the currently working files and build:')
    print(f'  {backup}')
    print('\nIn MSYS2 UCRT64:')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    print('Test with an output folder separate from your originals.')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
