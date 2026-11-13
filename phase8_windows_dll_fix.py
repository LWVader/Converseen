#!/usr/bin/env python3
"""Small, conservative Phase 8 packager fix.

Declare AUTHZ.dll, d3d9.dll and mscms.dll as Windows-provided DLLs.
Only edits SYSTEM_DLLS in pixel_shroom_phase8_package.py. Dry-run by default.
"""
from __future__ import annotations

import argparse
import ast
from datetime import datetime
from pathlib import Path
import shutil

TARGET = 'pixel_shroom_phase8_package.py'
WINDOWS_DLLS = ('authz.dll', 'd3d9.dll', 'mscms.dll')


def update(source: bytes) -> tuple[bytes, list[str]]:
    text = source.decode('utf-8-sig')
    tree = ast.parse(text)
    matches = [stmt for stmt in tree.body
               if isinstance(stmt, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == 'SYSTEM_DLLS' for t in stmt.targets)]
    if len(matches) != 1 or not isinstance(matches[0].value, ast.Set):
        raise RuntimeError('Expected exactly one SYSTEM_DLLS set in the packager; refusing to change it.')
    node = matches[0].value
    if not all(isinstance(elt, ast.Constant) and isinstance(elt.value, str) for elt in node.elts):
        raise RuntimeError('SYSTEM_DLLS is not a set of literal strings; refusing to change it.')
    current = {elt.value.lower() for elt in node.elts}
    pending = [dll for dll in WINDOWS_DLLS if dll not in current]
    if not pending:
        return source, []

    newline = '\r\n' if b'\r\n' in source else '\n'
    lines = text.splitlines(keepends=True)
    closing_line = node.end_lineno - 1
    if lines[closing_line].strip() != '}':
        raise RuntimeError('Cannot locate the set closing brace; refusing to change it.')
    addition = "    " + ', '.join(repr(name) for name in pending) + ',' + newline
    lines.insert(closing_line, addition)
    revised = ''.join(lines)
    ast.parse(revised)
    bom = b'\xef\xbb\xbf' if source.startswith(b'\xef\xbb\xbf') else b''
    return bom + revised.encode('utf-8'), pending


def main() -> None:
    parser = argparse.ArgumentParser(description='Fix Windows system DLL classification in the Phase 8 packager')
    parser.add_argument('--apply', action='store_true', help='Back up and modify the packaging script')
    parser.add_argument('--project', type=Path, default=Path.cwd())
    args = parser.parse_args()
    project = args.project.resolve()
    target = project / TARGET
    if not target.is_file():
        parser.error(f'Cannot find {target}. Copy this fix next to the existing Phase 8 packaging script.')

    original = target.read_bytes()
    changed, pending = update(original)
    if not pending:
        print('ALREADY PATCHED: all three Windows system DLLs are in SYSTEM_DLLS.')
        return
    print('Verified target:', target)
    print('Windows DLLs to add:', ', '.join(pending))
    if not args.apply:
        print('DRY RUN PASSED. No files changed. Run again with --apply to patch.')
        return

    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = target.with_name(TARGET + '.' + stamp + '.bak')
    if backup.exists():
        raise RuntimeError(f'Backup path already exists: {backup}')
    shutil.copy2(target, backup)
    target.write_bytes(changed)
    if target.read_bytes() != changed:
        raise RuntimeError('Written packager did not verify; restore backup at ' + str(backup))
    print('PATCH APPLIED. Backup:', backup)
    print('Next command: py -3 .\\pixel_shroom_phase8_package.py')


if __name__ == '__main__':
    main()
