#!/usr/bin/env python3
"""Phase 20: move Image Studio above Preview into a locked, single-window sidebar.

Usage, from the Pixel Shroom Converseen project root:
  py -3 pixel_shroom_phase20_single_window.py
  py -3 pixel_shroom_phase20_single_window.py --apply

Only src/mainwindowimpl.cpp changes. Requires the installed Phase 17-19 layout.
The program refuses unexpected source structures and backs up before writing.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import difflib
from pathlib import Path
import shutil
import sys

MARK = '// Pixel Shroom Phase 20: single-window Image Studio above Preview.'
START = '    // Pixel Shroom Phase 15: the Studio and file list share a resizable area.'
TIMER = '    QTimer::singleShot(0, this, [workspaceSplitter]() {'
END = '    });'

REPLACEMENT = '''    // Pixel Shroom Phase 20: single-window Image Studio above Preview.
    // Keep the existing QDockWidget as a fixed left sidebar. It can no longer
    // close, float, or move into a separate window. We reuse the real preview,
    // studio controls and image queue; no processing widget is duplicated.
    dockWidget->setFloating(false);
    dockWidget->setAllowedAreas(Qt::LeftDockWidgetArea);
    dockWidget->setFeatures(QDockWidget::NoDockWidgetFeatures);
    dockWidget->toggleViewAction()->setVisible(false);
    dockWidget->setMinimumWidth(500);
    dockWidget->setMaximumWidth(760);
    auto *emptyDockTitle = new QWidget(dockWidget);
    emptyDockTitle->setFixedHeight(0);
    dockWidget->setTitleBarWidget(emptyDockTitle);

    // The original Actions sidebar already contains a scroll area and a
    // Preview widget. Put the whole existing Image Studio above that Preview.
    // This shares one scrollbar instead of generating yet another window.
    verticalLayout_20->removeWidget(panel);
    panel->setParent(scrollAreaWidgetContents);
    panel->setMinimumWidth(0);
    panel->setMinimumHeight(305);
    panel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    verticalLayout_12->insertWidget(0, panel);
    verticalLayout_12->setSpacing(12);
    verticalLayout_7->setSizeConstraint(QLayout::SetDefaultConstraint);
    scrollArea->setWidgetResizable(true);
    scrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
    scrollArea->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
    scrollArea->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);

    // Hide the old Image Studio actions without disconnecting any converter
    // state. Settings remains available through Edit > Appearance settings.
    collapse->setChecked(true);
    collapse->hide();
    if (auto *appearance = panel->findChild<QPushButton *>("psAppearanceOpenButton"))
        appearance->hide();

    // The center/right workspace is dedicated to queue and export details.
    // Moving the EXISTING tree widget preserves selection, import and status
    // signals. Keep the Phase 17 queue object name for its glass stylesheet.
    auto *queueCard = new QFrame(centralwidget);
    queueCard->setObjectName("psQueueCard");
    queueCard->setAttribute(Qt::WA_StyledBackground, true);
    auto *queueLayout = new QVBoxLayout(queueCard);
    queueLayout->setContentsMargins(14, 11, 14, 14);
    queueLayout->setSpacing(8);
    auto *queueHeader = new QLabel(tr("IMAGE QUEUE"), queueCard);
    queueHeader->setObjectName("psQueueHeader");
    queueLayout->addWidget(queueHeader);
    verticalLayout_20->removeWidget(treeWidget);
    queueLayout->addWidget(treeWidget, 1);
    treeWidget->setMinimumHeight(180);
    treeWidget->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);
    verticalLayout_20->insertWidget(0, queueCard, 1);
    verticalLayout_20->setStretch(0, 1);

    // Give the editor a useful starting width; the user can still change the
    // divider between the fixed left sidebar and main workspace.
    QTimer::singleShot(0, this, [this]() {
        if (dockWidget && !dockWidget->isFloating())
            resizeDocks({dockWidget}, {540}, Qt::Horizontal);
    });'''


def transform(source: str) -> str:
    if MARK in source:
        raise ValueError('Phase 20 already appears to be installed. No changes made.')
    for required in (
        'Pixel Shroom Phase 17: stable compositing and separate image queue.',
        'Pixel Shroom Phase 18: independent settings window with live theme preview.',
        'Pixel Shroom Phase 19: one shared Resize/Website pixel size.',
        'auto *panel = new QFrame(centralwidget);',
        'auto *collapse = new QToolButton(panel);',
        '    auto *queueCard = new QFrame(workspaceSplitter);',
        '    workspaceSplitter->addWidget(queueCard);',
        '    verticalLayout_20->insertWidget(0, workspaceSplitter);',
    ):
        if required not in source:
            raise ValueError('Source is not the expected Phase 19 layout; missing ' + repr(required))
    if source.count(START) != 1:
        raise ValueError('Expected one Phase 15 workspace layout block.')
    begin = source.index(START)
    timer = source.find(TIMER, begin)
    if timer < 0:
        raise ValueError('Could not locate the original workspace splitter initialization timer.')
    finish = source.find(END, timer)
    if finish < 0:
        raise ValueError('Could not locate the end of the workspace splitter block.')
    finish += len(END)
    old = source[begin:finish]
    if 'workspaceSplitter->addWidget(queueCard);' not in old or 'verticalLayout_20->insertWidget(0, workspaceSplitter);' not in old:
        raise ValueError('Workspace layout differs from the expected Phase 17 structure.')
    # Leave previous Phase 16 editor-tab scroll wrappers untouched. They were
    # inserted BEFORE START and remain necessary in the narrower sidebar.
    return source[:begin] + REPLACEMENT + source[finish:]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--apply', action='store_true', help='Back up and modify source')
    parser.add_argument('--show-diff', action='store_true', help='Display source changes without applying')
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    path = root / 'src' / 'mainwindowimpl.cpp'
    try:
        if not (root / 'CMakeLists.txt').is_file() or not path.is_file():
            raise ValueError('Expected Converseen project root with CMakeLists.txt and src/mainwindowimpl.cpp.')
        previous = path.read_text(encoding='utf-8-sig')
        updated = transform(previous)
        if args.show_diff:
            for line in difflib.unified_diff(previous.splitlines(), updated.splitlines(),
                                             fromfile='before/mainwindowimpl.cpp',
                                             tofile='after/mainwindowimpl.cpp', lineterm=''):
                print(line)
        print('PHASE 20 SOURCE CHECK PASSED')
        print('  EDIT src/mainwindowimpl.cpp (UI layout only)')
        print('  KEEP original Preview, file queue, batch engine and DPI/export logic')
        print('  FIX  dock float/move, Image Studio placement, header controls')
        if not args.apply:
            print('DRY RUN PASSED. Nothing changed. Use --apply to install.')
            return 0
        backup = root / 'phase20-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        backup.mkdir(parents=True, exist_ok=False)
        src_backup = backup / 'src' / 'mainwindowimpl.cpp'
        src_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, src_backup)
        temp = path.with_name(path.name + '.phase20.tmp')
        try:
            temp.write_text(updated, encoding='utf-8')
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)
        print('APPLIED. Backup:', backup)
        print('In MSYS2 UCRT64: cmake --build build-portable --parallel 4')
        return 0
    except (OSError, UnicodeError, ValueError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
