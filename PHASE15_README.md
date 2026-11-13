# Pixel Shroom Image Studio — Phase 15
## Responsive layout + glass cards + accent/canvas personalization

This patch builds on the installed **Phase 14** Windows Qt6 source. It is a source-only patch and does not replace the existing installed or portable release.

### Fixes and features

1. **Windowed/fullscreen layout:** Moves the Image Studio and imported-file list into a vertical `QSplitter`. Drag the divider to allocate room. The Studio is no longer `QSizePolicy::Maximum`, and the file list can shrink without crushing the Settings controls.
2. **Scrollable Settings page:** The Appearance and Workspace personalization cards are inside an independent vertical scroll area. At smaller window heights, scroll inside Settings rather than clipping its contents.
3. **Glass cards:** Adds softer translucent multi-stop gradients, restrained highlights, subtle elevation shadows on Settings cards, selected-tab accent, and themed file-list, format, output and canvas surfaces. Native Windows Mica/Desktop Acrylic continues to supply the backdrop behind Qt widgets, when supported.
4. **Personalization (Settings only):** Accent presets Ice Blue, Amethyst, Sea Glass, Coral, and Champagne; plus a custom QColorDialog. Canvas-mat presets Auto, Midnight, Slate, Charcoal, Ivory; plus custom color. Both save through QSettings and update immediately when selected. Image data is **not** recolored, filtered or altered.
5. **Existing tools preserved:** No changes to JPG/PNG/WebP export, resizing, 300-DPI metadata, smoothing/sharpening, Website preview ≤10 MiB/original ≤100 MiB workflow, preview/comparison engine, packaging, licensing or updater code.

**Notes:** Qt card translucency is composited Qt painting, not a separate true per-card background-blur shader. The window backdrop is still native DWM Acrylic or Mica where available. This patch changes the appearance and layout but does not install Apple's proprietary Liquid Glass.

### Files

- `pixel_shroom_phase15_responsive_glass.py` — dry-run/source patcher with backups
- `pixelshroom_phase15_theme.h` — Qt style + settings helper
- `PHASE15_README.md` and `TESTING_CHECKLIST.txt` — installation and acceptance tests

The patch modifies only:

- `src/mainwindowimpl.cpp`
- `src/pixelshroom_native_glass.h`
- adds `src/pixelshroom_phase15_theme.h`

### Install safely

1. Close Pixel Shroom Image Studio windows.
2. Unzip the first two files into your project root:

   `C:\Users\bulls\Documents\Projects\Converseen`

3. From **PowerShell**:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase15_responsive_glass.py
```

If it says `DRY RUN PASSED`:

```powershell
py -3 .\pixel_shroom_phase15_responsive_glass.py --apply
```

Backups are placed under `phase15-backups\<timestamp>\src\`.

4. Build in **MSYS2 UCRT64** (not MINGW64 or unconfigured PowerShell):

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

5. Test beside your already-working portable runtime, without overwriting the stable EXE. In **PowerShell**:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase15-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase15-Test.exe'
```

**Do not launch the newly built EXE directly from `build-portable`:** the portable build expects adjacent ImageMagick modules and other runtime dependencies.

### Verify

- At ~1340×1000 (windowed) and maximized: Settings content is readable and vertically scrollable; the file list can be resized with its divider; the bottom conversion/output panels remain reachable.
- Settings → Accent color: change 5 presets and custom. Tabs, focus highlights and primary Upload button update. Close/reopen and verify persistence.
- Settings → Image canvas mat: choose Slate or Ivory; verify the empty canvas surround changes, **not** source/exported image pixels. Custom color works and persists.
- Switch Light/Dark glass; switch Mica/Acrylic/Off. The app remains usable and dialogs readable.
- Load JPEG, PNG, WebP; verify Live Preview, Compare Output, DPI, output folder, and Website exports. Test original/preview limits with actual file-size checks.

### Rollback

Close the Phase15 test EXE, then copy saved `mainwindowimpl.cpp` and `pixelshroom_native_glass.h` from the printed `phase15-backups\...\src` folder back into `src\`. Delete the newly added `src\pixelshroom_phase15_theme.h`. Rebuild with `cmake --build build-portable --parallel 4`. The stable portable EXE and installed release remain unchanged throughout this test.

### Validation limits

The patch passed local simulated source-transformation, repeated-installation rejection, and source-backup checks using a reconstruction of the Phase14 layout and header. It **has not been compiled or visually verified on your Windows machine**. The script deliberately stops if the local source markers differ rather than replacing unknown user edits.
