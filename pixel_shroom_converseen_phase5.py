#!/usr/bin/env python3
r"""Pixel Shroom Converseen Phase 5: reliable print DPI + accurate Compare metadata.

Targets the local fork after successful Phases 1-4. Dry-run is the default.
No network access, dependency installation, or modification to main.cpp.

PowerShell:
    py -3 .\pixel_shroom_converseen_phase5.py
    py -3 .\pixel_shroom_converseen_phase5.py --apply
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import re
import sys

SOURCE = Path('src/mainwindowimpl.cpp')
CONVERTER = Path('src/converter.cpp')
MARKER = 'Pixel Shroom Phase 5: use the visible DPI controls for EVERY batch.'


def change_once(s: str, old: str, new: str, label: str) -> str:
    hits = s.count(old)
    if hits != 1:
        raise ValueError(f'{label}: expected exactly one matching source anchor; found {hits}. Nothing changed.')
    return s.replace(old, new, 1)


METADATA_OLD = '''            const double dpiX = preview.dotsPerMeterX() * 0.0254;
            const double dpiY = preview.dotsPerMeterY() * 0.0254;
            QString dpiLabel = QObject::tr("DPI: not reliably reported");
            if (dpiX > 0 && dpiY > 0) {
                dpiLabel = QObject::tr("Reported image DPI: %1 × %2 (check final metadata)")
                    .arg(qRound(dpiX)).arg(qRound(dpiY));
            }'''

METADATA_NEW = r'''            // Read physical resolution from the ACTUAL file, not from a downscaled
            // Qt preview (which can report a misleading default of 96 DPI).
            double embeddedX = 0.0;
            double embeddedY = 0.0;
            QString dpiLabel = QObject::tr("Embedded DPI: not specified");
            try {
                Magick::Image fileMetadata;
                fileMetadata.ping(path.toStdString());
                const auto units = fileMetadata.resolutionUnits();
                const double toDpi = (units == Magick::PixelsPerCentimeterResolution)
                    ? 2.54 : 1.0;
                if (units == Magick::PixelsPerCentimeterResolution ||
                    units == Magick::PixelsPerInchResolution) {
                    embeddedX = fileMetadata.xResolution() * toDpi;
                    embeddedY = fileMetadata.yResolution() * toDpi;
                    if (embeddedX > 0.0 && embeddedY > 0.0) {
                        dpiLabel = QObject::tr("Embedded print DPI: %1 × %2")
                            .arg(qRound(embeddedX)).arg(qRound(embeddedY));
                    }
                }
            } catch (const Magick::Exception &e) {
                dpiLabel = QObject::tr("Embedded DPI unavailable: %1")
                    .arg(QString::fromStdString(e.what()));
            }
            if (readDpiX) *readDpiX = embeddedX;
            if (readDpiY) *readDpiY = embeddedY;'''

DPI_SYNC = r'''    // Pixel Shroom Phase 5: use the visible DPI controls for EVERY batch.
    // The native hidden spinboxes are reset to zero after the studio is built
    // during MainWindowImpl construction. A checked DPI box does not emit a
    // toggled signal again; sync it explicitly at the conversion boundary.
    if (auto *studioPrintDpi = findChild<QCheckBox*>("psPrintDpi")) {
        const bool printEnabled = studioPrintDpi->isChecked();
        groupResolution->setChecked(printEnabled);
        if (printEnabled) {
            auto *studioDpiValue = findChild<QSpinBox*>("psDpiValue");
            if (!studioDpiValue || studioDpiValue->value() < 72) {
                QMessageBox::warning(this, tr("Invalid print DPI"),
                                     tr("Choose a print resolution of at least 72 DPI."));
                return;
            }
            spin_resX->setValue(studioDpiValue->value());
            spin_resY->setValue(studioDpiValue->value());
        }
    }
'''

VERIFY_OUTPUT = r'''        // Print verification uses the actual saved file's embedded units.
        if (auto *studioPrintDpi = findChild<QCheckBox*>("psPrintDpi")) {
            if (studioPrintDpi->isChecked()) {
                if (auto *studioDpiValue = findChild<QSpinBox*>("psDpiValue")) {
                    const int wanted = studioDpiValue->value();
                    if (psOutputDpiX <= 0.0 || psOutputDpiY <= 0.0 ||
                        qAbs(psOutputDpiX - wanted) > 2.0 ||
                        qAbs(psOutputDpiY - wanted) > 2.0) {
                        summary->setText(summary->text() +
                            QObject::tr("\nWARNING: Export does not contain the expected %1 DPI metadata.")
                                .arg(wanted));
                        summary->setStyleSheet("color: #ffd49c; font-weight: bold;");
                    } else {
                        summary->setText(summary->text() +
                            QObject::tr("\nPrint DPI verified: %1 × %2 DPI embedded in exported file.")
                                .arg(qRound(psOutputDpiX)).arg(qRound(psOutputDpiY)));
                    }
                }
            }
        }
'''


def patch(s: str, converter: str) -> str:
    if MARKER in s:
        raise ValueError('Phase 5 is already installed. Refusing to apply it twice.')
    required = ('Pixel Shroom Phase 3: hide the native Dimensions tab, not its widgets.',
                'Pixel Shroom Phase 4: compare the selected original with an actual exported image.',
                'void MainWindowImpl::setupPixelShroomControls()')
    for key in required:
        if key not in s:
            raise ValueError(f'Expected Phase 4 source marker not found: {key!r}')
    for pattern in (r'(?m)^\s*my_image\.resolutionUnits\(Magick::PixelsPerInchResolution\);',
                    r'(?m)^\s*my_image\.density\(m_densityString\.toStdString\(\)\);'):
        if re.search(pattern, converter) is None:
            raise ValueError(f'Phase 1 converter DPI path not verified: {pattern!r}. Refusing to patch.')

    s = change_once(s,
        '    printDpi->setChecked(groupResolution->isChecked());',
        '    printDpi->setObjectName("psPrintDpi");\n'
        '    printDpi->setChecked(groupResolution->isChecked());', 'print toggle identifier')
    s = change_once(s,
        '    dpi->setRange(72, 1200);',
        '    dpi->setObjectName("psDpiValue");\n'
        '    dpi->setRange(72, 1200);', 'DPI numeric identifier')
    # Be strict: this is the already-upgraded version that sends density
    # whenever the checkbox is enabled, instead of comparing to source DPI.
    start = s.find('    /* Change image density */')
    if start == -1 or 'if (groupResolution->isChecked()) {' not in s[start:start+150]:
        raise ValueError('The Phase 1 unconditional setDensity path could not be verified.')
    s = change_once(s, '    /* Change image density */', DPI_SYNC + '    /* Change image density */',
                    'DPI handoff at batch start')

    s = change_once(s,
        'auto loadPane = [](const QString &path, QLabel *imageLabel, QLabel *detailsLabel) -> QSize {',
        'auto loadPane = [](const QString &path, QLabel *imageLabel, QLabel *detailsLabel,\n'
        '                           double *readDpiX, double *readDpiY) -> QSize {\n'
        '            if (readDpiX) *readDpiX = 0.0;\n'
        '            if (readDpiY) *readDpiY = 0.0;', 'compare reader signature')
    s = change_once(s, METADATA_OLD, METADATA_NEW, 'Qt fallback DPI display')
    s = change_once(s,
        '        const QSize originalSize = loadPane(originalPath, originalImage, originalDetails);\n'
        '        const QSize exportedSize = loadPane(exportedPath, exportedImage, exportedDetails);',
        '        const QSize originalSize = loadPane(originalPath, originalImage, originalDetails, nullptr, nullptr);\n'
        '        double psOutputDpiX = 0.0;\n'
        '        double psOutputDpiY = 0.0;\n'
        '        const QSize exportedSize = loadPane(exportedPath, exportedImage, exportedDetails,\n'
        '                                            &psOutputDpiX, &psOutputDpiY);',
        'output metadata collection')
    s = change_once(s,
        '        layout->addWidget(summary);',
        VERIFY_OUTPUT + '        layout->addWidget(summary);',
        'actual output DPI verification')

    if s.count(MARKER) != 1:
        raise ValueError('Internal marker verification failed.')
    return s


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Back up working files, then apply the patch')
    parser.add_argument('--project', type=Path, default=Path.cwd(), help='Existing Converseen project directory')
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    main_source = root / SOURCE
    converter_source = root / CONVERTER
    exe = root / 'build/converseen.exe'
    if not (root / 'CMakeLists.txt').is_file() or not main_source.is_file() or \
       not converter_source.is_file() or not exe.is_file():
        print('ERROR: Run this from the built Converseen fork (CMakeLists.txt and build/converseen.exe required).',
              file=sys.stderr)
        return 2
    try:
        original = main_source.read_text(encoding='utf-8-sig')
        converter = converter_source.read_text(encoding='utf-8-sig')
        changed = patch(original, converter)
    except (OSError, UnicodeError, ValueError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print('PHASE 5 CHECK PASSED: source markers, DPI converter, and comparison anchors verified.')
    print('Only src/mainwindowimpl.cpp will be changed. The converter and main.cpp are not modified.')
    if not args.apply:
        print('DRY RUN PASSED — nothing changed. To apply:')
        print('  py -3 .\\pixel_shroom_converseen_phase5.py --apply')
        return 0

    backup = root.parent / f'{root.name}-phase5-working-backup-{datetime.now():%Y%m%d-%H%M%S}'
    pending = main_source.with_name(main_source.name + '.phase5-tmp')
    if backup.exists():
        print(f'ERROR: Backup already exists: {backup}', file=sys.stderr)
        return 3
    try:
        (backup / 'src').mkdir(parents=True)
        shutil.copy2(main_source, backup / SOURCE)
        shutil.copy2(exe, backup / 'converseen.exe')
        (backup / 'ROLLBACK.txt').write_text(
            'Phase 5 backup contains the PRE-PATCH source and working converseen.exe.\n'
            'Close Converseen. Restore src/mainwindowimpl.cpp from this directory,\n'
            'then rebuild with: cmake --build build --parallel 4\n'
            'To restore the old executable without rebuilding, copy converseen.exe to build/.\n',
            encoding='utf-8')
        pending.write_text(changed, encoding='utf-8', newline='\n')
        pending.replace(main_source)
    except Exception as exc:
        print(f'ERROR: Could not apply Phase 5: {exc}', file=sys.stderr)
        pending.unlink(missing_ok=True)
        saved = backup / SOURCE
        if saved.is_file():
            shutil.copy2(saved, main_source)
        return 3
    print('PHASE 5 PATCH APPLIED.')
    print('Working source/executable backup:', backup)
    print('Next, in MSYS2 UCRT64:')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
