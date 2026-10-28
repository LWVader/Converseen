#!/usr/bin/env python3
r'''Pixel Shroom Converseen Phase 6 — linked zoom + sampled live controls.

Requires the working Phase 5 source. Dry run is default. No dependency install.
PowerShell:
  py -3 .\pixel_shroom_converseen_phase6.py
  py -3 .\pixel_shroom_converseen_phase6.py --apply
Copy BOTH this file and pixelshroom_phase6.h into the Converseen project root.
'''
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

CPP = Path('src/mainwindowimpl.cpp')
HEADER = Path('src/pixelshroom_phase6.h')
MARKER = 'Pixel Shroom Phase 6: synchronized zoom and live quality preview.'
PHASE5 = 'Pixel Shroom Phase 5: use the visible DPI controls for EVERY batch.'
PHASE4 = 'Pixel Shroom Phase 4: compare the selected original with an actual exported image.'

COMPARE = r'''    // Pixel Shroom Phase 6: synchronized zoom and live quality preview.
    // Compare is the actual saved export, and preserves embedded-DPI verification.
    auto *compareOutput = new QPushButton(tr("Compare output..."), panel);
    heading->addWidget(compareOutput);
    connect(compareOutput, &QPushButton::clicked, this, [this]() {
        const int row = treeWidget->currentIndex().row();
        if (row < 0 || row >= iAList->size()) {
            QMessageBox::information(this, tr("Choose an original"),
                                     tr("Select an imported image first."));
            return;
        }
        const QString originalPath = iAList->at(row).completeFileName;
        if (!QFileInfo::exists(originalPath)) {
            QMessageBox::warning(this, tr("Missing image"), tr("Original image no longer exists."));
            return;
        }
        const QString folder = checkSameDir->isChecked()
            ? QFileInfo(originalPath).absolutePath() : lineDirectory->text();
        const QString exportedPath = QFileDialog::getOpenFileName(
            this, tr("Select exported image"), folder,
            tr("Artwork (*.png *.jpg *.jpeg *.webp *.tif *.tiff);;All files (*.*)"));
        if (exportedPath.isEmpty()) return;
        auto *print = findChild<QCheckBox*>("psPrintDpi");
        auto *dpi = findChild<QSpinBox*>("psDpiValue");
        const int requested = print && print->isChecked() && dpi ? dpi->value() : 0;
        PixelShroomPhase6::compare(this, originalPath, exportedPath, requested);
    });
    auto *previewButton = new QPushButton(tr("Live preview..."), panel);
    previewButton->setToolTip(tr("Preview smoothing, sharpening and JPEG/WebP compression before export."));
    heading->addWidget(previewButton);
'''

PREVIEW_CONNECTION = r'''    // Image Studio controls remain authoritative. Only commit preview changes on Apply.
    connect(previewButton, &QPushButton::clicked, this, [this, width, height, keepAspect]() {
        const int row = treeWidget->currentIndex().row();
        if (row < 0 || row >= iAList->size()) {
            QMessageBox::information(this, tr("Choose an image"),
                                     tr("Select an imported image to preview."));
            return;
        }
        const QString source = iAList->at(row).completeFileName;
        QString format = comboWFormats->currentIndex() == 0
            ? QFileInfo(source).suffix().toLower()
            : comboWFormats->currentText().split(" - ").first().trimmed().toLower();
        const int nativeQuality = (format == "webp") ? m_webPQuality : m_jpgQuality;
        const int startingQuality = m_psOverrideQuality ? m_psQuality : nativeQuality;
        PixelShroomPhase6::livePreview(this, source, QSize(width->value(), height->value()),
            keepAspect->isChecked(), format, m_psOverrideQuality,
            qBound(1, startingQuality, 100), m_psSmoothSigma, m_psSharpenSigma,
            m_isWebPLosslessCompression, [this](bool custom, int quality, double smooth, double sharpen) {
                if (auto *widget = findChild<QCheckBox*>("psOverrideQuality"))
                    widget->setChecked(custom);
                if (auto *widget = findChild<QSpinBox*>("psQualityNumber"))
                    widget->setValue(quality);
                if (auto *widget = findChild<QDoubleSpinBox*>("psSmoothNumber"))
                    widget->setValue(smooth);
                if (auto *widget = findChild<QDoubleSpinBox*>("psSharpenNumber"))
                    widget->setValue(sharpen);
                m_psOverrideQuality = custom;
                m_psQuality = quality;
                m_psSmoothSigma = smooth;
                m_psSharpenSigma = sharpen;
                statusBar()->showMessage(tr("Preview settings applied. Ready for batch conversion."), 6000);
            });
    });

'''

def one(s: str, old: str, new: str, desc: str) -> str:
    count = s.count(old)
    if count != 1:
        raise ValueError(f'{desc}: expected exactly one anchor, found {count}; no changes made')
    return s.replace(old, new, 1)


def patch(s: str) -> str:
    if MARKER in s:
        raise ValueError('Phase 6 already installed; refusing to apply twice')
    for required in (PHASE4, PHASE5,
                     'void MainWindowImpl::setupPixelShroomControls()',
                     'psPrintDpi', 'psDpiValue'):
        if required not in s:
            raise ValueError(f'Missing Phase 5 source marker {required!r}; stop to protect the working version')
    s = one(s, '#include <QDialog>', '#include <QDialog>\n#include "pixelshroom_phase6.h"', 'include')

    start = s.find('    // ' + PHASE4)
    end = s.find('    auto *collapse = new QToolButton(panel);', start)
    if start < 0 or end < 0:
        raise ValueError('Original Phase 4 comparison button could not be located')
    region = s[start:end]
    if ('auto *compareOutput = new QPushButton' not in region or
        'connect(compareOutput, &QPushButton::clicked' not in region or
        '        dlg.exec();\n    });' not in region):
        raise ValueError('Comparison source differs from Phase 5; refusing to replace it')
    s = s[:start] + COMPARE + s[end:]
    s = one(s, '    auto *overrideQuality = new QCheckBox(tr("Use custom quality for JPEG / WebP"), compressTab);',
        '    auto *overrideQuality = new QCheckBox(tr("Use custom quality for JPEG / WebP"), compressTab);\n'
        '    overrideQuality->setObjectName("psOverrideQuality");', 'quality override')
    s = one(s, '    auto *qualityNumber = new QSpinBox(compressTab);',
        '    auto *qualityNumber = new QSpinBox(compressTab);\n'
        '    qualityNumber->setObjectName("psQualityNumber");', 'quality numeric')
    s = one(s, '        auto *number = new QDoubleSpinBox(enhanceTab);',
        '        auto *number = new QDoubleSpinBox(enhanceTab);\n'
        '        number->setObjectName(smoothing ? "psSmoothNumber" : "psSharpenNumber");',
        'enhance numeric')
    s = one(s, '    // Avoid the compressed single-row toolbar seen in Phase 1.',
        PREVIEW_CONNECTION + '    // Avoid the compressed single-row toolbar seen in Phase 1.',
        'live preview connection')
    if s.count(MARKER) != 1:
        raise ValueError('Internal Phase 6 marker verification failed')
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Back up the working executable and source, then apply')
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Path to existing Converseen fork')
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    source, header, exe = root / CPP, root / HEADER, root / 'build/converseen.exe'
    helper_template = Path(__file__).resolve().parent / 'pixelshroom_phase6.h'
    if not all(p.is_file() for p in (root / 'CMakeLists.txt', source, exe, helper_template)):
        print('ERROR: The project, working executable, or pixelshroom_phase6.h is missing.', file=sys.stderr)
        return 2
    if header.exists():
        print('ERROR: src/pixelshroom_phase6.h already exists; refusing to overwrite.', file=sys.stderr)
        return 2
    try:
        current = source.read_text(encoding='utf-8-sig')
        revised = patch(current)
        helper = helper_template.read_text(encoding='utf-8-sig')
        if 'namespace PixelShroomPhase6 {' not in helper:
            raise ValueError('Phase 6 companion header is invalid')
    except (OSError, UnicodeError, ValueError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 2
    print('PHASE 6 SOURCE CHECK PASSED: Phase 5 source and comparison anchors verified.')
    print('Only src/mainwindowimpl.cpp is edited; src/pixelshroom_phase6.h is added.')
    print('Batch converter, print DPI, main.cpp, CMake and status dialog are left unchanged.')
    if not args.apply:
        print('DRY RUN PASSED — no files changed. To install:')
        print('  py -3 .\\pixel_shroom_converseen_phase6.py --apply')
        return 0
    backup = root.parent / f'{root.name}-phase6-working-backup-{datetime.now():%Y%m%d-%H%M%S}'
    if backup.exists():
        print('ERROR: Backup folder already exists; retry.', file=sys.stderr)
        return 3
    temp = source.with_name(source.name+'.phase6-tmp')
    try:
        (backup / 'src').mkdir(parents=True)
        shutil.copy2(source, backup / CPP)
        shutil.copy2(exe, backup / 'converseen.exe')
        (backup / 'ROLLBACK.txt').write_text(
            'Close Converseen. Restore the saved src/mainwindowimpl.cpp from this backup.\n'
            'Delete the NEW src/pixelshroom_phase6.h, then rebuild with\n'
            'cmake --build build --parallel 4 (MSYS2 UCRT64).\n'
            'Or restore the saved working converseen.exe into build/ without rebuilding.\n',
            encoding='utf-8')
        temp.write_text(revised, encoding='utf-8', newline='\n')
        temp.replace(source)
        header.write_text(helper, encoding='utf-8', newline='\n')
    except Exception as exc:
        print(f'ERROR applying patch: {exc}', file=sys.stderr)
        temp.unlink(missing_ok=True)
        if (backup / CPP).exists(): shutil.copy2(backup / CPP, source)
        header.unlink(missing_ok=True)
        return 3
    print('PHASE 6 APPLIED. Working backup:', backup)
    print('In MSYS2 UCRT64 run:')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
