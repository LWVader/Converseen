# Pixel Shroom Image Studio — Phase 17: stable layout and glass surfaces

## What this repairs

This is a targeted correction for the November 13, 2026 screenshots after Phase 16:

- **Visual duplicates / ghosting** in Image Studio, Conversion Formats, Output Options, and the toolbar: make the Qt central backing surface and child editor pages stable rather than fully transparent. Keep Windows DWM backdrop support on the window, but limit see-through rendering inside functional controls.
- **Two boxes touching each other**: place the image queue into its own framed card, with an explicit “IMAGE QUEUE” heading and a 16-pixel draggable vertical splitter between Image Studio and the queue.
- **Tab bar still white / flat**: style the whole tab strip, not only individual tabs, with a glass-inspired gradient and saved accent color for the selected tab.
- **Toolbar**: add glass-gradient action buttons with distinct hover, pressed, and border states.
- **Windowed/fullscreen**: keep the editor's independent scrolling from Phase 16 and prevent it from shrinking below a practical minimum height.

### Important visual tradeoff

Native DWM Acrylic/Mica remains enabled where supported, but the Qt content surface is painted with stable, nearly glass-like layers rather than being truly transparent. This is deliberate to reduce the ghosting visible in the screenshots. A genuinely see-through desktop behind each individual card would require a custom painting/compositing architecture rather than nested translucent Qt stylesheets.

## Files

- `pixel_shroom_phase17_stable_layout.py` — dry-run installer with backups and guards
- `pixelshroom_phase17_theme.h` — theme layer that uses your saved accent color

Updates:
- `src/mainwindowimpl.cpp`
- `src/pixelshroom_native_glass.h`

Adds:
- `src/pixelshroom_phase17_theme.h`

Does **not** touch the image converter, DPI or website compression logic, main.cpp, installer, portable binaries, or original source assets.

## Install

Extract the two files above into your project root:

`C:\Users\bulls\Documents\Projects\Converseen`

From PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase17_stable_layout.py
```

Only if `DRY RUN PASSED` appears:

```powershell
py -3 .\pixel_shroom_phase17_stable_layout.py --apply
```

From **MSYS2 UCRT64**, not MINGW64:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

Test the newly compiled executable using the existing portable runtime; do not overwrite your stable installed application:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase17-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase17-Test.exe'
```

If the runtime folder was moved, adjust the path; do not copy the executable alone to an empty directory.

## Acceptance checks

1. Switch Resize, Compress, Enhance, Website, and Settings repeatedly.
2. Resize the main window to about 1200 × 800 and maximize again; look for ghost text behind controls.
3. Drag the divider between Image Studio and IMAGE QUEUE up and down; each box should maintain its own boundaries.
4. Ensure the tab strip no longer shows a white rectangular bar in dark mode.
5. Check toolbar buttons for stable text on mouseover, click, and window resize.
6. Check Conversion Formats and Output Options for duplicate-looking controls.
7. Import a test JPEG/PNG/WebP, resize and export one image, verify 300 DPI when selected, and test Website output limits.
8. Confirm Light/Dark and saved accent color work.

## Rollback

The installer prints the Phase 17 backup folder, such as:

`C:\Users\bulls\Documents\Projects\Converseen\phase17-backups\<timestamp>`

Close the test application and copy the backed-up `src\mainwindowimpl.cpp` and `src\pixelshroom_native_glass.h` back to the project source. Delete the added `src\pixelshroom_phase17_theme.h`, then rebuild `build-portable`. The original packaged and installed versions were not modified.

## Status

The installer and source transformations were tested with a reconstruction of the Phase 13–16 patch anchors. **It has not been compiled against your actual Windows source or visually validated on your desktop.** The installer deliberately stops on unknown source layouts instead of guessing.

If the dry run fails, provide the current `src/mainwindowimpl.cpp` and `src/pixelshroom_native_glass.h` so the patch can be adapted precisely. Do not force it.
