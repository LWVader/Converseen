# Pixel Shroom Image Studio — Phase 16: video-confirmed layout repair

## What the recording shows

In the approximately 13-second screen recording, the **Resize** tab controls collide when the Image Studio / imported-file-list divider is moved and the app is restored/maximized. The Width, Height, Preserve aspect, Resize method, Print resolution, and explanatory text overlap. The tab has a grid layout but is being compressed vertically rather than offered scrolling. The empty image list retains height at the expense of editable controls.

## What the patch changes

- Makes the **Resize, Compress, Enhance and Website** tab pages individually scrollable while keeping their existing controls, signal connections and settings. **Settings** already has its own scroll area and is not wrapped again.
- Preserves each tab's natural minimum content height, so the fields **scroll** instead of drawing on top of each other.
- Allocates more space to the editor by default, while keeping the file list accessible through the splitter.
- Retains the app-wide glass theme, color personalization, Mica/Acrylic, and image canvas treatment. Does not touch the image engine, 300-DPI code or website export size limits.
- One-source-file change: `src/mainwindowimpl.cpp`. Original file is backed up automatically to `phase16-backups/<timestamp>/src/mainwindowimpl.cpp`.

## Install

1. Copy `pixel_shroom_phase16_layout_fix.py` into `C:\Users\bulls\Documents\Projects\Converseen`.
2. Close all running Image Studio instances. Open PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase16_layout_fix.py
```

3. If it says `DRY RUN PASSED`, apply:

```powershell
py -3 .\pixel_shroom_phase16_layout_fix.py --apply
```

4. In **MSYS2 UCRT64** (not MINGW64):

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

5. In **PowerShell**, test beside the portable runtime rather than launching from `build-portable`:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase16-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase16-Test.exe'
```

Do **not** repackage or replace your stable installer until the test passes.

## Test checklist

- [ ] With a 960–1200 px wide window, Resize rows are readable; height can be changed without overlapping labels.
- [ ] Drag the divider upward until the editor is at minimum. The active tab scrolls vertically. Text and spinboxes must **not** overlap.
- [ ] Maximize, restore and repeat. Control alignment remains stable.
- [ ] Switch between Resize, Compress, Enhance, Website and Settings. All pages are reachable.
- [ ] Select an imported image and verify it appears in the preview and file list.
- [ ] Export a test PNG at 4800 × 4800 and 300 DPI; verify actual output metadata via `magick identify`.
- [ ] Test Website 10 MiB preview and 100 MiB original behavior; the patch does not change it.
- [ ] Test Appearance/Color switching and Native Mica/Acrylic after restoring the window.

## If dry run fails

Don't apply a patch with missing source markers. This kit targets the Phase 15 source. The script will stop without edits when it cannot safely find the expected source layout. Provide `src/mainwindowimpl.cpp` (not your proprietary art or credentials) for a version-specific correction.

## Roll back

Close the Phase16 test app. Copy the saved `mainwindowimpl.cpp` from the backup path printed by the patch into the project's `src` folder and rebuild `build-portable` in UCRT64. Your stable portable executable and installed app remain unchanged unless you explicitly overwrite them.

## Validation status

Python syntax checking, dry-run/apply/backup and repeated-apply guard were tested on a representative Phase 15 source layout reconstructed from the prior patch. The new Qt6 C++ code has **not** been compiled or interactively tested on the user's Windows machine.
