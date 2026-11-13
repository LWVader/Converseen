#!/usr/bin/env python3
"""Pixel Shroom Image Studio — Phase 11 upload presets + glass UI.

Dry run by default. --apply saves timestamped backups and patches only
src/mainwindowimpl.cpp, adding two headers under src/. No converter changes.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARK = 'Pixel Shroom Phase 11: upload-ready exports and premium glass UI.'
INCLUDES = '#include "pixelshroom_phase7.h"'
HEADING = '    heading->addWidget(title, 1);'
ENHANCE = '    tabs->addTab(enhanceTab, tr("Enhance"));'

UPLOAD_TAB = r'''    // Pixel Shroom Phase 11: upload-ready exports and premium glass UI.
    // A dedicated batch workflow; existing Convert / 300-DPI code is unchanged.
    auto *uploadTab = new QWidget(tabs);
    uploadTab->setObjectName("psUploadTab");
    auto *uploadLayout = new QVBoxLayout(uploadTab);
    uploadLayout->setContentsMargins(15, 15, 15, 12);
    uploadLayout->setSpacing(11);
    auto *uploadTitle = new QLabel(tr("Website upload • automatic lossless optimization"), uploadTab);
    QFont uploadFont = uploadTitle->font();
    uploadFont.setBold(true);
    uploadTitle->setFont(uploadFont);
    uploadLayout->addWidget(uploadTitle);
    auto *uploadExplanation = new QLabel(
        tr("PREVIEW: 10 MiB maximum. ORIGINAL: 100 MiB maximum. "
           "Originals retain their pixels and embedded print metadata. "
           "Previews use a lossless codec but can have fewer pixels."), uploadTab);
    uploadExplanation->setWordWrap(true);
    uploadLayout->addWidget(uploadExplanation);
    auto *uploadRow = new QHBoxLayout();
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
    uploadLayout->addLayout(uploadRow);
    auto *allowPreviewDownscale = new QCheckBox(
        tr("Reduce preview dimensions further only when needed to stay under 10 MiB"), uploadTab);
    allowPreviewDownscale->setChecked(true);
    uploadLayout->addWidget(allowPreviewDownscale);
    auto *uploadAction = new QPushButton(tr("Create upload-ready files for imported images"), uploadTab);
    uploadAction->setObjectName("psUploadAction");
    uploadAction->setMinimumHeight(38);
    uploadLayout->addWidget(uploadAction);
    auto *uploadHint = new QLabel(
        tr("Files are saved as __preview and __original pairs in the current output folder. "
           "The app never overwrites your original images. Oversized originals that cannot "
           "be reduced losslessly are reported rather than degraded."), uploadTab);
    uploadHint->setWordWrap(true);
    uploadLayout->addWidget(uploadHint);
    uploadLayout->addStretch(1);
    tabs->addTab(uploadTab, tr("Upload-ready"));
    connect(uploadAction, &QPushButton::clicked, this,
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
    });
'''

def replace_once(source: str, old: str, new: str, name: str) -> str:
    if source.count(old) != 1:
        raise ValueError(f'{name}: expected one source anchor, found {source.count(old)}')
    return source.replace(old, new, 1)


def transform(src: str) -> str:
    if MARK in src:
        raise ValueError('Phase 11 is already installed; no changes made')
    if 'Pixel Shroom Phase 7: unified output settings' not in src:
        raise ValueError('Expected the working Phase 7+ Image Studio source')
    src = replace_once(src, INCLUDES,
        INCLUDES + '\n#include "pixelshroom_glass_theme.h"\n#include "pixelshroom_upload_optimizer.h"\n#include <QApplication>',
        'phase7 include')
    opening = '    // Phase 2: Squoosh-inspired, accessible tabs; no changes to the batch engine.'
    src = replace_once(src, opening,
        '    // Phase 11: glass-inspired application theme; existing controls remain functional.\n'
        '    qApp->setStyleSheet(PixelShroomGlass::window());\n' + opening,
        'panel opening')
    start = '    panel->setStyleSheet(R"PSCSS('
    end = '    )PSCSS");'
    if src.count(start) != 1:
        raise ValueError('Image Studio panel style anchor not unique')
    first = src.index(start)
    last = src.find(end, first)
    if last < 0:
        raise ValueError('Image Studio panel style closing delimiter not found')
    src = src[:first] + '    panel->setStyleSheet(PixelShroomGlass::panel());' + src[last+len(end):]
    src = replace_once(src, ENHANCE, ENHANCE + '\n' + UPLOAD_TAB, 'Enhance tab')
    return src


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd())
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    root = args.project.resolve()
    source = root / 'src/mainwindowimpl.cpp'
    assets = [(Path(__file__).resolve().parent / 'pixelshroom_glass_theme.h',
               root / 'src/pixelshroom_glass_theme.h'),
              (Path(__file__).resolve().parent / 'pixelshroom_upload_optimizer.h',
               root / 'src/pixelshroom_upload_optimizer.h')]
    if not source.is_file():
        print(f'ERROR: Source not found: {source}'); return 1
    try:
        old = source.read_text(encoding='utf-8')
        new = transform(old)
        for local, target in assets:
            if not local.is_file():
                raise ValueError(f'Missing kit file {local.name}')
            if target.exists():
                if target.read_bytes() != local.read_bytes():
                    raise ValueError(f'{target} already exists with different contents; resolve manually')
            else:
                print('ADD', target.relative_to(root))
        print('MODIFY src/mainwindowimpl.cpp')
        print('PRESERVE converter.cpp, installer, CMake, main.cpp and build-portable')
        if not args.apply:
            print('DRY RUN PASSED — no source files changed. Use --apply to install.'); return 0
        backup = root / 'phase11-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        shutil.copy2(source, backup / 'mainwindowimpl.cpp')
        for local, target in assets:
            if not target.exists(): shutil.copy2(local, target)
        source.write_text(new, encoding='utf-8')
        print('APPLIED — backups:', backup)
        print('Build in MSYS2: cmake --build build-portable --parallel 4')
        print('Validate new features BEFORE updating your installer or GitHub release.')
        return 0
    except (OSError, ValueError, UnicodeError) as e:
        print('ERROR:', e); return 1

if __name__ == '__main__':
    sys.exit(main())
