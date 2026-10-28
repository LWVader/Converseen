#!/usr/bin/env python3
"""Pixel Shroom Studio - conservative Converseen quick-print patch.

Targets the current Converseen main branch (Qt 6, ImageMagick 7), without changing
main.cpp, the existing .ui file, or CMake settings. Run in the cloned repo.

Usage:
    py -3 pixel_shroom_converseen_upgrade.py          # validate / preview
    py -3 pixel_shroom_converseen_upgrade.py --apply  # backup and modify
"""
from __future__ import annotations
import argparse
import datetime as dt
import pathlib
import shutil
import sys

TARGETS = [
    pathlib.Path('src/mainwindowimpl.cpp'),
    pathlib.Path('src/mainwindowimpl.h'),
    pathlib.Path('src/converter.cpp'),
    pathlib.Path('src/converter.h'),
]


def substitute(s: str, old: str, new: str, file: pathlib.Path, label: str) -> str:
    count = s.count(old)
    if count != 1:
        raise ValueError(f'{file}: expected one anchor for {label}; found {count}. No files were changed.')
    return s.replace(old, new, 1)


def patch_main_h(s: str, file: pathlib.Path) -> str:
    s = substitute(s, '    void loadOptions();',
                   '    void loadOptions();\n    void setupPixelShroomControls();', file, 'setup method')
    s = substitute(s, '    IMFilterType m_resamplingFilter;',
                   '    IMFilterType m_resamplingFilter;\n\n'
                   '    // Pixel Shroom opt-in enhancements (default: no behavior change).\n'
                   '    bool m_psOverrideQuality = false;\n'
                   '    int m_psQuality = 95;\n'
                   '    double m_psSmoothSigma = 0.0;\n'
                   '    double m_psSharpenSigma = 0.0;', file, 'enhancement fields')
    return s


def patch_converter_h(s: str, file: pathlib.Path) -> str:
    s = substitute(s, '    void setResamplingFilter(IMFilterType resamplingFilter);',
                   '    void setResamplingFilter(IMFilterType resamplingFilter);\n'
                   '    void setEnhancements(double smoothSigma, double sharpenSigma);', file, 'enhancement setter')
    s = substitute(s, '    IMFilterType m_resamplingFilter;',
                   '    IMFilterType m_resamplingFilter;\n'
                   '    double m_psSmoothSigma = 0.0;\n'
                   '    double m_psSharpenSigma = 0.0;', file, 'enhancement state')
    return s


def patch_converter_cpp(s: str, file: pathlib.Path) -> str:
    s = substitute(s, '    m_flip = false;\n}',
                   '    m_flip = false;\n'
                   '    m_psSmoothSigma = 0.0;\n'
                   '    m_psSharpenSigma = 0.0;\n}', file, 'reset enhancements')
    s = substitute(s, 'void Converter::setMagickDefines(const QList<MagickDefine> &magickDefines)',
                   '''void Converter::setEnhancements(double smoothSigma, double sharpenSigma)
{
    m_psSmoothSigma = smoothSigma > 0.0 ? smoothSigma : 0.0;
    m_psSharpenSigma = sharpenSigma > 0.0 ? sharpenSigma : 0.0;
}

void Converter::setMagickDefines(const QList<MagickDefine> &magickDefines)''', file, 'setter implementation')
    s = substitute(s, '        out = QDir::toNativeSeparators(out);',
                   '''        // Pixel Shroom: smoothing first, optional sharpening after resize.
        // These operations default to disabled and never change input files.
        try {
            if (m_psSmoothSigma > 0.0)
                my_image.blur(0.0, m_psSmoothSigma);
            if (m_psSharpenSigma > 0.0)
                my_image.sharpen(0.0, m_psSharpenSigma);
        } catch (const Magick::Exception &error) {
            m_conv_status = -1;
            emit errorMessage(tr("Enhancement failed: %1").arg(QString::fromStdString(error.what())));
            return;
        }

        out = QDir::toNativeSeparators(out);''', file, 'processing order')
    s = substitute(s, '            //bgImg.resolutionUnits(PixelsPerInchResolution);',
                   '            bgImg.resolutionUnits(Magick::PixelsPerInchResolution);', file, 'background DPI unit')
    s = substitute(s, '        //my_image.resolutionUnits(PixelsPerInchResolution);',
                   '        my_image.resolutionUnits(Magick::PixelsPerInchResolution);', file, 'output DPI unit')
    return s


PANEL_CODE = r'''void MainWindowImpl::setupPixelShroomControls()
{
    // Small, optional quick-control panel. Existing UI and advanced settings remain intact.
    auto *panel = new QGroupBox(tr("Pixel Shroom | Quick Print & Quality"), centralwidget);
    auto *stack = new QVBoxLayout(panel);
    auto *top = new QHBoxLayout();
    auto *bottom = new QHBoxLayout();
    stack->addLayout(top);
    stack->addLayout(bottom);

    auto *preset = new QComboBox(panel);
    preset->setMinimumWidth(210);
    preset->setToolTip(tr("Choose a target size. Keeps original aspect ratio; never crops."));
    preset->addItem(tr("Custom size (existing controls)"), QSize());
    preset->addItem(tr("16 x 16 in | 4800 x 4800"), QSize(4800, 4800));
    preset->addItem(tr("16 x 20 in | 4800 x 6000"), QSize(4800, 6000));
    preset->addItem(tr("24 x 24 in | 7200 x 7200"), QSize(7200, 7200));
    preset->addItem(tr("24 x 30 in | 7200 x 9000"), QSize(7200, 9000));
    preset->addItem(tr("Web | 600 x 600"), QSize(600, 600));
    preset->addItem(tr("Web | 2048 x 2048"), QSize(2048, 2048));
    top->addWidget(new QLabel(tr("Preset:"), panel));
    top->addWidget(preset, 1);

    auto *advanced = new QPushButton(tr("Advanced format / resampling..."), panel);
    top->addWidget(advanced);
    connect(advanced, &QPushButton::clicked, this, [this]() { setQuality(); });

    connect(preset, QOverload<int>::of(&QComboBox::currentIndexChanged), this,
            [this, preset](int index) {
        if (index < 1)
            return;
        const QSize pixels = preset->itemData(index).toSize();
        if (!pixels.isValid())
            return;
        comboResizeValues->setCurrentText("px"); // This resets fields: do it first.
        groupDimensions->setChecked(true);
        checkRelative->setChecked(true);          // Fits image to box without cropping.
        spin_geoWidth->setValue(pixels.width());
        spin_geoHeight->setValue(pixels.height());
        if (index <= 4) {                         // Print presets only.
            groupResolution->setChecked(true);
            spin_resX->setValue(300);
            spin_resY->setValue(300);
        } else {
            groupResolution->setChecked(false);
        }
        showNewSizePreview();
        statusBar()->showMessage(tr("Preset applied. Different aspect ratios fit within the box without cropping."), 6000);
    });

    auto *overrideQuality = new QCheckBox(tr("Override JPEG/WebP quality"), panel);
    auto *quality = new QSpinBox(panel);
    quality->setRange(1, 100);
    quality->setValue(m_psQuality);
    quality->setEnabled(false);
    quality->setToolTip(tr("1-100; affects lossy JPEG and WebP. PNG still uses its own settings."));
    bottom->addWidget(overrideQuality);
    bottom->addWidget(quality);
    connect(overrideQuality, &QCheckBox::toggled, this, [this, quality](bool checked) {
        m_psOverrideQuality = checked;
        quality->setEnabled(checked);
    });
    connect(quality, QOverload<int>::of(&QSpinBox::valueChanged), this,
            [this](int value) { m_psQuality = value; });

    auto makeSigma = [panel, bottom](const QString &name, const QString &hint) {
        auto *spin = new QDoubleSpinBox(panel);
        spin->setRange(0.0, 2.0);
        spin->setDecimals(1);
        spin->setSingleStep(0.1);
        spin->setValue(0.0);
        spin->setToolTip(hint);
        bottom->addWidget(new QLabel(name, panel));
        bottom->addWidget(spin);
        return spin;
    };
    auto *smooth = makeSigma(tr("Smooth:"), tr("Gaussian blur sigma. 0 = off; try 0.2-0.4 cautiously."));
    auto *sharpen = makeSigma(tr("Sharpen:"), tr("Sharpen sigma. 0 = off; try 0.3-0.7 cautiously."));
    connect(smooth, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
            [this](double value) { m_psSmoothSigma = value; });
    connect(sharpen, QOverload<double>::of(&QDoubleSpinBox::valueChanged), this,
            [this](double value) { m_psSharpenSigma = value; });
    bottom->addStretch();

    // New panel is above the image list. No changes to Qt Designer .ui files.
    verticalLayout_20->insertWidget(0, panel);
}

'''


def patch_main_cpp(s: str, file: pathlib.Path) -> str:
    s = substitute(s, '#include <QColorDialog>',
                   '''#include <QColorDialog>
#include <QGroupBox>
#include <QHBoxLayout>
#include <QVBoxLayout>
#include <QComboBox>
#include <QCheckBox>
#include <QSpinBox>
#include <QDoubleSpinBox>
#include <QLabel>
#include <QPushButton>
#include <QSize>''', file, 'Qt imports')
    s = substitute(s, '    loadOptions();\n\n    resetDisplays();',
                   '    loadOptions();\n    setupPixelShroomControls();\n\n    resetDisplays();', file, 'panel startup')
    s = substitute(s, 'MainWindowImpl::~MainWindowImpl()', PANEL_CODE + 'MainWindowImpl::~MainWindowImpl()',
                   file, 'panel body')
    s = substitute(s, '    convertThread->setResamplingFilter(m_resamplingFilter);',
                   '    convertThread->setResamplingFilter(m_resamplingFilter);\n'
                   '    convertThread->setEnhancements(m_psSmoothSigma, m_psSharpenSigma);', file, 'conversion parameters')
    s = substitute(s, '''if ((groupResolution->isChecked()) && ((m_xResolution != spin_resX->value()) || (m_yResolution != spin_resY->value()))) {''',
                   'if (groupResolution->isChecked()) {', file, 'always apply requested DPI')
    s = substitute(s, '(m_isWebPLosslessCompression) ? "true" : "false"',
                   '(m_psOverrideQuality ? "false" : (m_isWebPLosslessCompression ? "true" : "false"))',
                   file, 'lossy WebP quality override')
    s = substitute(s, '        convertThread->setInputPicture(inputFilename);',
                   '''        if (m_psOverrideQuality && (out_format == "jpg" || out_format == "jpeg" || out_format == "webp"))
            quality = m_psQuality;

        convertThread->setInputPicture(inputFilename);''', file, 'quality override')
    return s


PATCHERS = {
    TARGETS[0]: patch_main_cpp,
    TARGETS[1]: patch_main_h,
    TARGETS[2]: patch_converter_cpp,
    TARGETS[3]: patch_converter_h,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', type=pathlib.Path, default=pathlib.Path.cwd(), help='Converseen repo directory')
    ap.add_argument('--apply', action='store_true', help='Create backup and modify files')
    args = ap.parse_args()
    root = args.project.resolve()
    build = root / 'build'
    if not (root / 'CMakeLists.txt').is_file():
        print(f'ERROR: {root} does not look like the Converseen repo (no CMakeLists.txt).', file=sys.stderr)
        return 2
    if not (build / 'converseen.exe').is_file() and args.apply:
        print('ERROR: build/converseen.exe not found. Refusing to modify project without a working exe to back up.', file=sys.stderr)
        return 2

    staged: dict[pathlib.Path, str] = {}
    try:
        for rel in TARGETS:
            p = root / rel
            old = p.read_text(encoding='utf-8-sig')
            if 'Pixel Shroom | Quick Print & Quality' in old or 'm_psSmoothSigma' in old:
                raise ValueError(f'{p}: appears already patched; stopping to avoid double application.')
            new = PATCHERS[rel](old, rel)
            staged[rel] = new
            print(f'Validated: {rel}')
    except (ValueError, FileNotFoundError, UnicodeError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2

    if not args.apply:
        print('\nDRY RUN PASSED: no changes made. To preserve the working build and apply:')
        print('  py -3 pixel_shroom_converseen_upgrade.py --apply')
        return 0

    name = f'{root.name}-working-backup-{dt.datetime.now().strftime("%Y%m%d-%H%M%S")}'
    backup = root.parent / name
    if backup.exists():
        print(f'ERROR: backup already exists: {backup}', file=sys.stderr)
        return 2
    try:
        backup.mkdir()
        for rel in TARGETS:
            dest = backup / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(root / rel, dest)
        # Preserve all generated artifacts/resources of the working build, not just the exe.
        shutil.copytree(build, backup / 'build')
        (backup / 'ROLLBACK.txt').write_text(
            'BACKUP OF WORKING CONVERSEEN (created before Pixel Shroom upgrade)\n\n'
            f'Original project: {root}\n\n'
            'If the new build fails, restore the four .cpp/.h files from this backup\n'
            'into the matching paths of the original project, then run:\n'
            '  cmake --build build --parallel 4\n\n'
            'The original full build directory is also preserved here.\n', encoding='utf-8')
        for rel, new in staged.items():
            (root / rel).write_text(new, encoding='utf-8', newline='\n')
    except Exception as exc:
        print(f'ERROR: patch/back-up failed: {exc}', file=sys.stderr)
        print('Check the backup and restore any changed files before rebuilding.', file=sys.stderr)
        return 3
    print('\nPATCH APPLIED. Working build backed up at:')
    print(f'  {backup}')
    print('Next commands (inside MSYS2 UCRT64):')
    print('  cmake --build build --parallel 4')
    print('  ./build/converseen.exe')
    print('Do not delete the backup until you verify conversions.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
