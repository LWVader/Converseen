# Pixel Shroom Image Studio — Phase 13
## Native Windows Desktop Acrylic + Mica (Qt6 / MSYS2 UCRT64)

This is a **real Windows DWM compositor integration**, not just a QSS gradient. It requests the documented Windows 11 system backdrop using `DwmSetWindowAttribute` (`DWMWA_SYSTEMBACKDROP_TYPE`) and extends the frame through the client area so the material can be visible beneath non-opaque Qt surfaces. The existing Phase 12 appearance is the fallback.

**This is not Apple's proprietary Liquid Glass.** Apple's renderer is not available to a Windows Qt Widgets application. On Windows 11 build 22621+ the effect can use Windows' real Desktop Acrylic (live, blurred desktop) or Mica (wallpaper-tinted, not a live blur). On Windows 10 or unsupported configurations the existing Opal/Smoke Qt theme remains.

## New controls

Inside the Image Studio header, a compact **Window backdrop** row appears below the title:

- **Desktop Acrylic · blur** (default) — Windows 11 DWM background blur, when supported.
- **Mica · subtle** — Windows 11 wallpaper-tinted backdrop.
- **Off · Qt appearance** — stable previous Phase 12 styling.

**Light glass / Dark glass** still controls the color palette independently. Both selections are remembered using `QSettings`.

### System behavior

The app preserves the normal native title bar and window controls, unlike a fragile frameless-window redesign. Native effects are optional; the Qt fallback remains present in every mode. Windows may suppress or simplify compositor materials when transparency is disabled, a high-contrast theme is used, the system is remote, or graphics/power settings do not permit the effect. A successful API call does not guarantee a blur will be visibly displayed under every Qt child panel; inspect the main backdrop and title bar during testing.

## Supported environment

- Existing local Converseen fork with Phase 11 and Phase 12 source patches already applied.
- Windows 11 build **22621 or newer** for native DWM material modes.
- Windows 10 or unsupported Windows 11 setup: Qt fallback; no crash intended.
- Existing MSYS2 **UCRT64**, Qt6, ImageMagick, CMake + Ninja.
- No Windows App SDK installation or extra runtime DLL packaging is required. `dwmapi.dll` is a Windows system library, resolved at runtime.

## Installation (do not overwrite your stable release)

1. Keep the working installer and portable ZIP as backups.
2. Extract **both** these files into `C:\Users\bulls\Documents\Projects\Converseen`:
   - `pixel_shroom_phase13_native_glass.py`
   - `pixelshroom_native_glass.h`
3. In **PowerShell** run the dry-run:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase13_native_glass.py
```

Only after `DRY RUN PASSED`:

```powershell
py -3 .\pixel_shroom_phase13_native_glass.py --apply
```

This adds `src\pixelshroom_native_glass.h` and edits **only** `src\mainwindowimpl.cpp`. It writes a timestamped copy of the original `mainwindowimpl.cpp` under `phase13-backups\...`. It does **not** change the converter, print DPI logic, compression engine, project resource paths, CMake, or installer.

4. Open **MSYS2 UCRT64** (not plain PowerShell) and compile:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
./build-portable/converseen.exe
```

Do not use `--replace` or rebuild the installer until the feature has passed testing on your computer.

## Acceptance checklist

- Open the built app on **Windows 11 22621+** and select `Desktop Acrylic · blur`. The main background/title area should display an OS-provided material (subject to Windows policies), not just a static blue-gray gradient.
- Switch to `Mica · subtle`: expect a wallpaper-tinted backdrop rather than live blur.
- Switch to `Off · Qt appearance`: verify the previous Opal/Smoke theme appears without strange transparency or black areas.
- Toggle `Light glass` and `Dark glass`; close and reopen. Both the color mode and material selection should persist.
- Resize, maximize, restore, and switch focus; confirm no titlebar/control glitches and no layout overlapping.
- Repeat with Windows Transparency Effects disabled, if possible; verify readable fallback and no crash.
- Test batch JPEG/PNG/WebP conversion, Website preview ≤10 MiB, original ≤100 MiB where losslessly possible, Live Preview/Compare, and 300-DPI print export.
- Check 100%, 125%, and 150% Windows scaling.
- Verify the previous stable installer and its saved artwork are untouched.

## Rollback

Close the app and in PowerShell replace the changed source file from the timestamped backup:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Get-ChildItem '.\phase13-backups' -Directory | Sort-Object Name -Descending | Select-Object -First 1
```

Replace `<BACKUP_FOLDER>` with that reported directory name:

```powershell
Copy-Item '.\phase13-backups\<BACKUP_FOLDER>\mainwindowimpl.cpp' '.\src\mainwindowimpl.cpp' -Force
Remove-Item '.\src\pixelshroom_native_glass.h'
```

Rebuild using MSYS2 UCRT64:

```bash
cmake --build build-portable --parallel 4
```

If you see a black/transparent client area in native mode, select `Off · Qt appearance` and report the OS version and screenshot; do not start altering ImageMagick dependencies.

## Testing status

- The Python patch passed local **Phase 12 → Phase 13 transformation** tests.
- Dry-run, backup, apply, and second-run refusal were tested using a synthetic source fixture.
- DWM function names, attributes, and Windows version restrictions were checked against Microsoft documentation.
- **The C++ has not been compiled or visually verified on your Windows computer**. The native effect depends on the Windows compositor and how Qt paints your main central widget; that requires a live Windows test before describing it as fully verified or shipping it.

## Technical and licensing notes

Windows uses the documented `DwmSetWindowAttribute` and `DwmExtendFrameIntoClientArea` APIs. The loader resolves them from Windows' `dwmapi.dll` at runtime; no Qt plugin replacement or third-party blur library is introduced. No `SetWindowCompositionAttribute` (undocumented API) and no `FramelessWindowHint` workaround.

Retain existing GPL notices and third-party license notices when releasing the modified Converseen fork. Version this as a new development build (for example v1.2.0), not as a silent replacement for your verified v1.0.0 release.
