#!/usr/bin/env python3
"""Phase 4: add an actual-output side-by-side comparison to Pixel Shroom Converseen.

Requires Phase 3 UI. Runs in dry-run mode until --apply is passed.
Only modifies src/mainwindowimpl.cpp. It backs up the working executable and source.

    py -3 pixel_shroom_converseen_phase4.py
    py -3 pixel_shroom_converseen_phase4.py --apply
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

TARGET = Path('src/mainwindowimpl.cpp')
PHASE3_MARKER = 'Pixel Shroom Phase 3: hide the native Dimensions tab, not its widgets.'
PHASE4_MARKER = 'Pixel Shroom Phase 4: compare the selected original with an actual exported image.'
INCLUDE_ANCHOR = '#include <QTabBar>'
INCLUDE_REPLACEMENT = '''#include <QTabBar>
#include <QDialog>
#include <QImageReader>
#include <QPixmap>
#include <QFileInfo>
#include <QDesktopServices>
#include <QUrl>'''
BUTTON_ANCHOR = '    heading->addWidget(title, 1);'
BUTTON_REPLACEMENT = r'''    heading->addWidget(title, 1);

    // Pixel Shroom Phase 4: compare the selected original with an actual exported image.
    // This compares real files AFTER conversion, not a simulated encoder preview.
    auto *compareOutput = new QPushButton(tr("Compare output..."), panel);
    compareOutput->setToolTip(tr("Compare your selected input with an exported JPEG, PNG or WebP file."));
    heading->addWidget(compareOutput);
    connect(compareOutput, &QPushButton::clicked, this, [this]() {
        const int selectedRow = treeWidget->currentIndex().row();
        if (selectedRow < 0 || selectedRow >= iAList->size()) {
            QMessageBox::information(this, tr("Choose an original"),
                                     tr("Select an imported image in the list first."));
            return;
        }
        const QString originalPath = iAList->at(selectedRow).completeFileName;
        if (!QFileInfo::exists(originalPath)) {
            QMessageBox::warning(this, tr("Original unavailable"),
                                 tr("The selected source file could not be found."));
            return;
        }
        const QString suggestedFolder = checkSameDir->isChecked()
            ? QFileInfo(originalPath).absolutePath() : lineDirectory->text();
        const QString exportedPath = QFileDialog::getOpenFileName(
            this, tr("Select your converted image"), suggestedFolder,
            tr("Artwork (*.png *.jpg *.jpeg *.webp *.tif *.tiff);;All files (*.*)"));
        if (exportedPath.isEmpty())
            return;

        QDialog dlg(this);
        dlg.setWindowTitle(tr("Pixel Shroom | Compare original and output"));
        dlg.resize(1010, 620);
        dlg.setMinimumSize(720, 480);
        dlg.setStyleSheet(R"PSCMP(
            QDialog { background: #20252b; }
            QLabel { color: #eff4f7; }
            QLabel#psComparisonImage { background: #12171d; border: 1px solid #607381;
                border-radius: 5px; padding: 6px; }
            QPushButton { color: #f6f8fa; background: #364650;
                border: 1px solid #63798b; padding: 6px 12px; border-radius: 4px; }
        )PSCMP");
        auto *layout = new QVBoxLayout(&dlg);
        layout->setContentsMargins(14, 12, 14, 12);
        auto *headingLabel = new QLabel(tr("ORIGINAL  /  CONVERTED OUTPUT"), &dlg);
        QFont comparisonTitleFont = headingLabel->font();
        comparisonTitleFont.setBold(true);
        headingLabel->setFont(comparisonTitleFont);
        layout->addWidget(headingLabel);
        auto *columns = new QHBoxLayout();
        columns->setSpacing(14);
        layout->addLayout(columns, 1);

        QLabel *originalImage = nullptr;
        QLabel *exportedImage = nullptr;
        QLabel *originalDetails = nullptr;
        QLabel *exportedDetails = nullptr;
        auto addPane = [&dlg, columns](const QString &name,
                                       QLabel *&imageLabel, QLabel *&detailsLabel) {
            auto *pane = new QVBoxLayout();
            auto *paneTitle = new QLabel(name, &dlg);
            pane->addWidget(paneTitle);
            imageLabel = new QLabel(&dlg);
            imageLabel->setObjectName("psComparisonImage");
            imageLabel->setMinimumSize(240, 280);
            imageLabel->setAlignment(Qt::AlignCenter);
            imageLabel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
            pane->addWidget(imageLabel, 1);
            detailsLabel = new QLabel(&dlg);
            detailsLabel->setWordWrap(true);
            pane->addWidget(detailsLabel);
            columns->addLayout(pane, 1);
        };
        addPane(tr("BEFORE | ORIGINAL"), originalImage, originalDetails);
        addPane(tr("AFTER | EXPORTED FILE"), exportedImage, exportedDetails);

        auto loadPane = [](const QString &path, QLabel *imageLabel, QLabel *detailsLabel) -> QSize {
            QImageReader reader(path);
            reader.setAutoTransform(true);
            const QSize actualPixels = reader.size();
            if (actualPixels.isValid())
                reader.setScaledSize(actualPixels.scaled(420, 380, Qt::KeepAspectRatio));
            const QImage preview = reader.read();
            const QFileInfo file(path);
            if (preview.isNull()) {
                imageLabel->setText(QObject::tr("No Qt preview available for this format"));
                detailsLabel->setText(file.fileName() + "\n" + reader.errorString());
                return actualPixels;
            }
            imageLabel->setPixmap(QPixmap::fromImage(preview));
            const double dpiX = preview.dotsPerMeterX() * 0.0254;
            const double dpiY = preview.dotsPerMeterY() * 0.0254;
            QString dpiLabel = QObject::tr("DPI: not reliably reported");
            if (dpiX > 0 && dpiY > 0) {
                dpiLabel = QObject::tr("Reported image DPI: %1 × %2 (check final metadata)")
                    .arg(qRound(dpiX)).arg(qRound(dpiY));
            }
            detailsLabel->setText(QObject::tr("%1\n%2 × %3 pixels  |  %4 MiB\n%5")
                .arg(file.fileName())
                .arg(actualPixels.width()).arg(actualPixels.height())
                .arg(QString::number(file.size() / 1048576.0, 'f', 2))
                .arg(dpiLabel));
            return actualPixels;
        };
        const QSize originalSize = loadPane(originalPath, originalImage, originalDetails);
        const QSize exportedSize = loadPane(exportedPath, exportedImage, exportedDetails);

        auto *summary = new QLabel(&dlg);
        summary->setWordWrap(true);
        if (originalSize.isValid() && exportedSize.isValid()) {
            const double scaleX = static_cast<double>(exportedSize.width()) / originalSize.width();
            const double scaleY = static_cast<double>(exportedSize.height()) / originalSize.height();
            if (scaleX > 2.0 || scaleY > 2.0) {
                summary->setText(QObject::tr("Upscaling: %1× width and %2× height. More pixels do not automatically create more fine detail.")
                    .arg(QString::number(scaleX, 'f', 2))
                    .arg(QString::number(scaleY, 'f', 2)));
                summary->setStyleSheet("color: #ffd49c; font-weight: bold;");
            } else {
                summary->setText(QObject::tr("Viewing the actual converted image. Open the full-size export to inspect fine details at 100%."));
            }
        } else {
            summary->setText(QObject::tr("Dimensions could not be read for one of the files."));
        }
        layout->addWidget(summary);
        auto *buttons = new QHBoxLayout();
        buttons->addStretch();
        auto *openExport = new QPushButton(tr("Open exported file"), &dlg);
        connect(openExport, &QPushButton::clicked, &dlg, [exportedPath]() {
            QDesktopServices::openUrl(QUrl::fromLocalFile(exportedPath));
        });
        buttons->addWidget(openExport);
        auto *closeButton = new QPushButton(tr("Close"), &dlg);
        connect(closeButton, &QPushButton::clicked, &dlg, &QDialog::accept);
        buttons->addWidget(closeButton);
        layout->addLayout(buttons);
        dlg.exec();
    });'''


def replace_exact_once(content: str, old: str, new: str, description: str) -> str:
    count = content.count(old)
    if count != 1:
        raise ValueError(f'{description}: expected exactly one anchor, found {count}; source untouched.')
    return content.replace(old, new, 1)


def patch(content: str) -> str:
    if PHASE3_MARKER not in content:
        raise ValueError('Phase 3 duplicate-controls fix not detected. Apply Phase 3 first.')
    if PHASE4_MARKER in content:
        raise ValueError('Phase 4 comparison is already installed; refusing to patch twice.')
    if content.count('void MainWindowImpl::setupPixelShroomControls()') != 1:
        raise ValueError('Expected Phase 3 setup function not found exactly once.')
    revised = replace_exact_once(content, INCLUDE_ANCHOR, INCLUDE_REPLACEMENT, 'Qt includes')
    revised = replace_exact_once(revised, BUTTON_ANCHOR, BUTTON_REPLACEMENT, 'comparison button')
    if revised.count(PHASE4_MARKER) != 1:
        raise ValueError('Comparison insertion failed verification.')
    return revised


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--apply', action='store_true', help='Modify sources after dry-run validation and backup')
    ap.add_argument('--project', type=Path, default=Path.cwd(), help='Clone folder')
    args = ap.parse_args()
    root = args.project.expanduser().resolve()
    src = root / TARGET
    exe = root / 'build/converseen.exe'
    if not (root / 'CMakeLists.txt').is_file() or not src.is_file() or not exe.is_file():
        print('ERROR: Run inside the cloned Converseen project containing CMakeLists.txt and build/converseen.exe.', file=sys.stderr)
        return 2
    try:
        old = src.read_text(encoding='utf-8-sig')
        new = patch(old)
    except (OSError, UnicodeError, ValueError) as err:
        print(f'ERROR: {err}', file=sys.stderr)
        return 2
    print('PHASE 4 SOURCE CHECK PASSED')
    print('Only src/mainwindowimpl.cpp will change. The converter and main.cpp remain untouched.')
    if not args.apply:
        print('DRY RUN PASSED — no changes. To apply:')
        print('  py -3 pixel_shroom_converseen_phase4.py --apply')
        return 0
    backup = root.parent / f'{root.name}-phase4-working-backup-{datetime.now():%Y%m%d-%H%M%S}'
    if backup.exists():
        print('ERROR: Backup already exists. Retry with a new timestamp.', file=sys.stderr)
        return 3
    temp = src.with_name(src.name + '.phase4-tmp')
    try:
        (backup / 'src').mkdir(parents=True)
        shutil.copy2(src, backup / TARGET)
        shutil.copy2(exe, backup / 'converseen.exe')
        (backup / 'README.txt').write_text(
            'Phase 4 backup: original file at src/mainwindowimpl.cpp and working converseen.exe.\n'
            'To roll back: close Converseen; copy backed-up source to src/mainwindowimpl.cpp,\n'
            'then run cmake --build build --parallel 4 in MSYS2 UCRT64.\n'
            'If needed, restore converseen.exe to build after closing the application.\n',
            encoding='utf-8')
        temp.write_text(new, encoding='utf-8', newline='\n')
        temp.replace(src)
    except Exception as err:
        print(f'ERROR: Could not apply: {err}', file=sys.stderr)
        if (backup / TARGET).is_file():
            shutil.copy2(backup / TARGET, src)
        temp.unlink(missing_ok=True)
        return 3
    print('PHASE 4 PATCH APPLIED.')
    print(f'Backup: {backup}')
    print('In MSYS2 UCRT64:')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
