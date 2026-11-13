# Pixel Shroom Image Studio — Phase 20
## Fixed single-window editor / Image Studio above Preview

This patch changes the layout of the existing **Phase 19** source. It does not introduce new image-processing controls or replace the tested image conversion engine.

### Changes

- Moves the **existing Image Studio panel** from the right workspace into the original left sidebar, directly **above the existing Preview**.
- Locks the original Actions `QDockWidget` in the left side of the main window: no floating, moving, closing, or dock-toggle entry.
- Hides the **Hide Controls** and **Appearance** buttons in the Image Studio header. All Resize, Compress, Enhance and Website tabs remain visible. Appearance is still available using **Edit → Appearance settings...**
- Keeps the image queue as its own card in the main workspace alongside Conversion Formats and Output Options.
- Uses the sidebar's existing vertical scroll area to reach Preview when the window is short, and retains the editor's per-tab scrolling.
- Retains the existing conversion logic, print DPI, website preview/original limits, and preview/compare behavior.

### Installation (Windows PowerShell)

Extract `pixel_shroom_phase20_single_window.py` from the ZIP into:
`C:\Users\bulls\Documents\Projects\Converseen`

Run a non-mutating source compatibility check:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase20_single_window.py
```

It should print **DRY RUN PASSED**. If not, do not apply: your current source does not match the expected Phase 19 layout.

When the dry run passes:

```powershell
py -3 .\pixel_shroom_phase20_single_window.py --apply
```

The script backs up `src\mainwindowimpl.cpp` to a timestamped folder under `phase20-backups` before writing it. It refuses to apply more than once.

### Build and test

In **MSYS2 UCRT64**, not MINGW64 or plain PowerShell:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

For the portable build, don't double-click `build-portable\converseen.exe` alone: it needs its bundled ImageMagick runtime. In PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase20-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase20-Test.exe'
```

Test normal and maximized windows; scroll the left sidebar; switch Resize, Compress, Enhance and Website; open Appearance from **Edit**; drag the left/right divider; select and convert two files; verify 300 DPI and 10 MiB / 50 MiB upload limits. The older portable EXE and installer are not replaced by this script.

### Rollback

Copy `phase20-backups\<timestamp>\src\mainwindowimpl.cpp` back to `src\mainwindowimpl.cpp`, then rebuild. The previously working portable EXE remains untouched.

### Testing status

The Python script passed syntax and source-transformation tests against a reconstruction of the Phase 19 layout. It has **not** been compiled against your actual Windows fork. If its dry-run or Qt compile fails, send the first error; do not force-apply the patch.
