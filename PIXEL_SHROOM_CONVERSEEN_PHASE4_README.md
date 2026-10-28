# Pixel Shroom Converseen — Phase 4: Compare Output

This update is for the **already-running Phase 3 Converseen fork**. It provides a Squoosh-inspired **before/after comparison of the actual exported image**, not an unverified simulation of its compression settings. It does not change any image processing code.

## What's new

- **Compare output...** button in the dark Pixel Shroom Image Studio header.
- Select an image in Converseen's list, convert it, then choose that exported JPEG, PNG or WebP when prompted.
- A side-by-side dialog shows the selected **original** and the **actual saved output**.
- It displays the pixel dimensions and file size of each image, along with DPI information reported by Qt (which may be absent or inferred for some formats).
- It warns when the exported image has more than 2× the input pixels in either dimension, since resizing does not invent original detail.
- **Open exported file** button launches your default image viewer for detailed 100% examination.
- The resize, compression, smoothing, sharpen, Rotate/Flip, batch conversion, and output-folder controls are unchanged.

**Not included yet:** automatic live pre-export preview, a 100% synchronized zoom slider, and AI upscaling. This feature compares saved files **after** conversion.

## Install (Windows)

1. Close Converseen and extract this ZIP.
2. Copy `pixel_shroom_converseen_phase4.py` into `C:\Users\bulls\Documents\Projects\Converseen`.
3. In **PowerShell**:

   ```powershell
   cd 'C:\Users\bulls\Documents\Projects\Converseen'
   py -3 .\pixel_shroom_converseen_phase4.py
   ```

   Confirm it prints `DRY RUN PASSED`. It won't change files.

4. Apply the patch:

   ```powershell
   py -3 .\pixel_shroom_converseen_phase4.py --apply
   ```

   The installer preserves `src/mainwindowimpl.cpp` and `build/converseen.exe` in a new sibling `Converseen-phase4-working-backup-...` folder.

5. In **MSYS2 UCRT64**:

   ```bash
   cd /c/Users/bulls/Documents/Projects/Converseen
   cmake --build build --parallel 4
   ./build/converseen.exe
   ```

   Your known FLIF startup warning is unrelated to this patch and is not addressed here.

## Test the new feature

1. Import and select one **copy** of a source image (not the original artwork master).
2. Use the **24 x 24 in (7200 x 7200)** preset with **Print resolution** enabled at **300 DPI**.
3. Export a JPEG or PNG to your normal output folder.
4. Click **Compare output...** in the Pixel Shroom Image Studio header.
5. Choose the exported file. Confirm both previews appear, and inspect the **output** width, height, file size, and reported DPI.
6. Click **Open exported file** to zoom in using your normal Windows image viewer.

### Independently verify final print metadata

For reliable print metadata, in MSYS2 UCRT64 run (replace the quoted path):

```bash
magick identify -format 'Pixels: %wx%h\nResolution: %x x %y (%U)\n' '/c/Users/bulls/Pictures/Saved Pictures/your-output.png'
```

**Important:** ImageMagick may report resolution as pixels per centimeter for certain PNGs. 300 DPI corresponds to about **118.11 pixels per centimeter**. Exporting 7200 x 7200 with 300 DPI metadata means nominally 24 x 24 inches. Upscaling a 1254 x 1254 image to 7200 x 7200 pixels is a 5.74× enlargement in both axes; it doesn't restore fine detail that the source doesn't contain.

## Rollback

Close the app, copy `src/mainwindowimpl.cpp` from the generated `Converseen-phase4-working-backup-...` directory back to your project, then rebuild:

```bash
cmake --build build --parallel 4
```

If the rebuild fails, copy the saved `converseen.exe` into your project's `build` directory, after ensuring Converseen is closed.

**Don't restore `src/main.cpp` or the other Phase 1–3 files.** Phase 4 only edits `src/mainwindowimpl.cpp`.

## Implementation / compatibility

- The installer checks for the Phase 3 marker before touching any files. It rejects duplicate application and unexpected source layouts.
- It changes only `src/mainwindowimpl.cpp`, adding a Qt dialog and a button in `setupPixelShroomControls()`.
- The Python patcher passed syntax, insertion, repeated-installation rejection, and simulated installation backup tests. **It hasn't been compiled against your actual Windows fork.** Your local `cmake --build` step is required to validate the C++ build.
- No image data is uploaded anywhere; the comparison uses two local files that you choose.
- Converseen's existing GPL notices and license requirements continue to apply if you distribute a modified copy.
