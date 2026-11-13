# Pixel Shroom Image Studio — Phase 8.1 Qt MOC update checker fix

## What failed
The compiler uses `DISABLE_CHECK_UPDATES` and omits Converseen's three update-checker functions, but `qt6_wrap_cpp()` invokes Qt's Meta-Object Compiler without that preprocessor macro. MOC generates calls to nonexistent methods and compilation stops in `moc_mainwindowimpl.cpp`.

## Fix
This patch changes **only `CMakeLists.txt`** so `qt6_wrap_cpp()` receives `OPTIONS -DDISABLE_CHECK_UPDATES` when the CMake `DISABLE_CHECK_UPDATES` option is enabled. It preserves source branding, the program icon, portable path initialization, and conversion logic.

## Installation
Extract `pixel_shroom_phase8_moc_fix.py` into `C:\Users\bulls\Documents\Projects\Converseen`.

PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase8_moc_fix.py
py -3 .\pixel_shroom_phase8_moc_fix.py --apply
```

In MSYS2 UCRT64:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake -S . -B build-portable -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DUSE_QT6=ON \
  -DDISABLE_CHECK_UPDATES=ON \
  '-DCMAKE_CXX_FLAGS=-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16 -DPIXELSHROOM_PORTABLE_BUILD'
cmake --build build-portable --parallel 4
```

If the build completes, return to PowerShell:

```powershell
py -3 .\pixel_shroom_phase8_package.py
```

After packaging, run `TEST_PORTABLE.cmd` in the portable directory, then launch `PixelShroomImageStudio.exe` directly from File Explorer. Verify logo, no Converseen update redirect, PNG export at 4800×4800/300 DPI, and compare/preview.

## Rollback
The installer saves the original `CMakeLists.txt` under `phase8-backups`. To reverse the patch, replace the modified file with that exact backup and reconfigure.

## Safety
No build directories, DLLs, or original files are deleted. If the local CMake layout has changed, the script refuses to apply. This fix has been syntax/patch-tested against representative upstream CMake but has not been compiled on your Windows machine.
