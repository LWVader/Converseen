#!/usr/bin/env python3
"""Brand Pixel Shroom's Converseen fork. Dry run by default; --apply backs up before writing.
Never removes upstream copyright/license/source attribution. No Python dependencies.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from datetime import datetime
import re
import shutil

NAME = 'Pixel Shroom Image Studio'
COMPANY = 'Pixel Shroom Studio'
SITE = 'https://www.pixelshroomstudio.com/'
VERSION = '1.0.0'
MARKER = 'PIXEL SHROOM BRANDING 8.1'


def replace_one(text: str, old: str, new: str, file: str, *, required=True):
    n = text.count(old)
    if n == 0 and not required:
        return text
    if n != 1:
        raise RuntimeError(f'{file}: expected one occurrence of {old[:80]!r}, found {n}. No files changed.')
    return text.replace(old,new,1)


def change_main(text):
    fname='src/main.cpp'
    text=replace_one(text,'QCoreApplication::setApplicationName("Converseen");',
        'QCoreApplication::setApplicationName("Pixel Shroom Image Studio");',fname)
    text=replace_one(text,'parser.setApplicationDescription("Converseen - The Batch Converter and Resizer");',
        'parser.setApplicationDescription("Pixel Shroom Image Studio - Batch image and print preparation");',fname)
    # Note: desktopFileName is not useful for Windows; leave source compatibility elsewhere.
    return text


def change_window(text):
    fname='src/mainwindowimpl.cpp'
    text=replace_one(text,'QDesktopServices::openUrl(QUrl(welcomePage, QUrl::TolerantMode));',
        '// '+MARKER+': disable upstream website opening on new-version startup.',fname)
    # The next two open the application's Help/Bug Report URLs, not credits/attributions.
    text=replace_one(text,'https://github.com/Faster3ck/Converseen/issues',SITE,fname)
    text=replace_one(text,'https://converseen.fasterland.net/help/',SITE,fname)
    text=replace_one(text,'QDesktopServices::openUrl(QUrl("https://converseen.fasterland.net/donate/", QUrl::TolerantMode));',
        '// '+MARKER+': upstream donate action is hidden in the Pixel Shroom fork.',fname)
    # A duplicated source-file pattern is a compatibility stop, rather than risking breakage.
    text=replace_one(text,'    setupUi(this);','    setupUi(this);\n    // '+MARKER+': hide original upstream donation action.\n    actionDonatePaypal->setVisible(false);',fname)
    return text


def change_globals(text):
    fname='src/globals.h'
    text=replace_one(text,'const QString PROGRAM_NAME = "Converseen";',
        'const QString PROGRAM_NAME = "Pixel Shroom Image Studio";',fname)
    text,n=re.subn(r'(const QString VERSION = )"[^"]+";',r'\g<1>"1.0.0";',text,count=1)
    if n!=1: raise RuntimeError(fname+': VERSION not found')
    return text


def change_dialog(text):
    fname='src/dialoginfo.cpp'
    text=replace_one(text,'Converseen %1','Pixel Shroom Image Studio %1',fname)
    text=replace_one(text,'    setupUi(this);','    setupUi(this);\n    // '+MARKER+': original-project credits remain in the About dialog.\n    pushFacebook->hide();\n    pushDonatePayPal->hide();',fname)
    # Hide obsolete action routes, but leave original credits, copyright and license intact.
    text=replace_one(text,'https://www.facebook.com/converseen',SITE,fname)
    text=replace_one(text,'https://converseen.fasterland.net/donate/',SITE,fname)
    return text


def change_ui_main(text):
    return replace_one(text,'<string>Converseen</string>','<string>Pixel Shroom Image Studio</string>','ui/mainwindow.ui')


def change_ui_about(text):
    text=replace_one(text,'<string>About Converseen...</string>','<string>About Pixel Shroom Image Studio...</string>','ui/dialoginfo.ui')
    old='Converseen is an image batch conversion tool. You can resize and convert images in more than 100 different formats.'
    new='Pixel Shroom Image Studio prepares artwork for print and web with batch resizing, quality, and image enhancements. Built from the open-source Converseen project.'
    text=replace_one(text,old,new,'ui/dialoginfo.ui')
    return text


def change_rc(text):
    fname='converseen.rc'
    # Do not change OriginalFilename: CMake still emits converseen.exe before packaging renames it.
    for key,val in [('Comments','Batch image processing and print preparation'),
                    ('CompanyName',COMPANY),
                    ('FileDescription','Pixel Shroom Image Studio - Image Processing'),
                    ('InternalName','PixelShroomImageStudio'),
                    ('ProductName',NAME),
                    ('FileVersion',VERSION),('ProductVersion',VERSION),
                    ('LegalCopyright','Converseen (C) Francesco Mondello; modifications (C) 2026 Pixel Shroom Studio; GPL-3.0-or-later')]:
        pat=r'(VALUE\s+"'+re.escape(key)+r'"\s*,\s*)"[^"]*"'
        text,count=re.subn(pat,lambda m:m.group(1)+'"'+val+'"',text,count=1)
        if count!=1: raise RuntimeError(fname+': cannot find '+key)
    for field in ['FILEVERSION','PRODUCTVERSION']:
        text,n=re.subn(r'(?m)^(\s*'+field+r'\s+)\d+,\d+,\d+,\d+',r'\g<1>1,0,0,0',text,count=1)
        if n!=1: raise RuntimeError(fname+': missing '+field)
    return text


def change_cmake(text):
    # Retain the executable target name, which the existing portable packager expects.
    text,n=re.subn(r'(?m)^set\(CONVERSEEN_VERSION\s+[^)]+\)',
                   'set(CONVERSEEN_VERSION 1.0.0)',text,count=1)
    if n!=1: raise RuntimeError('CMakeLists.txt: cannot find version declaration')
    return text

PATCHES = {
 'src/main.cpp': change_main,
 'src/mainwindowimpl.cpp': change_window,
 'src/globals.h': change_globals,
 'src/dialoginfo.cpp': change_dialog,
 'ui/mainwindow.ui': change_ui_main,
 'ui/dialoginfo.ui': change_ui_about,
 'converseen.rc': change_rc,
 'CMakeLists.txt': change_cmake,
}


def main():
    parser=argparse.ArgumentParser(description='Rebrand the Pixel Shroom Converseen fork, without removing upstream credits')
    parser.add_argument('--project',type=Path,default=Path.cwd())
    parser.add_argument('--apply',action='store_true')
    parser.add_argument('--png',type=Path,help='Optional new application icon PNG (recommended 256x256)')
    parser.add_argument('--ico',type=Path,help='Optional multi-resolution Windows icon ICO')
    args=parser.parse_args()
    root=args.project.resolve()
    if not (root/'.git').exists() or not (root/'CMakeLists.txt').is_file():
        parser.error('Run from the root of the cloned Converseen repository.')
    changes={}
    try:
        for name, transform in PATCHES.items():
            path=root/name
            if not path.is_file(): raise RuntimeError('Required source file missing: '+str(path))
            raw=path.read_text(encoding='utf-8')
            if MARKER in raw: raise RuntimeError('Branding marker already present: '+name+'; not applying twice.')
            amended=transform(raw)
            if amended==raw: raise RuntimeError('No change detected: '+name)
            changes[path]=(raw,amended)
        icons={}
        for opt, dest in [(args.png,root/'res/icon.png'),(args.ico,root/'res/converseen.ico')]:
            if opt:
                src=opt.resolve()
                if not src.is_file() or src.stat().st_size==0: raise RuntimeError('Icon file missing/empty: '+str(src))
                if not dest.is_file(): raise RuntimeError('Original icon missing: '+str(dest))
                if src==dest: raise RuntimeError('Icon source and destination are the same: '+str(src))
                icons[dest]=src
    except Exception as exc:
        parser.error(str(exc))
    print('Files to update:')
    for p in changes: print(' ',p.relative_to(root))
    for p in icons: print(' ',p.relative_to(root),'(new icon)')
    if not args.apply:
        print('DRY RUN PASSED. Run again with --apply to back up and modify the files.')
        return
    backup=root/'phase8-backups'/('branding-8.1-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    for p in [*changes,*icons]:
        target=backup/p.relative_to(root)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(p,target)
    try:
        for p,(_,new) in changes.items(): p.write_text(new,encoding='utf-8')
        for p,src in icons.items(): shutil.copy2(src,p)
    except Exception:
        for p in [*changes,*icons]: shutil.copy2(backup/p.relative_to(root),p)
        raise
    print('BRANDING APPLIED. Backup:', backup)
    if not icons:
        print('NOTE: Original icon remains until you supply --png and --ico; do not redistribute with original logo if you intend distinct branding.')
    print('NEXT: reconfigure build-portable with -DDISABLE_CHECK_UPDATES=ON and rebuild; then rerun your portable packager.')

if __name__=='__main__': main()
