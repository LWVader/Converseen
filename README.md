# Pixel Shroom Image Studio

**Pixel Shroom Image Studio** is the Windows-focused image-processing application maintained by [Pixel Shroom Studio](https://www.pixelshroomstudio.com/), based on the open-source Converseen project.

It supports batch image conversion and print preparation with Qt6 and ImageMagick. It also includes a separate website upload optimizer. The executable and source retain applicable Converseen/GPL attribution and license requirements.

## Two distinct image workflows

### 1. Convert (toolbar / F5)

**Convert** remains the normal image conversion engine. The original conversion settings are preserved, including:

- Output format (JPEG, PNG, WebP and other available ImageMagick formats)
- Resize presets, exact pixel dimensions, aspect-ratio options and resampling filters
- JPEG/WebP quality, WebP lossless, PNG compression and format-specific settings
- Smoothing and sharpening adjustments, output metadata and optional print DPI
- Destination directory, file naming and overwrite preferences

The **Convert** action does not automatically apply the website file-size limit.

### 2. Website → Optimize for website

This is a **separate action** for images that will be uploaded to the Pixel Shroom Studio website. It processes **checked images** in the queue and saves **exactly one image per input**:

- A full-resolution `__original` upload copy, **strictly smaller than 50 MiB**
- **No second preview or thumbnail file**
- Original source dimensions and existing print-resolution metadata preserved
- Original source files are never overwritten
- A source already below 50 MiB is copied byte-for-byte
- A too-large original may be compressed at the chosen *Website* quality, using verified lossless encoding or optional high-quality JPEG/WebP
- Some images may be rejected if the size limit cannot be satisfied while honoring transparency, metadata and image-depth protections

The Website quality control is independent of the **Compress** tab used by normal Convert. Results and failures appear in a dialog. The application no longer creates a TSV report for each export; on startup, it cleans up only previously generated `PixelShroom-Upload-Report-*.tsv` files in the app's `upload-reports` directory.

**Note:** This prepares local image files for upload. It does not automatically transfer them to Supabase or the website. The Website tool preserves *existing* DPI; it does not assign a new DPI value based on the print settings in Resize.

## Build and test on Windows

The supported local build environment is **MSYS2 UCRT64**, Qt6, ImageMagick 7 Q16-HDRI, CMake and Ninja. Use the **UCRT64 shell**, not MINGW64.

To build from an already-configured working clone:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-audit --parallel 4
```

For a new isolated test build, after installing Qt6/ImageMagick development dependencies:

```bash
cmake -S . -B build-audit -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DUSE_QT6=ON \
  -DDISABLE_CHECK_UPDATES=ON \
  '-DCMAKE_CXX_FLAGS=-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16 -DPIXELSHROOM_PORTABLE_BUILD'

cmake --build build-audit --parallel 4
```

### Important portable runtime requirement

A standalone `build-audit/converseen.exe` does **not** contain the Qt and ImageMagick runtime. For a portable-mode test, copy it to a **new test executable name** inside the existing complete portable application folder:

```bash
cp build-audit/converseen.exe \
  dist/PixelShroomImageStudio-Portable/PixelShroomImageStudio-Test.exe
```

Launch the test executable from that folder. Do **not** replace your working `PixelShroomImageStudio.exe` or existing installer until the test is successful.

For automated compile verification, see [Windows UCRT64 CI](.github/workflows/pixel-shroom-ucrt64.yml). That GitHub Actions job compiles and runs a non-GUI smoke test; it does **not** produce a release-ready portable package or installer.

## Release checks

1. Confirm the application opens from the full portable runtime.
2. Test **Convert (F5)** with JPEG, PNG and WebP, including resize and quality controls.
3. Verify a 4800 × 4800 export with print DPI enabled still records 300 DPI (approximately 118.11 pixels/cm).
4. Test **Website → Optimize for website** with a checked image below 50 MiB: exactly one upload file, no preview, no TSV report.
5. Test an image above 50 MiB with optional compression on and off; verify dimensions, metadata, transparency, and clearly reported failures.
6. Verify unchecked items are excluded and windowed/maximized layouts still work.

See [website export checklist](docs/WEBSITE_ONLY_EXPORT_RELEASE_TESTS.md) and [compression regression tests](docs/COMPRESSION_RELEASE_TESTS.md).

## Maintenance

Older phase-by-phase patch scripts are retained for historical traceability, but the repository's C++ source is the current application; **do not re-apply obsolete phase scripts to an updated checkout**. Avoid mixing a new compiler binary with an incomplete portable runtime.

Copyright and third-party license requirements continue to apply to this fork. Consult the repository's license and upstream attribution files before redistributing binaries.
