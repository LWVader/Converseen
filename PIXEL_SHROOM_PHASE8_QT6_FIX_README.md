# Phase 8 Qt6 build fix

Addresses `No Q_OBJECT in the class passed to QObject::findChild` in `src/mainwindowimpl.cpp`.

The Phase 7 custom `PreviewWindow` derives from `QDialog` but does not declare `Q_OBJECT`. Qt6 checks the template type supplied to `QObject::findChild<T>()`; this fix searches using `QWidget*` (which declares `Q_OBJECT`) and uses C++ `dynamic_cast` to obtain the original derived pointer safely. It replaces all **three** preview lookups, not just the one that failed first.

## Install

Copy `pixel_shroom_phase8_qt6_fix.py` into your Converseen root (`C:\Users\bulls\Documents\Projects\Converseen`).

In Windows PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase8_qt6_fix.py
py -3 .\pixel_shroom_phase8_qt6_fix.py --apply
```

The first command is a read-only compatibility check; run `--apply` only if it prints `DRY RUN PASSED`. The script backs up `src/mainwindowimpl.cpp` to `phase8-backups`.

In MSYS2 UCRT64:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

Once the build finishes successfully, use the existing Phase 8 packaging script:

```powershell
py -3 .\pixel_shroom_phase8_package.py
```

The fix **does not** alter `main.cpp`, the normal `build/converseen.exe`, ImageMagick modules, DPI handling, or the output-directory logic. The script source matching was tested against reconstructed Phase 7 sources; you still need to compile on Windows to validate the complete build.
