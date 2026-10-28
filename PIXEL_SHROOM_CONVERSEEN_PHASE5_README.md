# Pixel Shroom Converseen — Phase 5 DPI Fix

## What the screenshots showed

- The **16 × 16 in / 4800 × 4800** preset resized your file correctly.
- The **Conversion Status** window reported **Converted / 0 Errors**.
- Despite **Print resolution / 300 DPI** being enabled in Image Studio, the exported comparison reported **96 × 96 DPI**.
- An independent ImageMagick check on a prior file showed `Density: 72 x 72` and `Units: Undefined`, confirming that at least one export was missing valid 300-DPI metadata.

## Cause and changes

The earlier Phase 2 panel was created before the constructor reset the hidden native resolution boxes to zero. When **Print resolution** was already checked, changing or selecting a print preset did not necessarily emit a new toggle event to populate the hidden fields. The batch converter then could receive zero or stale density values.

**Phase 5** makes the new Image Studio checkbox and DPI numeric control the source of truth at the beginning of every batch. It also corrects **Compare output...** to inspect actual saved-file metadata with ImageMagick (`ping()`, `resolutionUnits()`, `xResolution()`, `yResolution()`) instead of reading DPI from Qt's scaled preview image. PNG pixels-per-centimeter density is converted to DPI for display. When print DPI is enabled, the comparison shows a pass or warning based on the selected value.

### Changes to the project

- **Modified:** `src/mainwindowimpl.cpp` (only)
- **Read-only compatibility check:** `src/converter.cpp`, to verify that the existing ImageMagick resolution-units and density setters are present
- **Unchanged:** `src/main.cpp`, `src/converter.cpp`, conversion-status dialog, CMake, existing image-enhancement settings, output naming and file-overwrite behavior

The known optional FLIF module startup warning is unrelated and remains unmodified.

## Install

1. Close Converseen. Extract the ZIP and copy `pixel_shroom_converseen_phase5.py` to:

   `C:\Users\bulls\Documents\Projects\Converseen`

2. In **Windows PowerShell**, validate without modifying source:

   ```powershell
   cd 'C:\Users\bulls\Documents\Projects\Converseen'
   py -3 .\pixel_shroom_converseen_phase5.py
   ```

   Continue only if it prints `DRY RUN PASSED`.

3. Apply:

   ```powershell
   py -3 .\pixel_shroom_converseen_phase5.py --apply
   ```

   A sibling folder named `Converseen-phase5-working-backup-YYYYMMDD-HHMMSS` is created, containing the working `src/mainwindowimpl.cpp` and `converseen.exe`. This does not delete your existing build directory.

4. Open **MSYS2 UCRT64**:

   ```bash
   cd /c/Users/bulls/Documents/Projects/Converseen
   cmake --build build --parallel 4
   ./build/converseen.exe
   ```

## Verify with one new test export

1. Import a test copy of a PNG or JPEG.
2. Choose `16 x 16 in | 4800 x 4800`.
3. Verify that `Print resolution` is checked and reads `300 DPI`.
4. Export to **PNG** under a *new filename* in a separate output folder. If you previously exported the same filename, do not accidentally compare an older file.
5. In **Compare output...**, choose the new exported file. It should show `Embedded print DPI: 300 × 300` and `Print DPI verified` (subject to PNG rounding), or a clear warning if the metadata is missing.
6. Confirm independently:

   ```bash
   magick identify -format 'Dimensions: %wx%h\nDensity: %x x %y\nUnits: %[units]\n' 'C:/full/path/to/new-export.png'
   ```

   Expected PNG result is usually **118.11 × 118.11 PixelsPerCentimeter** (approximately 300 DPI), or **300 × 300 PixelsPerInch** if the format writes inch-based units.

7. Repeat with two images in one batch if the first test passes. Print DPI should be applied consistently across all images in the batch.

**Note:** 4800 × 4800 pixels at 300 DPI is a nominal 16 × 16-inch print. Enlarging 1254 × 1254 pixels to 4800 × 4800 does not recover missing original detail.

## Rollback

1. Close Converseen.
2. Restore the saved `src/mainwindowimpl.cpp` from `Converseen-phase5-working-backup-*` to the matching project file.
3. Rebuild with `cmake --build build --parallel 4`. Or restore the saved `converseen.exe` into your `build` folder without rebuilding if no other files changed.

## Test status

The Python patch and its exact-text compatibility checks were tested using a reconstruction of the preceding Phase 4 code. The Windows C++ build and runtime DPI behavior **cannot be tested in this environment**. If the dry run or C++ build fails, do not remove backups or alter the source manually; share the first error line.
