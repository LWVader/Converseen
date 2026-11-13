#!/usr/bin/env python3
"""Phase 19: share resize/website dimensions, <50 MiB original limit, orientation dialog.

Run from Pixel Shroom Converseen root. DRY RUN by default.
  py -3 pixel_shroom_phase19_shared_resize.py
  py -3 pixel_shroom_phase19_shared_resize.py --apply

Applies an all-or-nothing, source-anchored transformation to two files:
  src/mainwindowimpl.cpp
  src/pixelshroom_upload_optimizer.h
Leaves converter.cpp, DPI handling, installer and existing binaries unchanged.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARK = "// Pixel Shroom Phase 19: one shared Resize/Website pixel size."


def one(s: str, before: str, after: str, description: str) -> str:
    count = s.count(before)
    if count != 1:
        raise ValueError(f"{description}: expected one exact source anchor, found {count}; no changes made.")
    return s.replace(before, after, 1)


OLD_PREVIEW_CONTROL = '''    auto *uploadRow = new QHBoxLayout();
    auto *previewEdgeLabel = new QLabel(tr("Preview longest edge"), uploadTab);
    auto *previewEdge = new QSpinBox(uploadTab);
    previewEdge->setObjectName("psUploadPreviewEdge");
    previewEdge->setRange(512, 4096);
    previewEdge->setSingleStep(256);
    previewEdge->setValue(2048);
    previewEdge->setSuffix(tr(" px"));
    uploadRow->addWidget(previewEdgeLabel);
    uploadRow->addWidget(previewEdge);
    uploadRow->addStretch();
    uploadLayout->addLayout(uploadRow);'''

NEW_SHARED_CONTROL = '''    // Pixel Shroom Phase 19: one shared Resize/Website pixel size.
    // The main Resize tab owns the values; Website only reads the same widgets.
    auto *sharedSize = new QLabel(uploadTab);
    sharedSize->setObjectName("psUploadSharedDimensions");
    sharedSize->setWordWrap(true);
    auto updateSharedSize = [width, height, sharedSize]() {
        sharedSize->setText(QObject::tr("Preview maximum from Resize: %1 x %2 px. "
                    "No upscaling; reduce dimensions further only if the 10 MiB cap requires it.")
                    .arg(width->value()).arg(height->value()));
    };
    QObject::connect(width, QOverload<int>::of(&QSpinBox::valueChanged),
                     uploadTab, [updateSharedSize](int) { updateSharedSize(); });
    QObject::connect(height, QOverload<int>::of(&QSpinBox::valueChanged),
                     uploadTab, [updateSharedSize](int) { updateSharedSize(); });
    // Preset selection updates both spinboxes under QSignalBlocker.
    QObject::connect(preset, QOverload<int>::of(&QComboBox::currentIndexChanged),
                     uploadTab, [updateSharedSize](int) { updateSharedSize(); });
    updateSharedSize();
    uploadLayout->addWidget(sharedSize);'''

OLD_UPLOAD_ACTION = '''    connect(uploadAction, &QPushButton::clicked, this,
            [this, previewEdge, allowPreviewDownscale]() {
        QStringList sources;
        for (const auto &item : *iAList)
            if (!item.completeFileName.isEmpty()) sources << item.completeFileName;
        sources.removeDuplicates();
        QString destination = QDir::fromNativeSeparators(lineDirectory->text().trimmed());
        if (checkSameDir->isChecked() && !sources.isEmpty())
            destination = QFileInfo(sources.first()).absolutePath();
        PixelShroomUpload::start(this, sources, destination,
                                previewEdge->value(), allowPreviewDownscale->isChecked());
    });'''

NEW_UPLOAD_ACTION = '''    connect(uploadAction, &QPushButton::clicked, this,
            [this, width, height, allowPreviewDownscale]() {
        // A 1-pixel value can be present before images have been selected;
        // never accidentally create unusably tiny website previews.
        if (width->value() < 64 || height->value() < 64) {
            QMessageBox::warning(this, tr("Resize dimensions needed"),
                tr("Choose width and height of at least 64 px in Resize before Website optimization."));
            return;
        }
        QStringList sources;
        for (const auto &item : *iAList)
            if (!item.completeFileName.isEmpty()) sources << item.completeFileName;
        sources.removeDuplicates();
        QString destination = QDir::fromNativeSeparators(lineDirectory->text().trimmed());
        if (checkSameDir->isChecked() && !sources.isEmpty())
            destination = QFileInfo(sources.first()).absolutePath();
        PixelShroomUpload::start(this, sources, destination,
                                width->value(), height->value(),
                                allowPreviewDownscale->isChecked());
    });'''

OLD_NATIVE_TABS = '''    // Pixel Shroom Phase 3: hide the native Dimensions tab, not its widgets.
    // Phase 2 deliberately updates groupDimensions, spin_geoWidth/Height,
    // checkRelative, and groupResolution behind the scenes. Removing or
    // disabling them could break the already-working conversion logic.
    // Keep the Rotate and Flip page available in the Actions Panel.
    const int nativeDimensionsTab = tabWidget->indexOf(tab);
    const int rotateFlipTab = tabWidget->indexOf(tab_2);
    if (nativeDimensionsTab >= 0 && rotateFlipTab >= 0) {
        tabWidget->setCurrentIndex(rotateFlipTab);
        tabWidget->setTabVisible(nativeDimensionsTab, false);
        tabWidget->setTabText(rotateFlipTab, tr("Rotate / Flip"));
    }'''

NEW_ORIENTATION = '''    // The original native Resize/DPI widgets stay alive (hidden) for the
    // working conversion engine. Only the native Rotate / Flip UI is moved.
    const int nativeDimensionsTab = tabWidget->indexOf(tab);
    const int rotateFlipTab = tabWidget->indexOf(tab_2);
    if (nativeDimensionsTab < 0 || rotateFlipTab < 0) {
        qWarning("Pixel Shroom: could not move native orientation controls");
    } else {
        tabWidget->setTabVisible(nativeDimensionsTab, false);
        tabWidget->removeTab(rotateFlipTab); // does not delete the widget
        tabWidget->hide();                  // collapse empty Actions Panel tab strip

        auto *orientationDialog = new QDialog(this);
        orientationDialog->setObjectName("psOrientationDialog");
        orientationDialog->setWindowTitle(tr("Orientation - Rotate / Flip"));
        orientationDialog->setMinimumSize(440, 340);
        auto *orientationLayout = new QVBoxLayout(orientationDialog);
        orientationLayout->setContentsMargins(14, 14, 14, 14);
        orientationLayout->setSpacing(10);
        orientationLayout->addWidget(tab_2, 1); // reuse existing wired controls
        auto *orientationClose = new QPushButton(tr("Back to Resize"), orientationDialog);
        orientationLayout->addWidget(orientationClose, 0, Qt::AlignRight);
        QObject::connect(orientationClose, &QPushButton::clicked,
                         orientationDialog, &QDialog::hide);
        auto *orientationOpen = new QPushButton(tr("Orientation...  Rotate / Flip"), resizeTab);
        orientationOpen->setObjectName("psOrientationOpen");
        sizeGrid->addWidget(orientationOpen, 6, 0, 1, 4);
        QObject::connect(orientationOpen, &QPushButton::clicked,
                         orientationDialog, [orientationDialog]() {
            orientationDialog->show();
            orientationDialog->raise();
            orientationDialog->activateWindow();
        });
    }'''


def transform_main(s: str) -> str:
    if MARK in s:
        raise ValueError("Phase 19 already appears to be installed.")
    for req in (
        'Pixel Shroom Phase 18: independent settings window with live theme preview.',
        'auto *width = new QSpinBox(resizeTab);',
        'auto *height = new QSpinBox(resizeTab);',
        'auto *uploadTab = new QWidget(tabs);',
        'auto *sizeGrid = new QGridLayout(resizeTab);',
    ):
        if req not in s:
            raise ValueError(f"Requires current Phase 18+ Image Studio. Missing {req!r}")
    s = one(s, OLD_PREVIEW_CONTROL, NEW_SHARED_CONTROL, "remove duplicated Website pixel input")
    s = one(s, OLD_UPLOAD_ACTION, NEW_UPLOAD_ACTION, "shared dimensions at upload time")
    s = one(s, OLD_NATIVE_TABS, NEW_ORIENTATION, "relocate native Rotate/Flip to Resize dialog")
    s = one(s,
        '"PREVIEW: 10 MiB maximum. ORIGINAL: 100 MiB maximum. "',
        '"PREVIEW: under 10 MiB. ORIGINAL: under 50 MiB. "',
        "Website size explanatory text")
    s = one(s,
        'tr("Reduce preview dimensions further only when needed to stay under 10 MiB")',
        'tr("Automatically shrink website previews further if necessary to fit under 10 MiB")',
        "Website preview downscale toggle text")
    # Use a non-modal dialog for the original orientation controls; the value
    # signals remain owned by MainWindowImpl, and no converter logic changes.
    return s


OLD_PREVIEW_START = '''inline BlobCandidate choosePreview(Magick::Image &input, const QByteArray &original,
                                   const QString &suffix, int maxEdge, bool downscale,
                                   int &width, int &height) {
    Magick::Image preview(input);
    const int iw = int(input.columns()), ih = int(input.rows());
    const int edge = std::max(256, std::min(4096, maxEdge));
    if (std::max(iw, ih) > edge) {
        const double scale = double(edge) / std::max(iw,ih);
        preview.filterType(Magick::LanczosFilter);
        preview.resize(Magick::Geometry(size_t(std::max(1, qRound(iw*scale))),
                                        size_t(std::max(1, qRound(ih*scale)))));
    }'''

NEW_PREVIEW_START = '''inline BlobCandidate choosePreview(Magick::Image &input, const QByteArray &original,
                                   const QString &suffix, int maxWidth, int maxHeight,
                                   bool downscale, int &width, int &height) {
    Magick::Image preview(input);
    const int iw = int(input.columns()), ih = int(input.rows());
    // Website uses the same bounding dimensions as the Resize tab. Do not
    // upscale a source that is already smaller; keep original aspect ratio.
    const int targetW = std::max(1, std::min(20000, maxWidth));
    const int targetH = std::max(1, std::min(20000, maxHeight));
    const double scale = std::min({1.0, double(targetW) / iw, double(targetH) / ih});
    if (scale < 1.0) {
        preview.filterType(Magick::LanczosFilter);
        preview.resize(Magick::Geometry(size_t(std::max(1, qRound(iw*scale))),
                                        size_t(std::max(1, qRound(ih*scale)))));
    }'''


def transform_optimizer(s: str) -> str:
    if "Pixel Shroom Phase 19: shared Resize bounds" in s:
        raise ValueError("Phase 19 optimizer already appears to be installed.")
    if 'namespace PixelShroomUpload {' not in s:
        raise ValueError("Website optimizer header doesn't match the expected source.")
    s = one(s,
        'constexpr qint64 OriginalLimit = qint64(100) * 1024 * 1024;',
        'constexpr qint64 OriginalLimit = qint64(50) * 1024 * 1024; // STRICT: files must be smaller',
        "50 MiB original cap")
    s = one(s, OLD_PREVIEW_START,
            '    // Pixel Shroom Phase 19: shared Resize bounds\n' + NEW_PREVIEW_START,
            "2D preview bounds")
    # The website storage caps are strict less-than limits.
    for old_size_test, new_size_test in (
        ('original.size() <= PreviewLimit', 'original.size() < PreviewLimit'),
        ('candidate.bytes.size() <= PreviewLimit', 'candidate.bytes.size() < PreviewLimit'),
        ('best.bytes.size() <= PreviewLimit', 'best.bytes.size() < PreviewLimit'),
        ('if (preview.bytes.size() > PreviewLimit)', 'if (preview.bytes.size() >= PreviewLimit)'),
    ):
        s = one(s, old_size_test, new_size_test, 'strict preview storage limit')
    s = one(s, 'if (original.bytes.size() > OriginalLimit)',
            'if (original.bytes.size() >= OriginalLimit)',
            "strict original size cutoff")
    s = one(s,
        '"Original exceeds 100 MiB even after verified lossless attempts; no quality reduction applied"',
        '"Original is 50 MiB or larger after verified lossless attempts; original pixels and quality were preserved"',
        "50 MiB original error text")
    s = one(s,
        'inline Result process(const QString &sourcePath, const QString &targetDir,\n                      int maxEdge, bool downscale) {',
        'inline Result process(const QString &sourcePath, const QString &targetDir,\n                      int maxWidth, int maxHeight, bool downscale) {',
        "process size parameters")
    s = one(s,
        'BlobCandidate preview = choosePreview(input, bytes, suffix, maxEdge, downscale, pw, ph);',
        'BlobCandidate preview = choosePreview(input, bytes, suffix, maxWidth, maxHeight, downscale, pw, ph);',
        "process passes 2D bounds")
    s = one(s,
        'int maxEdge, bool downscale, const std::shared_ptr<std::atomic_bool> &cancel)',
        'int maxWidth, int maxHeight, bool downscale, const std::shared_ptr<std::atomic_bool> &cancel)',
        "batch signature")
    s = one(s,
        'Result row = process(file, outDir, maxEdge, downscale);',
        'Result row = process(file, outDir, maxWidth, maxHeight, downscale);',
        "batch calls process")
    s = one(s,
        'inline void start(QWidget *parent, const QStringList &files, const QString &targetDir,\n                  int maxEdge, bool downscale) {',
        'inline void start(QWidget *parent, const QStringList &files, const QString &targetDir,\n                  int maxWidth, int maxHeight, bool downscale) {',
        "start size parameters")
    s = one(s,
        'watcher->setFuture(QtConcurrent::run([files, targetDir, maxEdge, downscale, cancel]() {\n        return batch(files, targetDir, maxEdge, downscale, cancel);',
        'watcher->setFuture(QtConcurrent::run([files, targetDir, maxWidth, maxHeight, downscale, cancel]() {\n        return batch(files, targetDir, maxWidth, maxHeight, downscale, cancel);',
        "async batch dimensions")
    return s


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd(), help='Converseen project root')
    p.add_argument('--apply', action='store_true', help='Back up and apply after source validation')
    opts = p.parse_args()
    root = opts.project.expanduser().resolve()
    cpp = root / 'src/mainwindowimpl.cpp'
    hdr = root / 'src/pixelshroom_upload_optimizer.h'
    try:
        if not (root / 'CMakeLists.txt').is_file():
            raise ValueError('No CMakeLists.txt at project root.')
        originals = {path: path.read_text(encoding='utf-8-sig') for path in [cpp, hdr]}
        changes = {cpp: transform_main(originals[cpp]),
                   hdr: transform_optimizer(originals[hdr])}
        print('PHASE 19 SOURCE CHECK PASSED')
        print('  Modify src/mainwindowimpl.cpp')
        print('  Modify src/pixelshroom_upload_optimizer.h')
        print('  Keep original-pixel integrity and metadata checks')
        print('  No changes to image converter, DPI, build files or installer')
        if not opts.apply:
            print('DRY RUN PASSED. Files unchanged. Run again with --apply to patch.')
            return 0
        backup = root / 'phase19-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        for path in originals:
            target = backup / path.relative_to(root)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)
        exe = root / 'build-portable/converseen.exe'
        if exe.is_file():
            shutil.copy2(exe, backup / 'converseen.exe')
        installed: list[Path] = []
        try:
            for path, after in changes.items():
                temp = path.with_name(path.name + '.phase19.tmp')
                temp.write_text(after, encoding='utf-8', newline='\n')
                temp.replace(path)
                installed.append(path)
        except Exception:
            for path in installed:
                shutil.copy2(backup / path.relative_to(root), path)
            raise
        print('APPLIED. Backup:', backup)
        print('Rebuild using MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        print('Test a copied exe; keep your stable installed application unchanged.')
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
