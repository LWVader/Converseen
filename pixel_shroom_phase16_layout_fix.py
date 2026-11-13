#!/usr/bin/env python3
"""Pixel Shroom Image Studio Phase 16: fix cramped editor tabs and splitter sizing.

Safely patches Phase 15 source only. Defaults to a non-mutating dry run.
Does NOT modify converter, DPI/export logic, or packaged releases.
"""
from __future__ import annotations
import argparse
import datetime as dt
import difflib
import shutil
import sys
from pathlib import Path

MARK = '// Pixel Shroom Phase 16: scrolling editor pages and balanced splitter.'
SPLITTER_MARK = '    // Pixel Shroom Phase 15: the Studio and file list share a resizable area.'

SCROLL_CODE = r'''    // Pixel Shroom Phase 16: scrolling editor pages and balanced splitter.
    // Keep the original page objects alive: quality, DPI, resize and export signal
    // connections target their widgets. Only the Qt presentation is wrapped.
    const int initiallySelectedTab = tabs->currentIndex();
    {
        const QSignalBlocker suppressTabSignals(tabs);
        for (QWidget *page : {static_cast<QWidget *>(resizeTab),
                              static_cast<QWidget *>(compressTab),
                              static_cast<QWidget *>(enhanceTab),
                              static_cast<QWidget *>(uploadTab)}) {
            const int existingIndex = tabs->indexOf(page);
            if (existingIndex < 0 || !page->layout())
                continue;

            // A grid must NEVER shrink its content to fit a short splitter pane;
            // preserve natural row heights and scroll the viewport instead.
            page->layout()->activate();
            const int contentHeight = qMax(195, page->layout()->sizeHint().height() + 18);
            page->setMinimumHeight(contentHeight);
            page->setMinimumWidth(0);
            page->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Minimum);
            const QString caption = tabs->tabText(existingIndex);
            const QIcon tabIcon = tabs->tabIcon(existingIndex);
            const QString tip = tabs->tabToolTip(existingIndex);
            tabs->removeTab(existingIndex);

            auto *scrollArea = new QScrollArea(tabs);
            scrollArea->setObjectName(QStringLiteral("psEditorScroll_%1").arg(page->objectName()));
            scrollArea->setFrameShape(QFrame::NoFrame);
            scrollArea->setWidgetResizable(true);
            scrollArea->setHorizontalScrollBarPolicy(Qt::ScrollBarAlwaysOff);
            scrollArea->setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
            scrollArea->setSizeAdjustPolicy(QAbstractScrollArea::AdjustIgnored);
            scrollArea->setAutoFillBackground(false);
            scrollArea->viewport()->setAutoFillBackground(false);
            scrollArea->setStyleSheet(
                "QScrollArea { background: transparent; border: none; }"
                "QScrollArea > QWidget > QWidget { background: transparent; }"
            );
            scrollArea->setWidget(page);
            tabs->insertTab(existingIndex, scrollArea, tabIcon, caption);
            tabs->setTabToolTip(existingIndex, tip);
        }
        tabs->setCurrentIndex(initiallySelectedTab);
    }
    tabs->tabBar()->setUsesScrollButtons(true);

'''

REPLACEMENTS = [
    ('    panel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);',
     '    panel->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Expanding);\n'
     '    panel->setMinimumHeight(260);', 'editor panel size policy'),
    ('    treeWidget->setMinimumHeight(98);',
     '    treeWidget->setMinimumHeight(88);', 'file list minimum height'),
    ('    tabs->setMinimumHeight(215);',
     '    tabs->setMinimumHeight(175);', 'tab viewport minimum height'),
    ('    workspaceSplitter->setStretchFactor(0, 3);',
     '    workspaceSplitter->setStretchFactor(0, 4);', 'splitter editor stretch factor'),
    ('    workspaceSplitter->setStretchFactor(1, 1);',
     '    workspaceSplitter->setStretchFactor(1, 1);', 'splitter file list stretch factor'),
    ('''        if (available > 0)
            workspaceSplitter->setSizes({qMax(255, (available * 3) / 4),
                                         qMax(98, available / 4)});''',
     '''        if (available > 0)
            workspaceSplitter->setSizes({qMax(260, available - 100),
                                         100});''',
     'splitter initial allocation'),
]


def transform(text: str) -> str:
    if MARK in text:
        raise ValueError('Phase 16 appears to be installed already; no files changed')
    if text.count(SPLITTER_MARK) != 1 or 'psSettingsScroll' not in text:
        raise ValueError('Requires the Phase 15 splitter and scrollable Settings; no files changed')
    for needle in ('auto *resizeTab', 'auto *compressTab', 'auto *enhanceTab', 'auto *uploadTab',
                   'auto *workspaceSplitter', 'tabs->addTab(settingsTab, tr("Settings"))'):
        if needle not in text:
            raise ValueError('Missing Phase 15 source marker: ' + needle)

    text = text.replace(SPLITTER_MARK, SCROLL_CODE + SPLITTER_MARK, 1)
    for old, new, label in REPLACEMENTS:
        count = text.count(old)
        if count != 1:
            raise ValueError(f'{label}: expected exactly one source anchor, found {count}. No files changed')
        if old != new:
            text = text.replace(old, new, 1)
    return text


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    parser.add_argument('--apply', action='store_true', help='Make a backup and update source file')
    parser.add_argument('--show-diff', action='store_true', help='Show compact unified diff in dry run')
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    target = root / 'src' / 'mainwindowimpl.cpp'
    if not (root / 'CMakeLists.txt').is_file() or not target.is_file():
        print('ERROR: expected a Converseen project root with CMakeLists.txt and src/mainwindowimpl.cpp')
        return 2
    try:
        original = target.read_text(encoding='utf-8-sig')
        rewritten = transform(original)
        if args.show_diff:
            for line in difflib.unified_diff(original.splitlines(), rewritten.splitlines(),
                                             fromfile='before/mainwindowimpl.cpp',
                                             tofile='after/mainwindowimpl.cpp', lineterm=''):
                print(line)
        if not args.apply:
            print('DRY RUN PASSED — Phase 15 source markers match; no files were changed.')
            print('Run again with --apply to back up and apply the layout fix.')
            return 0
        stamp = dt.datetime.now().strftime('%Y%m%d-%H%M%S')
        backup = root / 'phase16-backups' / stamp / 'src' / 'mainwindowimpl.cpp'
        backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target, backup)
        temp = target.with_suffix('.cpp.phase16.tmp')
        try:
            temp.write_text(rewritten, encoding='utf-8')
            temp.replace(target)
        finally:
            if temp.exists():
                temp.unlink()
        print('APPLIED Phase 16 layout changes: ' + str(target))
        print('BACKUP: ' + str(backup))
        print('Next: rebuild in MSYS2 UCRT64, then test a copied portable EXE.')
        return 0
    except (OSError, ValueError) as exc:
        print('ERROR: ' + str(exc))
        return 1

if __name__ == '__main__':
    sys.exit(main())
