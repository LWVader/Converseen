# Pixel Shroom Image Studio — Phase 14: Full Application Glass + Appearance Settings

## Scope

This update builds on **Phase 13** and styles the **whole Qt application**, not only the Image Studio card:

- Application toolbar and toolbar buttons; menus; form controls; checkboxes, sliders, buttons, lists, tables, headers, status and progress bars; file-format and output panels.
- Left Actions/Preview panel and the **empty image preview canvas** (without changing rendered image pixels or applying a visual effect to exported artwork).
- Live Preview and Compare Output windows. Removes conflicting dark inline `setStyleSheet` definitions from their Phase 6/7 headers.
- Adds **Settings** as a fifth Image Studio tab for `Light glass / Dark glass` and `Desktop Acrylic / Mica / Off`; removes their visible selectors from the image-page header. Adds **Edit → Appearance settings...** as another way to open Settings.
- Keeps the original native Windows DWM backdrop controller and its graceful Qt fallback.

**Important:** Windows Acrylic/Mica provides the native *window backdrop*. Qt Widgets controls use coordinated translucent/frosted materials; they do not each have an independent OS-level backdrop blur. The image pixels are never tinted or modified by the theme.

## Files modified

- `src/mainwindowimpl.cpp`
- `src/pixelshroom_native_glass.h`
- `src/pixelshroom_phase6.h`
- `src/pixelshroom_phase7.h`
- Adds `src/pixelshroom_appwide_glass.h`

**Not modified:** `converter.cpp`, `main.cpp`, DPI logic, the upload optimization engine, CMake configuration, the portable build, installer scripts or original artwork.

## Install

1. Close **all** running Pixel Shroom Image Studio windows.
2. Preserve your known-good `dist` and v1.0.0 installer. Work only on the source project.
3. Extract `pixel_shroom_phase14_full_glass.py` and `pixelshroom_appwide_glass.h` into the **root** of your Converseen project:
   `C:\Users\bulls\Documents\Projects\Converseen`
4. In **PowerShell**:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase14_full_glass.py
```

Only after `DRY RUN PASSED`:

```powershell
py -3 .\pixel_shroom_phase14_full_glass.py --apply
```

5. In **MSYS2 UCRT64** (not MINGW64, not ordinary PowerShell):

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

6. Your `build-portable/converseen.exe` has portable-module validation. Do **not** run it on its own from the build directory. Instead copy it under a **separate name** into the already-working portable runtime folder in PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase14-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase14-Test.exe'
```

This uses existing DLLs, Qt plugins and ImageMagick coders without overwriting your stable executable. Do not launch the newly built EXE from `build-portable` without the bundle.

## What to verify

1. **Settings tab:** Light/Dark theme toggle and Windows backdrop selector appear there, **not beside Compare Output / Live Preview**. The Edit menu has **Appearance settings...**.
2. **Whole-app theme:** top toolbar buttons, left preview area, imported-files table, conversion-format/output panels, dialogs, Live Preview and Compare Output have consistent appearance.
3. **Image canvas:** artwork displays with original colors; its surrounding preview mat has the glass appearance.
4. **Native material:** test Acrylic/Mica/Off. Actual DWM blur depends on Windows 11 build, transparency and the compositor, and may be obscured by opaque child surfaces.
5. **Functions:** test the 10 MiB website preview and 100 MiB original profiles; JPEG/PNG/WebP conversions; output path change; 4800x4800 PNG at 300 DPI; Live Preview and Compare Output.
6. **Theme persistence:** close/reopen the test executable. Light/Dark and native material should retain your chosen values through QSettings.

## Roll back safely

The installer prints the backup directory, for example:

`phase14-backups\20261113-...\src\...`

Close the test app. Copy the four backup source files from that backup `src` directory back to the main project's `src` directory. Remove newly added `src/pixelshroom_appwide_glass.h`. Rebuild `build-portable` and test again. **Your original portable EXE and installer were never modified.**

Do not run `--apply` a second time: the patch explicitly refuses repeated application.

## Validation limits

The patcher was tested with a reconstructed Phase 13 source fixture and the existing Phase 6/7 headers, including dry-run, backup, and duplicate-run checks. It has not been compiled on your Windows computer, and your local fork may have extra edits. Dry-run will refuse to patch mismatched source anchors rather than guessing.
