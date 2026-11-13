# Pixel Shroom Image Studio — Phase 18
## Full-workspace colors, polished scrollbars, separate appearance window

This is a targeted follow-up to the user's Phase 17 screenshot. It does not change any image-processing logic, files being exported, output directories, metadata handling, or the installer.

### Changes

- **Unified accent theme:** The selected accent now affects the main workspace, toolbar, menus, action buttons, image queue, side panel, conversion/output cards, field borders and highlights, progress bar, and tab bar. The existing **Canvas mat** setting still controls the editor canvas separately. Tint strengths are deliberately restrained so all text remains readable.
- **Scrollbar restyling:** Rounded vertical and horizontal scroll tracks/handles in matched colors, hover feedback, a wider grab target, no dated arrow buttons. Applied globally, including the Settings view and queue.
- **Dedicated Settings window:** Removes the fifth Settings tab from Image Studio. Open via **Appearance...** in Image Studio's header or **Edit → Appearance settings...**. The window contains the existing appearance and personalization controls plus a color-responsive interface preview. Use **Back to editor** (top or bottom) or the title-bar Close button to exit. No settings are duplicated and saved preferences continue using QSettings.
- **Reliable painting:** Maintains Phase 17's stable widget backgrounds rather than making Qt child widgets transparently expose old frames. Native Windows Mica/Acrylic remains available at the window level, not on each child card.

### Files changed

- Updates `src/mainwindowimpl.cpp` (Settings presentation/navigation only).
- Updates `src/pixelshroom_native_glass.h` (theme wiring).
- Adds `src/pixelshroom_phase18_theme.h` (one unified paint palette and scrollbar style).

It does **not** modify `converter.cpp`, export settings, format processing, DPI metadata logic, Website 10/100 MiB optimizer, CMake, installer scripts, or `dist`.

### Install

1. Close all running development-test copies of Image Studio. Keep your installed v1.0.0 and working portable executable as backups.
2. Extract `pixel_shroom_phase18_settings_and_palette.py` and `pixelshroom_phase18_theme.h` to `C:\Users\bulls\Documents\Projects\Converseen`.
3. Open Windows PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase18_settings_and_palette.py
```

Only when the check reports **DRY RUN PASSED**:

```powershell
py -3 .\pixel_shroom_phase18_settings_and_palette.py --apply
```

4. Rebuild with **MSYS2 UCRT64** (not MINGW64):

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

5. Test the new executable using a distinct filename in your existing portable runtime bundle:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase18-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase18-Test.exe'
```

### Visual and functional test

- **Appearance...** opens a dedicated Settings window and the image editor shows only Resize / Compress / Enhance / Website tabs.
- Edit → Appearance settings... opens the same window. Closing/reopening doesn't create multiple settings windows.
- Change accent to Coral or Sea Glass. Toolbar, side pane, queue, tabs, form cards and scrollbar highlights follow it. Light and Dark both retain readable contrast.
- Changing canvas mat changes only the preview mat (including the Settings sample), not image pixels.
- Settings preview samples the toolbar, canvas, primary/secondary actions and progress bar. Both **Back to editor** buttons work.
- Drag a scrollbar and verify smooth scrolling in narrow and maximized windows. The page doesn't overlap or clip.
- Re-test JPEG, PNG and WebP, 300-DPI PNG print export, Website preview/original limits, Live Preview and Compare Output.

### Restore if anything fails

The script prints a backup directory, e.g. `phase18-backups\YYYYMMDD-HHMMSS-xxxxxx`. Close the test program. Copy the saved `src\mainwindowimpl.cpp` and `src\pixelshroom_native_glass.h` back from that backup to the project `src` directory. Delete only the newly added `src\pixelshroom_phase18_theme.h`; rebuild `build-portable`.

### Limits

This patch has been tested with reconstructed Phase 17 source anchors, including a dry run, backup and duplicate-install guard. Your exact local C++ fork has not been provided or compiled here. If the dry run fails, it will not modify the project. In that case, upload current `src/mainwindowimpl.cpp` and `src/pixelshroom_native_glass.h` for a source-exact patch. Do not bypass the compatibility check.
