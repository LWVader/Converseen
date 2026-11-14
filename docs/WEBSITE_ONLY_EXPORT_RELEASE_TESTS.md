# Website-only export workflow — hang fix and release gate

## Scope

All imported Pixel Shroom Image Studio artwork is intended for **website upload**.

- **Toolbar (F5): Prepare upload** is now the primary export action. It processes **checked** queue rows.
- **Website tab** contains upload rules; no second Optimize action.
- **Resize** dimensions specify maximum preview bounds. Full-size upload copies retain the **source** pixel dimensions. Automatic previews can start at a maximum long edge of 2560 pixels and shrink further to fit under 10 MiB.
- **Compress** quality controls the lossy **fallback on a large original upload copy**. If a source already fits under 50 MiB, its output copy is byte-for-byte identical. Fallback is enabled by default for this website-only workflow, can be switched off, and applies only to the generated copy.
- **Enhance** (smoothing/sharpening) applies to the website preview *only*; it never changes original artwork or a full-resolution upload copy. Adjustments are off at 0.
- Source images are **never overwritten**. Outputs are `__original` and `__preview` plus a TSV report.
- All sizes are strict: original `< 50 MiB`, preview `< 10 MiB`. Compression quality is not guaranteed to fit every source; an unsatisfied constraint must be reported.
- The workflow prepares files on disk; it does **not** upload them automatically to the Pixel Shroom website or Supabase Storage.
- **DPI limitation:** Website upload copies preserve embedded source DPI when unchanged and verify selected lossy candidates against source density. The legacy Resize print-DPI checkbox does **not** assign a new DPI value during Website preparation. To get a 300-DPI original, start with a source already tagged as 300 DPI, then verify the upload copy. Adding new DPI metadata is a separate requested feature that should be implemented and tested deliberately.

## Why the old progress dialog seemed stuck

The old Website optimizer used an indeterminate `QProgressDialog(0,0)`, tried to encode large lossless outputs even for sources already under 50 MiB, and potentially retried heavy codecs at up to 16 preview resolutions. The new code bypasses unnecessary original re-encoding and unchanged small previews, uses fast preview encoding at bounded size, and reports real per-image stages.

Cancellation is cooperative. It is checked **between** compression steps; it cannot forcibly interrupt an ImageMagick call already in progress.

## Windows test

Use MSYS2 **UCRT64**:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
git fetch origin
git switch fix/website-optimizer-progress-20261113
cmake --build build-audit --parallel 4
cp build-audit/converseen.exe \
  dist/PixelShroomImageStudio-Portable/PixelShroomImageStudio-Website-Test.exe
```

Run `PixelShroomImageStudio-Website-Test.exe` **inside the complete portable runtime directory**. Do not overwrite the working release.

### Required smoke tests

1. Import a small 1254 x 1254 image around 3.5 MiB. Mark it checked; click **Prepare upload (F5)**. Progress must show stages and finish with an export report; the new version should not re-encode a source already below 50 MiB.
2. Uncheck one queued image; it must not export. Check the queue items to process them.
3. Test the preview bounds and optional auto-downscale. Verify preview size strictly <10 MiB and full-resolution upload strictly <50 MiB.
4. Test an opaque >50 MiB 8-bit PNG with fallback ON; check for an acceptable JPEG output with the same full pixel dimensions, print density and color profile, or an explicit failure if unable to fit. With fallback OFF, source must not be silently degraded.
5. Test a source with real alpha transparency. If a compressed full copy is required, preserve alpha through WebP, or report a failure.
6. Test an original already tagged 300 DPI. Verify exported copy still reports ~300 pixels per inch (or 118.11 per centimeter).
7. Set Enhance smoothing/sharpening >0. Verify only preview changes; full-size copy stays source-identical when under 50 MiB.
8. Test Cancel during batch optimization. Some in-flight compression steps may finish before cancellation takes effect; the app must terminate later work.
9. Open `PixelShroom-Upload-Report-*.tsv`; inspect errors and output filenames.
10. Verify the original artwork bytes on disk are unmodified and both windowed/maximized UI still work.

Do not merge or package until the Windows compile and runtime tests pass.
