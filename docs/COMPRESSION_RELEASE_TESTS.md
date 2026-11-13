# Pixel Shroom Image Studio — Compression regression checklist

The **Compress** tab and the **Website** tab are different export paths.

## Normal batch conversion
1. Import and check a JPEG or PNG image.
2. Choose **JPEG** under **Convert to** (the output format).
3. On **Compress**, enable **Set custom JPEG / WebP quality**. Export once at quality 95 and again at quality 82 into separate destination directories.
4. Click **Convert** each time; changing the slider alone does **not** write a file.
5. Check that both exports have the requested pixel dimensions and that the lower-quality output is generally smaller for a typical photographic image. Image contents can prevent strict size monotonicity.
6. Repeat with **WebP**; enable **WebP lossless** and confirm its quality override is disabled. PNG compression 0–9 is lossless and may not reduce arbitrary already-compressed images.
7. For print exports verify 300-DPI metadata:
   `magick identify -format "%wx%h %x %y %[units]\n" OUTPUT.png`.
   For 300 DPI, expect ~300 with `PixelsPerInch` or ~118.11 with `PixelsPerCentimeter`.

## Website optimization
1. Select **Resize** dimensions as desired maximum preview bounds; **Website** uses the same values.
2. Check only one or two queue images; leave another unchecked. Website must use only checked items.
3. Under **Website**, keep **Automatically shrink previews** checked.
4. With **high-quality original compression** unchecked, verify originals remain lossless or identical. If none fits under **50 MiB**, the app should report failure without writing an oversized file.
5. For an 8-bit opaque PNG/JPEG larger than 50 MiB, enable **If original exceeds 50 MiB, allow high-quality JPEG/WebP compression** and optimize again into a different empty destination directory.
6. The original output should keep the source pixel width and height and verified DPI/ICC metadata; the report should identify lossy JPEG/WebP and its chosen quality. This is a compressed copy, **not pixel-identical artwork**. The source file must remain unchanged.
7. Confirm previews are **strictly under 10 MiB** and originals **strictly under 50 MiB**. If a candidate cannot fit without violating its quality or metadata constraints, a reported failure is correct.
8. To validate an output pair:
   ```powershell
   py -3 tests\verify_website_export.py --source "C:\path\art.png" --original "C:\path\exports\art__original.jpg" --preview "C:\path\exports\art__preview.webp" --max-width 2048 --max-height 2048
   ```
9. Test an alpha-transparent input and a 16-bit original. They must **never** be silently flattened or downsampled to meet 50 MiB; valid outputs must satisfy the verified metadata and precision rules or report a failure.
10. Test two source folders when **Image's directory** is selected: the optimizer must stop rather than save all outputs into the first source folder.
11. Open **PixelShroom-Upload-Report-*.tsv** and inspect the message for each input. Report the first failed row along with the actual source size and format.

## Build the updated draft branch, without replacing your working release

```bash
git fetch origin
git switch audit/precompile-cleanup-20261113
cmake --build build-audit --parallel 4
```

The build command alone does not validate image compression. Copy the new `build-audit/converseen.exe` into a separate test filename in the complete bundled portable runtime before launching it.

Do **not** merge the draft pull request or replace the installer until JPEG, PNG, WebP, 300-DPI, website limits, and batch selection all pass in Windows.

## Caveats

Lossless encoding alone cannot guarantee a 50 MiB original for arbitrary complex or high-resolution artwork. A quality-limited lossy option can often meet the cap but cannot guarantee it for every input. WebP density/ICC support varies; the code rejects fallback candidates that fail its metadata checks rather than mislabeling them as equivalent.
