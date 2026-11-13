# Pixel Shroom Image Studio — Phase 8 Windows DLL Packaging Fix

## Why packaging stopped

The C++ portable build completed. `windeployqt6` deployed the core Qt DLLs and plugins. The Python packager then stopped because it incorrectly treated three standard Windows imports as missing third-party DLLs:

- `Qt6Core.dll` imports `AUTHZ.dll`
- `qwindows.dll` imports `d3d9.dll`
- `qwindows.dll` imports `mscms.dll`

The Phase 8 package builder has an allowlist named `SYSTEM_DLLS` in `pixel_shroom_phase8_package.py`. These names were missing from that allowlist. Windows supplies them; do **not** copy DLLs out of `C:\Windows\System32` into the portable application.

## How to apply

Extract `pixel_shroom_phase8_windows_dll_fix.py` into:

`C:\Users\bulls\Documents\Projects\Converseen`

Open Windows PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase8_windows_dll_fix.py
```

Expect `DRY RUN PASSED`. Apply:

```powershell
py -3 .\pixel_shroom_phase8_windows_dll_fix.py --apply
```

The fix backs up `pixel_shroom_phase8_package.py` with a timestamp before modifying its `SYSTEM_DLLS` set. It does not change C++ code, ImageMagick, Qt, or either compiled build. Applying it again is safe: it will report `ALREADY PATCHED`.

Then retry packaging (no recompile required):

```powershell
py -3 .\pixel_shroom_phase8_package.py
```

The expected results, if no further issues appear, are:

- `dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio.exe`
- `dist\PixelShroomImageStudio-Portable\TEST_PORTABLE.cmd`
- `dist\PixelShroomImageStudio-Portable-Win64.zip`

Run `TEST_PORTABLE.cmd` and double-click `PixelShroomImageStudio.exe` from **File Explorer**, not from MSYS2. Test one JPEG, PNG and WebP and a 4800×4800 300-DPI export. Test from a folder outside `C:\msys64` and eventually on another Windows computer without MSYS2 to verify that the package is truly portable.

## Nonblocking warnings

The earlier `windeployqt` output about OpenSSL, Direct3D 12 DXC, or missing Qt translation catalog is not what stopped the package. They may affect features you aren't using; they'll be reviewed once basic standalone conversion works. Do not suppress unknown DLL failures or copy system files to make the packager pass.

## What was tested

Patch installer behavior, source syntax, backup creation, idempotence, and all three allowlist additions were checked in a local test fixture. The updated packager has not been run on your Windows machine; its final package and standalone runtime still require verification there.
