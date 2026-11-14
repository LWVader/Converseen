# Pixel Shroom Image Studio — Compression Regression Tests

The two export functions are **independent**:

- **Convert (F5)**: ordinary image conversions, print sizing, dpi stamping, JPEG/WebP quality override, PNG compression, smoothing/sharpening, file renaming and overwrite settings. All original conversion controls remain intact.
- **Website → Optimize for website**: one original full-resolution upload image per checked input, strictly below 50 MiB. No preview/thumbnail, no duplicate image export. Website quality control is separate from the normal Compress tab.

## Normal Convert tests

1. Import a JPEG or PNG; check its queue row and select JPEG under `Convert to`.
2. On **Compress**, check **Set custom JPEG / WebP quality**; export at 95 then 82 using separate target folders. Both files should be created by the **Convert** toolbar button.
3. Repeat with WebP lossy and WebP lossless; verify its lossy quality override and lossless checkbox behave consistently.
4. Choose PNG and verify the visible PNG compression 0–9 controls work without unexpected quality loss; PNG file size may not always get smaller.
5. On Resize, test 4800 × 4800 and 300 DPI; check with:

```bash
magick identify -format "%wx%h %x %y %[units]\n" output.png
```

300 DPI can display as ~300 PixelsPerInch or ~118.11 PixelsPerCentimeter.

6. Enable Enhance; ensure the settings affect normal Convert outputs. Verify metadata removal and renaming/overwrite behavior still work.

## Website tests

1. Select **Website** and check its own lossy fallback checkbox and quality value, independently of Compress.
2. Optimize a checked image smaller than 50 MiB. It should create exactly one `__original` image, preserving original bytes, pixel dimensions and embedded DPI.
3. Optimize an opaque 8-bit source larger than 50 MiB. If allowed, it should try high-quality JPEG/WebP for the full-sized copy without altering source artwork. An explicit failure is correct if it cannot meet size and metadata requirements.
4. Confirm no `__preview` images are created.
5. Check the output image directly:

```powershell
py -3 tests\verify_website_export.py --source "C:\art\source.png" --original "C:\art\processed\source__original.jpg"
```

6. Confirm no new TSV reports are created. Existing `PixelShroom-Upload-Report-*.tsv` files are removed from the app's AppData `upload-reports` folder at startup, without deleting other application files. Failed image messages must remain visible in the results dialog.

See [WEBSITE_ONLY_EXPORT_RELEASE_TESTS.md](WEBSITE_ONLY_EXPORT_RELEASE_TESTS.md) for the complete runtime checklist.
