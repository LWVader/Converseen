# Pixel Shroom Image Studio — Phase 9 Installer Kit

This kit compiles a Windows setup `.exe` from your **already-tested portable release** using Inno Setup. It does not rebuild Converseen or modify `build`, `build-portable`, your source, your image files, or the existing portable app.

## Prerequisites

- Windows with your tested portable folder at `C:\Users\bulls\Documents\Projects\Converseen\dist\PixelShroomImageStudio-Portable`.
- Its `PixelShroomImageStudio.exe` launches from File Explorer and JPEG/PNG/WebP + 300-DPI conversions work.
- Python 3 (the `py -3` launcher that you already use).
- Inno Setup 7, installed from https://jrsoftware.org/isdl.php (or run `winget install --id JRSoftware.InnoSetup.7 -e -s winget -i`). Inno Setup 6.7+ should also compile this file.

## Extract to the Converseen project root

Put **all three** provided files directly in `C:\Users\bulls\Documents\Projects\Converseen`:

1. `PixelShroomImageStudio.iss`
2. `build_pixel_shroom_installer.py`
3. `PixelShroom_icon.ico`

Do not extract into `dist\PixelShroomImageStudio-Portable`, because that is the application payload.

## Check (no changes)

In Windows PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\build_pixel_shroom_installer.py
```

Expect `CHECK PASSED`. If files are reported missing, run the original portable packager or resolve the listed files before proceeding.

## Build the installer

```powershell
py -3 .\build_pixel_shroom_installer.py --build --version 1.0.0
```

If Inno Setup isn't automatically found, pass e.g.:

```powershell
py -3 .\build_pixel_shroom_installer.py --build --version 1.0.0 --iscc 'C:\Program Files (x86)\Inno Setup 7\ISCC.exe'
```

Result (on your Windows machine):

`C:\Users\bulls\Documents\Projects\Converseen\dist\installer\PixelShroomImageStudio-Setup-1.0.0-Win64.exe`

The builder refuses to overwrite an existing installer. To build a later release, increment `--version 1.0.1` or rename your prior setup EXE first.

## What installer does

- Installs only for the current user (no UAC prompt required by default).
- Default location: `%LOCALAPPDATA%\Programs\Pixel Shroom Image Studio`.
- Copies the complete portable runtime, including the private Qt / ImageMagick DLLs, coder modules, configs and licenses.
- Creates Start Menu and uninstall entries, plus an **optional** desktop shortcut.
- Uses your uploaded mushroom artwork as the setup executable's icon. The actual app icon comes from your already-branded portable EXE.
- Offers to launch Image Studio after installing.
- Leaves existing output images and their chosen folders alone; doesn't register file associations or run the obsolete Converseen updater.

## Test before distributing

1. Preserve your working portable folder and ZIP.
2. Build setup EXE, double-click it in File Explorer, and finish setup.
3. Launch from Start Menu and optional Desktop shortcut.
4. Verify JPEG/PNG/WebP processing, changed output folder, live preview, comparison, and an exported PNG reporting ~118.11 pixels/cm (= ~300 DPI) for a 4800x4800 print.
5. Check About Pixel Shroom Image Studio; ensure no upstream website opens automatically.
6. Uninstall using **Settings > Apps > Installed apps**. Confirm that your exported artwork remains untouched.
7. **Before public distribution**, test on a separate computer or fresh Windows VM that does not have MSYS2, Qt or ImageMagick installed. This is not validated on another machine yet.

## Attribution and distribution obligations

Pixel Shroom Image Studio is a modified Converseen fork. Keep the original authorship and GPL notices accessible, and offer the **complete corresponding source code** for the distributed binaries, including your modifications and any applicable build scripts. You should also comply with Qt, ImageMagick and other dependency-license terms, including notices. The included installer only packages the portable runtime; it **does not automatically make a source-code distribution**. Before sharing publicly, prepare source availability and test the license directory.

Inno Setup requests that commercial users purchase a license: https://jrsoftware.org/isorder.php.

## Limitations

The zip **contains installer-building files**, not a compiled Windows installer; your Windows computer must compile the `.iss` with Inno Setup. Signing is not configured. Unsigned installers can trigger Windows SmartScreen warnings; a code-signing certificate and proper signing workflow are recommended before broad distribution.

Rollback: this installer kit does not change your source or working build. If the install test fails, uninstall from Windows Settings and continue using your existing portable release.
