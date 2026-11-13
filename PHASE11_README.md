# Pixel Shroom Image Studio — Phase 11

## Changes

1. **Upload-ready tab:** click once to process all imported PNG/JPEG/WebP still images into two files each, in the application's currently selected output folder.
   - `name__preview.webp` or `.png` (or original extension if a small input can be copied unchanged). Strict maximum **10 MiB = 10,485,760 bytes**. Default longest edge 2,048 px. If the first preview is still oversized, the optional **reduce preview dimensions further** option searches for a smaller preview. The preview is *encoded* losslessly, but **resizing is not pixel-preserving**.
   - `name__original.png`, `.jpg`, `.jpeg`, or `.webp` depending on the smallest verified candidate. Strict maximum **100 MiB = 104,857,600 bytes**. An unchanged source copy is always eligible. Re-encoded PNG and/or lossless WebP are considered only if byte size improves and decoded pixels, depth, print density, and common ICC/EXIF/XMP/IPTC profiles pass verification. Source files are not modified. If the original cannot fit, the pair is rejected rather than silently degrading quality.
   - A timestamped TSV report records accepted sizes and rejects. No output file is intentionally overwritten. Batch compression runs on a background worker and can be cancelled between images.
2. **Premium glass-inspired theme:** new charcoal/navy layered gradients, frosted-looking translucent cards, refined menus and dock areas, blue luminous controls, accessible text contrast and clearer active tabs.
3. **Preserved:** existing batch Convert, custom enhancement controls, 300 DPI exports, Compare Output, Live Preview, Phase 8 packaging, and Inno Setup scripts. This patch **does not** edit `converter.cpp` or your verified runtime bootstrap.

## Important limitations

- No truly lossless compressor can guarantee that **all** arbitrary originals will fit within 100 MiB. The optimizer reports failures rather than changing the original's image data. **Do not change original size or DPI to force it under the cap.**
- Previews may be resized to 2,048 px (or lower when needed) *before* lossless encoding. The preview is not a full-resolution print master.
- The optimization checks widely used profiles and print resolution; uncommon/custom metadata should be audited before uploading important assets. A byte-for-byte source copy is retained when that is the smallest eligible choice.
- The UI is **glass-inspired Qt styling**, not the operating system's true blurred Mica/Acrylic backdrop; a native blur can be a separate enhancement after testing.
- The current optimizer handles **still** PNG/JPEG/WebP, not multi-frame GIF/TIFF/PDF; only use it on still artwork. The original Converseen converter continues supporting its existing formats.
- File caps are expressed in binary **MiB**. This kit does not change any Supabase bucket limits; it prepares files to fit the stated website upload limits.

## Install safely

**Keep the verified v1.0.0 installer and portable ZIP before changing your source.** In PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
New-Item -ItemType Directory -Force '.\release-backup-v1.0.0' | Out-Null
Copy-Item '.\dist\installer\PixelShroomImageStudio-Setup-1.0.0-Win64.exe' '.\release-backup-v1.0.0\' -ErrorAction Stop
Copy-Item '.\dist\PixelShroomImageStudio-Portable-Win64.zip' '.\release-backup-v1.0.0\' -ErrorAction Stop
```

Extract these **three files** into the Converseen project root:
- `pixel_shroom_phase11_upgrade.py`
- `pixelshroom_glass_theme.h`
- `pixelshroom_upload_optimizer.h`

Test compatibility without changing source:

```powershell
py -3 .\pixel_shroom_phase11_upgrade.py
```

Only if `DRY RUN PASSED`, apply:

```powershell
py -3 .\pixel_shroom_phase11_upgrade.py --apply
```

The installer backs up `src/mainwindowimpl.cpp` in `phase11-backups/<timestamp>/`. It adds two new headers under `src/` and changes **one** `.cpp` file.

Compile using your existing MSYS2 UCRT64 shell:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

You can preserve the current portable folder while testing the new build. Once compilation succeeds, return to PowerShell:

```powershell
py -3 .\pixel_shroom_phase8_package.py --replace
```

`--replace` updates only the portable folder and ZIP inside `dist`; it does not delete `dist\installer` or the separate `release-backup-v1.0.0` folder. Use `TEST_PORTABLE.cmd` then launch `PixelShroomImageStudio.exe`. Test **Upload-ready** with one copy of an image first. Leave your already installed v1.0.0 untouched until tests pass.

## Test plan

1. Convert a 4,800 × 4,800 PNG at 300 DPI with the **existing Convert** button; confirm the output still embeds ~300 DPI using `magick identify`.
2. Import that PNG. Select your test output directory. Under **Upload-ready**, press **Create upload-ready files for imported images**.
3. Inspect both `__preview` and `__original` files. Check the actual byte sizes:

```powershell
Get-ChildItem 'C:\Users\bulls\OneDrive\Pictures\Saved Pictures\*__*.png', 'C:\Users\bulls\OneDrive\Pictures\Saved Pictures\*__*.webp' -ErrorAction SilentlyContinue |
  Select-Object Name, Length
```

4. Verify original pixels/metadata when the output was recompressed:

```bash
magick identify -format '%f | %wx%h | %x x %y | %[units]\n' '/c/path/to/original.png' '/c/path/to/output__original.png'
magick identify -format '%#\n' '/c/path/to/original.png' '/c/path/to/output__original.png'
```

5. Use input filenames with spaces, choose a non-default OneDrive output folder, and run twice. The second run must create uniquely named pairs rather than overwrite the first.
6. Run a high-detail image that cannot be losslessly encoded within 100 MiB; verify it appears as a failure in the TSV report, without a reduced-quality original.
7. Verify no clipped controls or illegible text on Windows 10/11 at 100% and 150% display scaling. Verify Live Preview and Compare Output still function.

## Release management

Do **not** overwrite a validated public `v1.0.0` release with changed features. After production tests, commit the new headers, `.cpp` change and this installer script, then prepare a new version (for example, `v1.1.0`) and rebuild the corresponding Windows installer and source archive. Preserve GPL notices and source-availability requirements.

## Rollback

Restore `src/mainwindowimpl.cpp` from the folder printed by `--apply`, then delete the two new headers only if no other source uses them. Rebuild `build-portable`. Your v1.0.0 setup and portable ZIP copies are unchanged under `release-backup-v1.0.0`.

## Verification status

The Python source patch passed dry-run, apply, backup and idempotence tests on a synthetic Phase 7-compatible source fixture. A lossless WebP encode of the uploaded Pixel Shroom logo produced the **same decoded pixel signature** with ImageMagick. **The C++ patch has not been compiled or Windows-tested here**; the MSYS2 compile and a few application tests are the remaining acceptance steps.
