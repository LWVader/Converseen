#!/usr/bin/env python3
"""Pixel Shroom Converseen Phase 7 — one set of controls + one live preview.

Dry-run by default; run with --apply only after a successful dry run.
Requires working Phase 6 source. Does not alter converter, DPI or CMake files.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

SOURCE = Path('src/mainwindowimpl.cpp')
PREVIEW_HEADER = Path('src/pixelshroom_phase7.h')
PHASE6_HEADER = Path('src/pixelshroom_phase6.h')
MARKER = 'Pixel Shroom Phase 7: unified output settings and modeless live preview.'

COMPRESS = r'''    // Pixel Shroom Phase 7: unified output settings and modeless live preview.
    // For JPEG, PNG and WebP, this is the single visible settings surface.
    // Other formats keep Converseen's original dialog for specialist settings.
    auto *compressTab = new QWidget(tabs);
    compressTab->setObjectName("psCompressTab");
    auto *compressGrid = new QGridLayout(compressTab);
    compressGrid->setContentsMargins(8, 12, 8, 10);
    compressGrid->setHorizontalSpacing(14);
    compressGrid->setVerticalSpacing(10);
    auto *formatLabel = new QLabel(tr("Image format: choose it in 'Convert to' below"), compressTab);
    formatLabel->setWordWrap(true);
    compressGrid->addWidget(formatLabel, 0, 0, 1, 3);

    auto *overrideQuality = new QCheckBox(tr("Set custom JPEG / WebP quality"), compressTab);
    overrideQuality->setObjectName("psOverrideQuality");
    overrideQuality->setChecked(m_psOverrideQuality);
    compressGrid->addWidget(overrideQuality, 1, 0, 1, 3);
    auto *qualityLabel = new QLabel(tr("Quality"), compressTab);
    auto *qualitySlider = new QSlider(Qt::Horizontal, compressTab);
    auto *qualityNumber = new QSpinBox(compressTab);
    qualityNumber->setObjectName("psQualityNumber");
    qualitySlider->setRange(1, 100);
    qualityNumber->setRange(1, 100);
    qualityNumber->setMinimumWidth(75);
    qualitySlider->setValue(m_psQuality);
    qualityNumber->setValue(m_psQuality);
    compressGrid->addWidget(qualityLabel, 2, 0);
    compressGrid->addWidget(qualitySlider, 2, 1);
    compressGrid->addWidget(qualityNumber, 2, 2);
    auto *qualityHint = new QLabel(tr("Higher quality keeps more detail but creates larger files."), compressTab);
    qualityHint->setWordWrap(true);
    compressGrid->addWidget(qualityHint, 3, 0, 1, 3);

    auto *pngLabel = new QLabel(tr("PNG compression"), compressTab);
    auto *pngSlider = new QSlider(Qt::Horizontal, compressTab);
    auto *pngNumber = new QSpinBox(compressTab);
    pngSlider->setRange(0, 9);
    pngNumber->setRange(0, 9);
    pngSlider->setValue(qBound(0, m_pngQuality, 9));
    pngNumber->setValue(qBound(0, m_pngQuality, 9));
    compressGrid->addWidget(pngLabel, 4, 0);
    compressGrid->addWidget(pngSlider, 4, 1);
    compressGrid->addWidget(pngNumber, 4, 2);
    auto *pngHint = new QLabel(tr("PNG is lossless. 0 = fast, 9 = stronger compression; image detail stays the same."), compressTab);
    pngHint->setWordWrap(true);
    compressGrid->addWidget(pngHint, 5, 0, 1, 3);

    auto *webpLossless = new QCheckBox(tr("WebP lossless (preserve all pixels)"), compressTab);
    webpLossless->setChecked(m_isWebPLosslessCompression);
    compressGrid->addWidget(webpLossless, 6, 0, 1, 3);
    auto *effortLabel = new QLabel(tr("WebP compression effort"), compressTab);
    auto *effortSlider = new QSlider(Qt::Horizontal, compressTab);
    auto *effortNumber = new QSpinBox(compressTab);
    effortSlider->setRange(0, 6);
    effortNumber->setRange(0, 6);
    effortSlider->setValue(qBound(0, m_webPCompression, 6));
    effortNumber->setValue(qBound(0, m_webPCompression, 6));
    compressGrid->addWidget(effortLabel, 7, 0);
    compressGrid->addWidget(effortSlider, 7, 1);
    compressGrid->addWidget(effortNumber, 7, 2);
    auto *effortHint = new QLabel(tr("Higher effort may create smaller WebP files but takes longer."), compressTab);
    effortHint->setWordWrap(true);
    compressGrid->addWidget(effortHint, 8, 0, 1, 3);
    auto *dithering = new QCheckBox(tr("WebP dithering / preprocessing"), compressTab);
    dithering->setChecked(m_iskWebPDithering);
    compressGrid->addWidget(dithering, 9, 0, 1, 3);
    auto *metadata = new QCheckBox(tr("Remove source metadata (includes profile information)"), compressTab);
    metadata->setChecked(m_removeMetadata);
    metadata->setToolTip(tr("Removes source metadata. Verify the final DPI and color profile for print exports."));
    compressGrid->addWidget(metadata, 10, 0, 1, 3);
    auto *otherHint = new QLabel(tr("For this uncommon output format, use the 'Image settings' button below."), compressTab);
    otherHint->setWordWrap(true);
    compressGrid->addWidget(otherHint, 11, 0, 1, 3);
    compressGrid->setColumnStretch(1, 1);
    tabs->addTab(compressTab, tr("Compress"));

    connect(qualitySlider, &QSlider::valueChanged, qualityNumber, &QSpinBox::setValue);
    connect(qualityNumber, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, qualitySlider](int value) {
        qualitySlider->setValue(value);
        m_psQuality = value;
    });
    connect(overrideQuality, &QCheckBox::toggled, this, [this](bool on) {
        m_psOverrideQuality = on;
    });
    connect(pngSlider, &QSlider::valueChanged, pngNumber, &QSpinBox::setValue);
    connect(pngNumber, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, pngSlider](int value) {
        pngSlider->setValue(value);
        m_pngQuality = value;
        IniSettings::setPngQuality(value);
    });
    connect(effortSlider, &QSlider::valueChanged, effortNumber, &QSpinBox::setValue);
    connect(effortNumber, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this, effortSlider](int value) {
        effortSlider->setValue(value);
        m_webPCompression = value;
        IniSettings::setWebPCompression(value);
    });
    connect(dithering, &QCheckBox::toggled, this, [this](bool on) {
        m_iskWebPDithering = on;
        IniSettings::setIskWebPDithering(on);
    });
    connect(metadata, &QCheckBox::toggled, this, [this](bool on) {
        m_removeMetadata = on;
        IniSettings::setIsRemoveMetadata(on);
    });

    // The Phase 1 converter forces lossy WebP when overriding quality;
    // keep the two controls mutually exclusive so the UI is always truthful.
    connect(webpLossless, &QCheckBox::toggled, this, [this, overrideQuality](bool on) {
        m_isWebPLosslessCompression = on;
        IniSettings::setIsWebPLosslessCompression(on);
        if (on) overrideQuality->setChecked(false);
    });
    connect(overrideQuality, &QCheckBox::toggled, this, [webpLossless](bool on) {
        if (on && webpLossless->isVisible() && webpLossless->isChecked())
            webpLossless->setChecked(false);
    });

    // One codec-specific UI. Keep native settings for OTHER formats only.
    auto selectedCodec = [this]() -> QString {
        QString codec;
        if (comboWFormats->currentIndex() == 0) {
            const int row = treeWidget->currentIndex().row();
            if (row >= 0 && row < iAList->size())
                codec = QFileInfo(iAList->at(row).completeFileName).suffix().toLower();
        } else {
            codec = comboWFormats->currentText().split(" - ").first().trimmed().toLower();
        }
        if (codec == "jpg" || codec == "jfif") codec = "jpeg";
        if (codec == "png24" || codec == "png32" || codec == "png8") codec = "png";
        return codec;
    };
    auto updateCodecUi = [this, selectedCodec, formatLabel, overrideQuality, qualityLabel,
                          qualitySlider, qualityNumber, qualityHint, pngLabel, pngSlider,
                          pngNumber, pngHint, webpLossless, effortLabel, effortSlider,
                          effortNumber, effortHint, dithering, metadata, otherHint]() {
        const QString codec = selectedCodec();
        const bool jpeg = codec == "jpeg";
        const bool png = codec == "png";
        const bool webp = codec == "webp";
        const bool managed = jpeg || png || webp;
        // A previous JPEG override must not silently switch a lossless WebP preset to lossy.
        if (webp && webpLossless->isChecked() && overrideQuality->isChecked())
            overrideQuality->setChecked(false);
        formatLabel->setText(managed
          ? QObject::tr("%1 output — controls below apply to the entire batch.").arg(codec.toUpper())
          : QObject::tr("Choose JPEG, PNG or WebP in 'Convert to' for simple settings."));
        overrideQuality->setVisible(jpeg || webp);
        const bool lossyQuality = (jpeg || webp) && !(webp && webpLossless->isChecked());
        qualityLabel->setVisible(lossyQuality);
        qualitySlider->setVisible(lossyQuality);
        qualityNumber->setVisible(lossyQuality);
        qualityHint->setVisible(lossyQuality);
        qualitySlider->setEnabled(overrideQuality->isChecked());
        qualityNumber->setEnabled(overrideQuality->isChecked());
        pngLabel->setVisible(png);
        pngSlider->setVisible(png);
        pngNumber->setVisible(png);
        pngHint->setVisible(png);
        webpLossless->setVisible(webp);
        effortLabel->setVisible(webp);
        effortSlider->setVisible(webp);
        effortNumber->setVisible(webp);
        effortHint->setVisible(webp);
        dithering->setVisible(webp);
        metadata->setVisible(managed);
        otherHint->setVisible(!managed);
        btnFormatOptions->setVisible(!managed);
        btnFormatOptions->setToolTip(QObject::tr("Advanced image settings for additional formats"));
    };
    connect(comboWFormats, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [updateCodecUi](int) { updateCodecUi(); });
    connect(treeWidget, &QTreeWidget::itemSelectionChanged, this, updateCodecUi);
    connect(overrideQuality, &QCheckBox::toggled, this, [updateCodecUi](bool) { updateCodecUi(); });
    connect(webpLossless, &QCheckBox::toggled, this, [updateCodecUi](bool) { updateCodecUi(); });
    updateCodecUi();

'''

PREVIEW = r'''    // Phase 7: Live Preview has NO extra adjustment controls. Main Studio is
    // the source of truth; the separate window updates whenever Studio changes.
    auto refreshPreview = [this, width, height, keepAspect, selectedCodec]() {
        auto *window = findChild<PixelShroomPhase7::PreviewWindow*>("psStudioLivePreview");
        if (!window) return;
        const QString codec = selectedCodec();
        const int nativeQuality = codec == "webp" ? m_webPQuality : m_jpgQuality;
        const int selectedQuality = m_psOverrideQuality ? m_psQuality : nativeQuality;
        window->setParameters(QSize(width->value(), height->value()), keepAspect->isChecked(),
                              codec, m_psOverrideQuality, qBound(1, selectedQuality, 100),
                              m_psSmoothSigma, m_psSharpenSigma, m_isWebPLosslessCompression,
                              m_pngQuality, m_webPCompression, m_iskWebPDithering);
    };
    connect(previewButton, &QPushButton::clicked, this,
            [this, refreshPreview]() {
        const int row = treeWidget->currentIndex().row();
        if (row < 0 || row >= iAList->size()) {
            QMessageBox::information(this, tr("Choose an image"),
                                     tr("Select an imported image first."));
            return;
        }
        const QString source = QFileInfo(iAList->at(row).completeFileName).absoluteFilePath();
        if (!QFileInfo(source).isFile()) {
            QMessageBox::warning(this, tr("Missing source"), tr("The selected original no longer exists:\n%1").arg(source));
            return;
        }
        auto *window = findChild<PixelShroomPhase7::PreviewWindow*>("psStudioLivePreview");
        if (!window) {
            window = new PixelShroomPhase7::PreviewWindow(this);
            window->setObjectName("psStudioLivePreview");
            window->setAttribute(Qt::WA_DeleteOnClose);
        }
        if (!window->openSource(source)) {
            window->close();
            return;
        }
        refreshPreview();
        window->show();
        window->raise();
        window->activateWindow();
    });
    // Keep preview in sync with all user-visible Studio settings.
    auto whenChanged = [refreshPreview]() { refreshPreview(); };
    connect(width, QOverload<int>::of(&QSpinBox::valueChanged), this, [whenChanged](int) { whenChanged(); });
    connect(height, QOverload<int>::of(&QSpinBox::valueChanged), this, [whenChanged](int) { whenChanged(); });
    connect(keepAspect, &QCheckBox::toggled, this, [whenChanged](bool) { whenChanged(); });
    connect(comboWFormats, QOverload<int>::of(&QComboBox::currentIndexChanged),
            this, [whenChanged](int) { whenChanged(); });
    connect(qualityNumber, QOverload<int>::of(&QSpinBox::valueChanged), this, [whenChanged](int) { whenChanged(); });
    connect(overrideQuality, &QCheckBox::toggled, this, [whenChanged](bool) { whenChanged(); });
    connect(webpLossless, &QCheckBox::toggled, this, [whenChanged](bool) { whenChanged(); });
    connect(pngNumber, QOverload<int>::of(&QSpinBox::valueChanged), this, [whenChanged](int) { whenChanged(); });
    connect(effortNumber, QOverload<int>::of(&QSpinBox::valueChanged), this, [whenChanged](int) { whenChanged(); });
    connect(dithering, &QCheckBox::toggled, this, [whenChanged](bool) { whenChanged(); });
    connect(treeWidget, &QTreeWidget::itemSelectionChanged, this, [this, refreshPreview]() {
        auto *window = findChild<PixelShroomPhase7::PreviewWindow*>("psStudioLivePreview");
        if (!window) return;
        const int row = treeWidget->currentIndex().row();
        if (row >= 0 && row < iAList->size() &&
            window->openSource(QFileInfo(iAList->at(row).completeFileName).absoluteFilePath()))
            refreshPreview();
    });
    if (auto *smoothWidget = findChild<QDoubleSpinBox*>("psSmoothNumber"))
        connect(smoothWidget, QOverload<double>::of(&QDoubleSpinBox::valueChanged),
                this, [whenChanged](double) { whenChanged(); });
    if (auto *sharpenWidget = findChild<QDoubleSpinBox*>("psSharpenNumber"))
        connect(sharpenWidget, QOverload<double>::of(&QDoubleSpinBox::valueChanged),
                this, [whenChanged](double) { whenChanged(); });

'''


def once(text: str, old: str, new: str, name: str) -> str:
    number = text.count(old)
    if number != 1:
        raise ValueError(f'{name}: expected 1 source anchor, found {number}; stopping safely')
    return text.replace(old, new, 1)


def patch(text: str) -> str:
    for token in ('Pixel Shroom Phase 6: synchronized zoom and live quality preview.',
                  'Pixel Shroom Phase 5: use the visible DPI controls for EVERY batch.',
                  'void MainWindowImpl::setupPixelShroomControls()',
                  'auto *compressTab = new QWidget(tabs);',
                  'auto *previewButton = new QPushButton(',
                  'auto *collapse = new QToolButton(panel);',
                  'btnFormatOptions'):
        if token not in text:
            raise ValueError(f'Phase 6 source expected, missing: {token!r}')
    if MARKER in text:
        raise ValueError('Phase 7 is already installed')
    text = once(text, '#include "pixelshroom_phase6.h"',
                '#include "pixelshroom_phase6.h"\n#include "pixelshroom_phase7.h"', 'header inclusion')

    a = text.find('    // Compress tab: Squoosh-style quality slider + exact value, opt-in.')
    b = text.find('    // Enhance tab: independent subtle blur / detail sharpening, both off by default.', a)
    if a < 0 or b < a:
        raise ValueError('Phase 6 Compress block not found')
    old_block = text[a:b]
    if 'setQuality();' not in old_block or 'auto *qualityNumber' not in old_block:
        raise ValueError('Unexpected native quality wiring; no files changed')
    text = text[:a] + COMPRESS + text[b:]

    a = text.find('    // Image Studio controls remain authoritative. Only commit preview changes on Apply.')
    b = text.find('    // Avoid the compressed single-row toolbar seen in Phase 1.', a)
    if a < 0 or b < a or 'PixelShroomPhase6::livePreview' not in text[a:b]:
        raise ValueError('Phase 6 Live Preview block not found')
    text = text[:a] + PREVIEW + text[b:]
    # Dialog starts from an existing user-selected output directory; normalize
    # Windows paths and fall back to the original folder if that folder is gone.
    old = ('        const QString folder = checkSameDir->isChecked()\n'
           '            ? QFileInfo(originalPath).absolutePath() : lineDirectory->text();')
    new = ('        QString folder = checkSameDir->isChecked()\n'
           '            ? QFileInfo(originalPath).absolutePath() : lineDirectory->text();\n'
           '        folder = QDir::fromNativeSeparators(folder.trimmed());\n'
           '        if (!QDir(folder).exists()) folder = QFileInfo(originalPath).absolutePath();')
    text = once(text, old, new, 'compare-output initial folder')
    return text


def main() -> int:
    arg = argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--project', type=Path, default=Path.cwd())
    arg.add_argument('--apply', action='store_true')
    args = arg.parse_args()
    root = args.project.expanduser().resolve()
    target = root / SOURCE
    header = root / PREVIEW_HEADER
    exe = root / 'build/converseen.exe'
    helper = Path(__file__).resolve().parent / 'pixelshroom_phase7.h'
    requirements = (root / 'CMakeLists.txt', target, root / PHASE6_HEADER, exe, helper)
    missing = [str(p) for p in requirements if not p.is_file()]
    if missing or header.exists():
        print('ERROR: Required files missing or Phase 7 header already exists:',
              *missing, sep='\n  ', file=sys.stderr)
        if header.exists(): print(f'  Phase 7 header already exists: {header}', file=sys.stderr)
        return 2
    try:
        current = target.read_text(encoding='utf-8-sig')
        revised = patch(current)
        helper_text = helper.read_text(encoding='utf-8-sig')
        if 'class PreviewWindow : public QDialog' not in helper_text:
            raise ValueError('Invalid Phase 7 preview helper')
    except (ValueError, UnicodeError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2
    print('PHASE 7 SOURCE CHECK PASSED — paths and Phase 6 anchors verified.')
    print('Repository: ', root)
    print('Edit: ', target)
    print('Add: ', header)
    print('Preserved: converter, DPI engine, Phase 6 comparison, main.cpp and status dialog')
    if not args.apply:
        print('DRY RUN PASSED. Nothing changed; rerun with --apply.')
        return 0
    backup = root.parent / f'{root.name}-phase7-working-backup-{datetime.now():%Y%m%d-%H%M%S}'
    if backup.exists():
        print('ERROR: Backup directory exists; retry.', file=sys.stderr)
        return 3
    tmp = target.with_name(target.name + '.phase7-tmp')
    try:
        (backup / 'src').mkdir(parents=True)
        shutil.copy2(target, backup / SOURCE)
        shutil.copy2(root / PHASE6_HEADER, backup / PHASE6_HEADER)
        shutil.copy2(exe, backup / 'converseen.exe')
        (backup / 'ROLLBACK.txt').write_text(
            'Close Converseen. Restore backup src/mainwindowimpl.cpp to project src/.\n'
            'Delete newly added src/pixelshroom_phase7.h.\n'
            'Rebuild inside MSYS2 UCRT64: cmake --build build --parallel 4\n'
            'Or restore backup converseen.exe into project build/ for the previous executable.\n',
            encoding='utf-8')
        tmp.write_text(revised, encoding='utf-8', newline='\n')
        tmp.replace(target)
        header.write_text(helper_text, encoding='utf-8', newline='\n')
    except Exception as exc:
        print(f'ERROR applying patch: {exc}', file=sys.stderr)
        tmp.unlink(missing_ok=True)
        saved = backup / SOURCE
        if saved.is_file(): shutil.copy2(saved, target)
        header.unlink(missing_ok=True)
        return 3
    print('PHASE 7 APPLIED. Backup:', backup)
    print('Build and run in MSYS2 UCRT64:')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
