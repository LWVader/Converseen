# Pixel Shroom Converseen — Phase 2 UI Update

Phase 2 is a focused upgrade for an **existing Converseen fork with Phase 1 already installed and working**. It is not a standalone application or executable.

## What changed

### 1. Conversion Status window

- Increase initial window size to 760 × 420 with a 640 × 340 minimum.
- Make the **Image** column stretch and keep **Status** in its own fixed-width column.
- Truncate visually with a middle ellipsis instead of drawing long filenames through the status column.
- Show the full filename and full status in tooltips when hovering over rows.
- Preserve existing batch status, close, and abort behavior.

### 2. Pixel Shroom | Image Studio

Replaces the cramped Phase 1 single-row panel with dark, blue-accented, Squoosh-inspired tabs:

**Resize** — Preset dropdown, editable width/height in pixels, aspect-fit toggle, resize filter (Automatic/Lanczos/Mitchell/Catrom/Triangle), print-resolution checkbox and DPI setting.

**Compress** — Checkbox-controlled JPEG/WebP quality override, linked quality slider and numerical value (1–100), plus an Advanced button to open the existing Converseen quality/format dialog. PNG keeps its native lossless settings. When the quality override is enabled, the original Phase 1 conversion logic switches WebP to lossy (by design).

**Enhance** — Separate sliders and numbers for Gaussian smoothing and sharpening (0.0–2.0 sigma; **0 = off**). Phase 1's converter still applies these opt-in enhancements. Smoothing here is an image blur filter, **not the same control** as MozJPEG's compressor-specific smoothing setting in Squoosh.

A **Hide controls** toggle collapses the editor to leave more room for the image list. Existing advanced/native Converseen controls remain available.

### Unchanged

- Existing conversion/resize processing code (`src/converter.cpp`, `src/converter.h`)
- Your Phase 1 quality override and enhancement engine
- `src/main.cpp`, the MSYS2 runtime DLL setup, and the existing FLIF warning
- `CMakeLists.txt`, Qt Designer UI files, and original application settings

## Install on Windows

1. **Close Converseen** and keep your existing Phase 1 working-build backup.
2. Extract this ZIP.
3. Copy `pixel_shroom_converseen_phase2.py` into:

   `C:\Users\bulls\Documents\Projects\Converseen\`

4. Open **Windows PowerShell**:

   ```powershell
   cd 'C:\Users\bulls\Documents\Projects\Converseen'
   py -3 .\pixel_shroom_converseen_phase2.py
   ```

   You must see `DRY RUN PASSED`. This step checks compatibility without modifying files.

5. Apply:

   ```powershell
   py -3 .\pixel_shroom_converseen_phase2.py --apply
   ```

   Before touching the source, the script backs up **the entire current `build` directory** and both files listed below to a sibling folder named `Converseen-phase2-working-backup-YYYYMMDD-HHMMSS`.

6. Open **MSYS2 UCRT64**:

   ```bash
   cd /c/Users/bulls/Documents/Projects/Converseen
   cmake --build build --parallel 4
   ./build/converseen.exe
   ```

   If compilation fails, paste the **first `error:` line and ten surrounding lines**, not just the final Ninja message.

## Source files replaced

Only these files are edited:

- `src/mainwindowimpl.cpp` — replaces the Phase 1 panel function and adds UI includes.
- `src/dialogconversionstatus.cpp` — fixes long-filename display and window sizing.

The patch **does not remove or modify** your current `build/converseen.exe` until you explicitly run CMake to rebuild.

## Test plan

1. Verify the status window displays long filenames in a separate column from `Converted`, `Skipped`, and `Error`.
2. Resize a **copy** of one square image using the 600 × 600 web preset. Confirm size.
3. Convert to JPEG at quality 90 (with quality override checked) and compare file sizes with quality 100.
4. Try Enhance at smoothing 0.0/sharpen 0.0, then light settings to verify that effects are optional.
5. Test the 16 × 16 in preset (4800 × 4800 pixels and 300 DPI) with a square source. **DPI alone does not add source image detail.**
6. Test a non-square source against a square target: when aspect ratio is checked, the result **fits within** the target and may not exactly fill it. Unchecking aspect ratio stretches the output (no auto-cropping is performed).

ImageMagick output verification:

```bash
magick identify -format '%f: %wx%h, %x x %y %U, quality %Q\n' '/path/to/image.jpg'
```

## Rollback

Close Converseen, open the sibling `Converseen-phase2-working-backup-...` folder created by the script, and copy these original files into the corresponding project paths:

- `src/mainwindowimpl.cpp`
- `src/dialogconversionstatus.cpp`

Then run `cmake --build build --parallel 4`. If needed, the backup also contains the complete original `build` directory.

**Never use `git restore src/main.cpp`** to roll this back; it could undo the separate DLL troubleshooting changes.

## Compatibility and verification

This Phase 2 script was tested with a simulated Phase 1 project for safe anchor matching, preview-only mode, full-build backup, application, and double-application rejection. **It has not been compiled on your Windows machine**, so the local build remains the decisive test. It refuses to edit unmatched or already-Phase-2 source, instead of guessing where to insert code. Because Converseen is GPL software, preserve the required GPL notices and obligations if distributing a modified build.
