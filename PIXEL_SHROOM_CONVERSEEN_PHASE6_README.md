# Pixel Shroom Converseen — Phase 6

**Linked full-resolution zoom, sampled live enhancement and compression preview, and rough output-size estimate**

## Baseline and scope

This upgrade requires the **working Phase 5 version**, with confirmed 300 DPI in the exported file. It does **not** alter Converseen's batch conversion engine or print resolution logic. Only `src/mainwindowimpl.cpp` changes; `src/pixelshroom_phase6.h` is added. `src/main.cpp`, `src/converter.cpp`, `src/converter.h`, CMake, and the conversion-status dialog remain unchanged.

A dry run checks the Phase 5 source markers and expected UI anchors. It stops without modifications if your local source differs.

## New interface

### Compare output — synchronized zoom and pan

- Select a previously converted file using the familiar **Compare output...** button.
- The new comparison window provides **Fit, 100%, 200%, 400%** zoom options. Drag (pan) either image and the other view follows the corresponding normalized position.
- **100% means one native pixel per screen pixel for the *exported* image**; the source image is scaled to match the same visual composition when the source is smaller. This is intentional for upscaling comparisons.
- Comparison loads the actual image files at full resolution for accurate zoom. Very large images consume substantial memory; a warning appears for especially large pairs.
- Embedded DPI is inspected using ImageMagick rather than the Qt display fallback. For print exports, the dialog confirms when it matches the selected print-DPI setting.

### Live preview — adjust before batch conversion

- Select a source artwork, choose JPEG, WebP, or PNG as the target format in the main application, then click **Live preview...**.
- Preview uses an in-memory **maximum 1100-pixel sample** for speed, applies the selected resize proportion, Gaussian smoothing, sharpening, and compression through ImageMagick. No temporary file is saved and your original file is not modified.
- Set **Smoothing (0.0–2.0)** and **Sharpening (0.0–2.0)**. For JPEG or WebP, turn on the quality override to change the quality percentage. PNG remains lossless and has no JPEG/WebP quality slider.
- Click **Apply settings to batch** to synchronize the already-existing Compress/Enhance controls and processing values. Click **Cancel** to discard trial settings.
- The preview shows the encoded sample's size and a **rough extrapolation for the full output file**, before converting the batch.

**Preview limitations:** It is intentionally a *sampled proxy*, not the finished 4800/7200-pixel output. It approximates the final results; exact sharpening halos, upscaled texture, metadata, WebP/PNG encoder options, and final file size can differ. No claim of pixel-perfect preview or guaranteed file-size estimate. Use the full-size **Compare output** feature after conversion to inspect the actual export. Print-DPI verification still happens on the actual exported file.

## Install on Windows

Close Converseen. Extract this ZIP and put both of these files in your existing project root:

- `pixel_shroom_converseen_phase6.py`
- `pixelshroom_phase6.h`

In **PowerShell**, run:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_converseen_phase6.py
```

Only proceed if you see `DRY RUN PASSED`. Then:

```powershell
py -3 .\pixel_shroom_converseen_phase6.py --apply
```

The installer creates a sibling backup directory named `Converseen-phase6-working-backup-YYYYMMDD-HHMMSS` containing the pre-upgrade source and working executable. It adds the new header to `src/` and modifies the one `.cpp` file, leaving the build executable untouched until you compile.

In **MSYS2 UCRT64**:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build --parallel 4
./build/converseen.exe
```

If the Windows compilation fails, **do not delete backups**. Capture the first `error:` line (not just the final Ninja message) and the lines around it.

## Verification checklist

1. Import one image (use a copy of an artwork, not the only original).
2. Select a 16x16 print preset, check 4800 x 4800 at 300 DPI. Use a separate destination directory.
3. Choose **PNG**. Click **Live preview...**; change smoothing and sharpening; confirm the right sample changes. Click **Cancel**, reopen, then click **Apply settings to batch** and check values in Enhance.
4. Convert the image. Confirm the status dialog shows `Converted` with zero errors.
5. Click **Compare output...**, select the actual exported file, test Fit / 100% / 200% / 400%, then drag in either image and verify linked navigation.
6. Verify output metadata in MSYS2 UCRT64:

```bash
magick identify -format 'Dimensions: %wx%h\nDensity: %x x %y\nUnits: %[units]\n' 'C:/full/path/to/new-output.png'
```

For 4800 × 4800 PNG at 300 DPI, approximately `118.11 x 118.11` and `PixelsPerCentimeter` is expected.

7. Repeat with a JPEG or lossy WebP output: set custom quality to 75 vs 95 and compare sampled file-size estimates. The final file sizes are not expected to match the estimated numbers exactly.

## Rollback

1. Close the application.
2. Copy `src/mainwindowimpl.cpp` from the backup folder into the project's `src/mainwindowimpl.cpp`.
3. Delete the added `src/pixelshroom_phase6.h`.
4. Rebuild with `cmake --build build --parallel 4`. Alternatively restore the saved working `converseen.exe` to `build/` without rebuilding.

No Git commit is automatically created. Commit your tested changes only after you are satisfied with the Windows result. Keep the working Phase 5 backup until the new build is validated.

## Testing / caveats

- The Python source matching, simulated dry run, simulated installation, and duplicate-installation protection were tested.
- The Phase 6 C++ code was **not compiled in this environment**, which lacks Qt/ImageMagick development headers. Compilation and GUI operation must be verified on your MSYS2 UCRT64 installation.
- Existing optional FLIF ImageMagick startup warnings are not modified by Phase 6.
- Converseen is GPL-licensed. If you redistribute this fork, comply with the applicable GPL terms and maintain upstream attribution.
