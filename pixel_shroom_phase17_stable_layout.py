#!/usr/bin/env python3
"""Phase 17: stable Qt painting, separated editor/queue cards, refined glass toolbar.

Dry run by default; --apply backs up source before writing. Requires Phase 16.
Does not modify conversion, metadata/DPI, or the installer/distribution folder.
"""
from __future__ import annotations
import argparse
from datetime import datetime
from pathlib import Path
import shutil
import sys

MARK = '// Pixel Shroom Phase 17: stable compositing and separate image queue.'


def one(source: str, old: str, new: str, label: str) -> str:
    occurrences = source.count(old)
    if occurrences != 1:
        raise ValueError(f'{label}: expected exactly one anchor; found {occurrences}. Source unchanged.')
    return source.replace(old, new, 1)


def change_main(source: str) -> str:
    if MARK in source:
        raise ValueError('Phase 17 is already present; will not reapply.')
    if 'Pixel Shroom Phase 16: scrolling editor pages and balanced splitter.' not in source:
        raise ValueError('Phase 16 layout is required; no files modified.')
    if '    workspaceSplitter->addWidget(treeWidget);' not in source:
        raise ValueError('Cannot locate Phase 15/16 treeWidget splitter setup.')
    source = one(source,
        '    workspaceSplitter->addWidget(treeWidget);',
        '''    // Pixel Shroom Phase 17: stable compositing and separate image queue.
    // The queue has its own card and its own margins. Drag the splitter to
    // resize either card without reparenting or destroying the actual tree.
    auto *queueCard = new QFrame(workspaceSplitter);
    queueCard->setObjectName("psQueueCard");
    queueCard->setAttribute(Qt::WA_StyledBackground, true);
    auto *queueLayout = new QVBoxLayout(queueCard);
    queueLayout->setContentsMargins(14, 11, 14, 14);
    queueLayout->setSpacing(8);
    auto *queueHeader = new QLabel(tr("IMAGE QUEUE"), queueCard);
    queueHeader->setObjectName("psQueueHeader");
    queueLayout->addWidget(queueHeader);
    queueLayout->addWidget(treeWidget, 1);
    workspaceSplitter->addWidget(queueCard);
    queueCard->setMinimumHeight(134);''', 'separate file queue card')
    source = one(source,
        '    workspaceSplitter->setHandleWidth(8);',
        '''    workspaceSplitter->setHandleWidth(16);
    workspaceSplitter->setOpaqueResize(false);''', 'splitter breathing room')
    source = one(source,
        '    panel->setMinimumHeight(260);',
        '    panel->setMinimumHeight(300);', 'editor minimum height')
    source = one(source,
        '    tabs->tabBar()->setExpanding(true);',
        '''    tabs->tabBar()->setExpanding(true);
    tabs->tabBar()->setDrawBase(false);
    tabs->tabBar()->setObjectName("psStudioTabBar");''', 'tabbar styling anchor')
    source = one(source,
        '''            scrollArea->setStyleSheet(
                "QScrollArea { background: transparent; border: none; }"
                "QScrollArea > QWidget > QWidget { background: transparent; }"
            );''',
        '''            // Phase 17: don't force transparent child backgrounds.
            // The global glass theme paints stable page/viewport surfaces.
            scrollArea->setStyleSheet(QString());
            scrollArea->setAttribute(Qt::WA_StyledBackground, true);''',
        'remove transparent child paint override')
    source = one(source,
        '''            workspaceSplitter->setSizes({qMax(260, available - 100),
                                         100});''',
        '''            workspaceSplitter->setSizes({qMax(300, available - 150),
                                         150});''', 'balanced first splitter sizes')
    return source


def change_native(source: str) -> str:
    if '#include "pixelshroom_phase17_theme.h"' in source:
        raise ValueError('Phase 17 native integration is already present')
    if 'PixelShroomPhase15Theme::app(dark_)' not in source:
        raise ValueError('Phase 15 theme hook missing; cannot safely modify controller.')
    source = one(source,
        '#include "pixelshroom_phase15_theme.h"',
        '#include "pixelshroom_phase15_theme.h"\n#include "pixelshroom_phase17_theme.h"',
        'theme header')
    # Preserve DWM frame/title-bar backdrop, but paint the Qt central widget.
    # A transparent central widget + WA_NoSystemBackground caused older text to
    # show through after resizing on some Win11/Qt6 configurations.
    source = one(source,
        '    QWidget#centralwidget { background: transparent; }',
        '    /* The centralwidget is now painted by Phase 17 to avoid ghosted controls. */',
        'remove transparent central override')
    source = one(source,
        '        central_->setAttribute(Qt::WA_NoSystemBackground, active);',
        '''        // Qt widgets need a real backing surface even when DWM blur is on.
        central_->setAttribute(Qt::WA_NoSystemBackground, false);
        central_->setAttribute(Qt::WA_StyledBackground, true);''',
        'correct child repaint behavior')
    source = one(source,
        '''                            PixelShroomPhase15Theme::app(dark_) +
                            (active ? nativeWindowOverrides() : QString()));''',
        '''                            PixelShroomPhase15Theme::app(dark_) +
                            PixelShroomPhase17Theme::app(dark_) +
                            (active ? nativeWindowOverrides() : QString()));''',
        'append stable app stylesheet')
    source = one(source,
        '''                              PixelShroomPhase15Theme::panel(dark_));''',
        '''                              PixelShroomPhase15Theme::panel(dark_) +
                              PixelShroomPhase17Theme::panel(dark_));''',
        'append stable editor stylesheet')
    return source


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path, default=Path.cwd())
    p.add_argument('--apply', action='store_true')
    args = p.parse_args()
    root = args.project.expanduser().resolve()
    src = root / 'src'
    targets = {src / 'mainwindowimpl.cpp': change_main,
               src / 'pixelshroom_native_glass.h': change_native}
    supplied = Path(__file__).with_name('pixelshroom_phase17_theme.h')
    destination = src / 'pixelshroom_phase17_theme.h'
    try:
        if not (root / 'CMakeLists.txt').is_file():
            raise ValueError('Run from Converseen project root (missing CMakeLists.txt).')
        if destination.exists():
            raise ValueError('Phase 17 theme already exists; refusing to overwrite.')
        if not supplied.is_file():
            raise ValueError('Missing companion theme header beside script.')
        theme = supplied.read_text(encoding='utf-8')
        if 'namespace PixelShroomPhase17Theme' not in theme:
            raise ValueError('Theme header failed validation.')
        updates = {}
        for path, transform in targets.items():
            if not path.is_file():
                raise ValueError(f'Required source file missing: {path}')
            updates[path] = transform(path.read_text(encoding='utf-8-sig'))
        print('PHASE 17 SOURCE CHECK PASSED')
        for path in updates:
            print('  UPDATE', path.relative_to(root))
        print('  ADD   ', destination.relative_to(root))
        print('  KEEP  image conversion, print DPI, website optimizer, portable release')
        if not args.apply:
            print('DRY RUN PASSED. No files changed. Run with --apply to install.')
            return 0
        backup = root / 'phase17-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        for path in updates:
            b = backup / path.relative_to(root)
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, b)
        completed = []
        try:
            for path, modified in updates.items():
                path.write_text(modified, encoding='utf-8')
                completed.append(path)
            destination.write_text(theme, encoding='utf-8')
        except Exception:
            for path in completed:
                shutil.copy2(backup / path.relative_to(root), path)
            destination.unlink(missing_ok=True)
            raise
        print('APPLIED. Backup:', backup)
        print('Build with MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        return 0
    except (OSError, ValueError, UnicodeError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
