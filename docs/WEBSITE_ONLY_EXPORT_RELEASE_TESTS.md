# Pixel Shroom Image Studio — Website Export Test Plan

## Two independent export workflows

1. **Convert (F5)** uses the original Converseen conversion engine, including output format, Resize, Compress, Enhance, DPI/print settings, renaming, and overwrite controls. It is **not** subject to the 50 MiB Website limit.
2. **Website → Optimize for website** prepares precisely **one full-resolution website image per checked queue item**. It saves an `__original` image below 50 MiB, **never a preview**, and does not alter the imported source. Website compression quality is independent of Compress. Resize/Enhance/print DPI belong to normal Convert, not Website optimization.

Website output requirements:
- Image file size strictly **less than 50 MiB**.
- Preserve the *source* pixel dimensions and available embedded DPI/color profile; for oversized 8-bit images, the optional high-quality JPEG/WebP fallback may alter pixel colors but never dimensions.
- When a source already fits, make an identical byte-for-byte copy.
- If the constraints cannot be met, report a failure rather than silently reduce resolution, flatten transparency, remove ICC data or downconvert 16-bit artwork.
- **One image only** per checked input in the selected output directory, named `<stem>__original.<ext>`. Do not generate `__preview`.
- No TSV/diagnostic reports are written on export. Success counts and up to eight failure details are shown directly in the results dialog. On startup, the app removes legacy `PixelShroom-Upload-Report-*.tsv` files only from its AppData `upload-reports` folder; other app data and images remain untouched.
- Files are prepared locally; there is no automatic Supabase upload.

## Build / test (MSYS2 UCRT64)

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
git fetch origin
git switch fix/single-website-original-restore-convert-20261114
cmake --build build-audit --parallel 4
cp build-audit/converseen.exe \
  dist/PixelShroomImageStudio-Portable/PixelShroomImageStudio-SingleUpload-Test.exe
```

Open the copied test executable from inside the complete `dist/PixelShroomImageStudio-Portable` folder. Do not replace `PixelShroomImageStudio.exe` or the installer.

## Required checks

1. Toolbar says **Convert**, triggers normal conversion, preserves the destination format, resize filter, quality overrides, enhancements, 300-DPI settings, rename/overwrite behavior.
2. Open Compress and select JPEG/WebP/PNG in `Convert to`. Check the corresponding codec controls appear; verify a JPEG at quality 82 is generally smaller than 95 for a typical photograph.
3. Select one small `<50 MiB` image and click **Website → Optimize for website**. Progress should finish without unnecessary recompression. The chosen folder contains exactly one `__original` image (plus any files already there) and no new `__preview`. The source and copied image have identical bytes.
4. Unchecked image queue rows must not export via the Website button.
5. For an 8-bit opaque source `>=50 MiB`, with the Website lossy fallback enabled, verify a same-size JPEG copy below 50 MiB, or explicit failure if metadata constraints prevent it. With fallback disabled, only lossless copies are allowed.
6. Check a transparent image and a 16-bit input: no silent alpha flattening or 16-to-8-bit downgrade.
7. Confirm a source tagged 300 DPI produces the same recorded DPI in its upload output. Website does **not** assign new 300 DPI to sources missing it.
8. Test F5 normal Convert after Website optimization. Ensure it still runs original image conversion, **not** the Website optimizer.
9. Verify Cancel stops work between compression attempts (individual ImageMagick encoding calls cannot be interrupted), and results/errors appear in the results dialog without creating a report file.
10. Ensure unrelated mixed-directory sources are not silently exported into the first folder when **Image's directory** is selected.
11. Close and reopen the updated program. Verify existing `PixelShroom-Upload-Report-*.tsv` files in the app's AppData `upload-reports` folder are removed; unrelated files in the folder are preserved. Confirm new Website exports do not create `.tsv` files.
12. Run the updated read-only verifier, replacing paths with actual files:

```powershell
py -3 tests\verify_website_export.py --source "C:\path\art.png" --original "C:\path\out\art__original.jpg"
```

**Release gate:** Do not merge or repackage before a successful UCRT64 compile and all applicable Windows runtime tests. A lossless file over 50 MiB may correctly fail; the application cannot guarantee every source fits without loss or violating its fidelity safeguards.
