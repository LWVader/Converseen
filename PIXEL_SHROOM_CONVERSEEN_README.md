# Pixel Shroom Studio — Converseen Quick Print & Quality (Phase 1)

This additive patch targets the upstream Converseen 0.15.x Qt6 / ImageMagick 7 source layout. It **does not alter `src/main.cpp`**, so the local runtime workarounds for FLIF stay as they are. It also leaves `ui/mainwindow.ui` and CMake flags unchanged. Python 3.10+ is needed only to apply the patch, not to run Converseen.

**The patch has been statically validated against the expected source anchors, but has NOT been compiled on the user's Windows machine.** It will refuse to modify the project if those anchors differ. The compiled app still needs a local test.

## Installation

1. Close Converseen before doing any changes.
2. Put `pixel_shroom_converseen_upgrade.py` into `C:\Users\bulls\Documents\Projects\Converseen\`.
3. Open **Windows PowerShell** and run:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_converseen_upgrade.py
```

The first command checks compatibility and **does not change files**.

4. If you see `DRY RUN PASSED`, apply:

```powershell
py -3 .\pixel_shroom_converseen_upgrade.py --apply
```

Before editing the four source files, this copies the **entire existing `build` directory** and all four original files to a sibling directory like `Converseen-working-backup-20261028-132000`. It does not touch Git's `.git` directory or replace your current exe before you choose to rebuild.

5. Open **MSYS2 UCRT64** and run:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build --parallel 4
./build/converseen.exe
```

You should see the **Pixel Shroom | Quick Print & Quality** panel above the image list.

## How controls work

- **Print presets**: 16×16 (4800×4800), 16×20 (4800×6000), 24×24 (7200×7200), 24×30 (7200×9000). Enables 300 DPI metadata and uses the existing aspect-preserving ImageMagick resize.
- **Web presets**: 600×600 and 2048×2048; resolution metadata controls are left off for web outputs.
- **JPEG/WebP quality override**: unchecked by default; check to use the chosen quality (1–100) for JPEG and lossy WebP. Original PNG compression controls remain in **Advanced format / resampling...**.
- **Smooth**: Gaussian blur sigma (0 = off, range 0.0 to 2.0). Begin at 0.2–0.4 only on copies.
- **Sharpen**: sharpen sigma (0 = off, range 0.0 to 2.0). Begin at 0.3–0.7 only on copies.
- **Advanced**: opens Converseen's existing dialog for resampling filters, JPEG/PNG/WebP format options, and metadata handling.
- **DPI**: sets resolution units to pixels/inch before applying requested density. Setting 300 DPI metadata by itself does not add genuine source detail.

### Important: aspect ratios

The quick presets use **fit within target dimensions, no cropping**. A 1:1 source image selected for 16×20 **will not become exactly 4800×6000**, because preserving its shape prevents that. To get exact dimensions, use source artwork with the target aspect ratio, or plan a deliberate crop/padding workflow. The patch avoids automatic cropping.

### Initial test

1. Choose an **empty output directory**; don't overwrite originals.
2. Load one JPEG/PNG image (small test first).
3. Choose 600×600 web preset, override JPEG/WebP quality at 90, smoothing = 0, sharpen = 0; run conversion.
4. Choose a square source and 16×16 print preset; export JPEG.
5. Verify using ImageMagick in MSYS2 UCRT64:

```bash
magick identify -format '%f: %wx%h, %x x %y %U, quality %Q\n' '/path/to/output.jpg'
```

Expected for an already-square source with 16×16 preset: **4800×4800 pixels** and **300 pixels/inch**, subject to ImageMagick and JPEG metadata rounding.

### Rollback

If compile or conversion fails, locate the sibling `Converseen-working-backup-...` directory produced by the script. Copy these original files back into your existing project:

- `src/mainwindowimpl.cpp`
- `src/mainwindowimpl.h`
- `src/converter.cpp`
- `src/converter.h`

Then rebuild:

```bash
cmake --build build --parallel 4
```

Alternatively, copy the backed-up build directory back over the current build after restoring the source files. **Do not run `git restore src/main.cpp`**, as this may reverse your local ImageMagick runtime workarounds.

### Scope/limitations

- No before/after image comparison yet; this is **Phase 1** quick controls.
- The new controls start with their defaults on each launch and don't yet store separate profiles.
- FLIF's existing warning is **not** addressed by this enhancement patch.
- Because this is GPL-3.0-covered source, follow Converseen's GPL obligations if distributing modified binaries.
