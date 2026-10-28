# Pixel Shroom Converseen — Phase 7

## Goal
A simplified Squoosh-inspired UI, built on the **working Phase 6 fork**. This release reduces repeated controls, makes JPEG/PNG/WebP settings format-aware and removes the extra sliders from the Live Preview window. It preserves the **Phase 5 validated 300 DPI export path** and Phase 6 linked Compare Output zoom.

## Source changes

- **Edit only:** `src/mainwindowimpl.cpp`
- **Add only:** `src/pixelshroom_phase7.h`
- **Leave unchanged:** `src/pixelshroom_phase6.h`, `src/mainwindowimpl.h`, `src/converter.cpp`, `src/converter.h`, `src/main.cpp`, Qt Designer UI files and CMake.
- **Working executable:** `build/converseen.exe` (not replaced until **you** rebuild).

The Phase 7 installer requires these exact existing files, checks matching source markers, and will stop if your local fork differs. No absolute user-specific path is compiled into the application.

## Simplified UI

**Resize:** Same existing native-backed size controls, presets, aspect-fit, Lanczos / Mitchell / other filter choices, and print DPI.

**Compress:** The application retains **one Convert to selector** in the original output area. The Compress tab automatically changes to match the format selected there:

- **JPEG:** One opt-in quality slider (1–100), and the optional Remove source metadata control.
- **PNG:** One PNG compression control (0–9), lossless; quality loss does not change as compression increases.
- **WebP:** One quality slider (lossy), WebP lossless switch, compression-effort control (0–6), dithering toggle, and optional Remove source metadata.
- **Other formats:** The original Image settings dialog is available for advanced native controls. It is hidden when JPEG/PNG/WebP are selected, preventing redundant competing settings for those formats.

**Enhance:** Original smoothing/sharpening controls remain the only editor for their values.

**Live preview:** A **modeless** (non-blocking) before/after sampled window. Move the sliders in the main Image Studio and the preview automatically updates after a short debounce. It shows a **rough** full-size output estimate. The previous extra quality and enhance sliders in the preview are no longer shown.

**Compare output:** The original Phase 6 real-file zoom and 300-DPI verification are unchanged. Its file picker now normalizes Windows paths and falls back to the selected original's folder if the configured output folder no longer exists.

## Windows paths

| Purpose | Path |
| --- | --- |
| Working project | `C:\Users\bulls\Documents\Projects\Converseen` |
| Installer files (copy from extracted ZIP) | Project root, beside `CMakeLists.txt` |
| Main C++ file | `src\mainwindowimpl.cpp` |
| Original Phase 6 header | `src\pixelshroom_phase6.h` |
| New Phase 7 header | `src\pixelshroom_phase7.h` (copied automatically) |
| Built executable | `build\converseen.exe` |
| MSYS2 dependencies | `C:\msys64\ucrt64\bin` |
| Exported files | Whatever **Save in** indicates in the main window, including OneDrive paths with spaces |

No fixed absolute export folder is added. Original input paths are read from Converseen's selected-image records; output paths are selected using Qt's native file dialog.

## Install

1. **Close Converseen**. Extract ZIP and copy `pixel_shroom_converseen_phase7.py` and `pixelshroom_phase7.h` into `C:\Users\bulls\Documents\Projects\Converseen` (project root).
2. In **Windows PowerShell**, validate (no changes):

   ```powershell
   cd 'C:\Users\bulls\Documents\Projects\Converseen'
   py -3 .\pixel_shroom_converseen_phase7.py
   ```

3. If `DRY RUN PASSED`, apply:

   ```powershell
   py -3 .\pixel_shroom_converseen_phase7.py --apply
   ```

4. In **MSYS2 UCRT64**, compile and run:

   ```bash
   cd /c/Users/bulls/Documents/Projects/Converseen
   cmake --build build --parallel 4
   ./build/converseen.exe
   ```

5. Check installed paths in **PowerShell**:

   ```powershell
   .\verify_pixel_shroom_paths.ps1 -ProjectRoot 'C:\Users\bulls\Documents\Projects\Converseen' -OutputFolder 'C:\Users\bulls\OneDrive\Pictures\Saved Pictures'
   ```

   If execution policy blocks a `.ps1` file, you can read the script and run its individual `Test-Path` checks; you need not change your machine-wide execution policy.

## Test the paths end to end

1. Import a test PNG, choose **PNG**, select `16 x 16 in | 4800 x 4800`, and check 300 DPI in **Resize**.
2. On **Compress**, confirm only PNG compression appears, with no duplicate native **Image settings** button. Change PNG compression and open **Live preview**. Change **Enhance** smoothing while the window is open; verify it refreshes.
3. In the original output area, select a different **Save in** folder (prefer a separate test folder) and convert. Confirm the output file appears in that folder. **Compare output** should open its picker there and verify print DPI from the real file.
4. Change **Convert to** to JPEG: Compress should show only the JPEG quality slider. For WebP it should show quality, lossless, effort and dithering. Changing WebP lossless should turn off custom lossy quality.
5. To inspect metadata with MSYS2 UCRT64 (replace path with your exported image):

   ```bash
   magick identify -format 'Dimensions: %wx%h\nDensity: %x x %y\nUnits: %[units]\n' 'C:/Users/bulls/OneDrive/Pictures/Saved Pictures/test.png'
   ```

   For PNG at 300 DPI, approx. `118.11 × 118.11` **PixelsPerCentimeter** is correct.

## Rollback

The installer automatically creates a timestamped sibling backup such as:

`C:\Users\bulls\Documents\Projects\Converseen-phase7-working-backup-YYYYMMDD-HHMMSS`

Close Converseen, restore `src/mainwindowimpl.cpp` from that backup to the project, delete **new** `src/pixelshroom_phase7.h`, then rebuild. Or copy the backed-up `converseen.exe` to `build\converseen.exe` to run the previous working binary without rebuilding.

## Test status and limitations

- The patcher has passed simulated Phase 6 source checks, dry-run, application, backup and duplicate-install protections.
- **C++ compilation and Windows UI runtime are not tested here**; your local `cmake --build` is the necessary validation. Any source layout mismatch should stop the installer without changes.
- The live preview uses a capped sample and is an **estimate**, not pixel-perfect output. DPI is verified only on exported files.
- The existing optional ImageMagick FLIF module warning and local MSYS2 development DLL setup are unchanged.
- The project is GPL-licensed; keep applicable source attribution/license obligations when redistributing your fork.
