# Pixel Shroom Image Studio — Phase 19: One size control for print and website

This is a **source-only upgrade for Phase 18 or later**. It is not an already-compiled EXE. It changes two files and deliberately does not repackage or overwrite your installed application.

## What changes

**Resize** is the single place to set pixel width, height, and aspect ratio. **Website** no longer has a separate "Preview longest edge" input. Instead, a read-only line shows the current Resize dimensions, e.g., "Preview maximum from Resize: 4800 x 4800 px". Presets, manual changes and the website action use the same spin boxes. These dimensions are a **maximum bounding box** for website previews, not a guarantee of an exact size: the output preserves aspect ratio, does not upscale a smaller original, and may be downscaled further to satisfy the upload cap.

Website exports have two outcomes:
- **Preview:** smaller than **10 MiB**; saved as `__preview`, with lossless WebP/PNG encoding or an unchanged source file where eligible. Preview pixel count may decrease, so this is not pixel-identical to the original if downscaled.
- **Original:** smaller than **50 MiB**, instead of 100 MiB; saved as `__original`. The optimizer keeps the original file when it's already small enough or adopts a smaller candidate only after decoding and checking pixel equivalence, resolution, and the stored ICC/EXIF/XMP/IPTC profiles. If 50 MiB cannot be reached losslessly, it reports a failure rather than lowering image quality or resizing the original.

**Orientation / Rotate / Flip** is moved from the permanent left Actions Panel to a button at the bottom of **Resize**. The existing widget `tab_2` is reused in a separate nonmodal dialog, so its original controls/signals continue driving Converseen's conversion engine. The left tab bar is hidden. The original hidden Dimensions widgets still exist and continue to support print DPI and conversion.

## Install

Extract `pixel_shroom_phase19_shared_resize.py` to the root of your local project:

`C:\Users\bulls\Documents\Projects\Converseen`

Close running test copies. In PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase19_shared_resize.py
```

Proceed only when you see **DRY RUN PASSED**. The script validates all expected source anchors **before editing either file**.

```powershell
py -3 .\pixel_shroom_phase19_shared_resize.py --apply
```

The script saves the originals under a timestamped `phase19-backups\...` folder (and a copy of your current `build-portable\converseen.exe` if available).

Build in **MSYS2 UCRT64**:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

Test **without replacing the stable portable executable**. In PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase19-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase19-Test.exe'
```

## Test cases

1. Set Resize to `4800 x 4800` and open Website: it shows those same dimensions; no second pixel editor.
2. Change Resize to `2048 x 2048`, switch to Website, and confirm the shared line changes.
3. Optimize a large PNG: preview is **strictly <10 MiB**, original is **strictly <50 MiB** or the app reports it cannot fit losslessly.
4. Verify the original's pixel dimensions and DPI with `magick identify`. The original output is not forcibly resized to the preview bound.
5. Open Resize → **Orientation… Rotate / Flip**, change an orientation option and convert a test image. The original controls should still apply.
6. Ensure the left Actions Panel no longer displays the Rotate/Flip box. Check windowed and maximized layouts, live preview, and 300-DPI print exports.
7. Confirm the output directory still works with paths containing spaces (e.g. OneDrive Pictures).

## Rollback

Close the application, then copy the two source files back from the printed `phase19-backups\...\src\` folder and rebuild. Your installed release and original portable executable are not modified by this patch.

**Limitations:** The patch's source transformations can be tested here, but the Qt6 C++ code has **not been compiled on your Windows machine**. If the dry run finds a changed source anchor, it stops without editing anything. Do not force an unmatched patch: send `src/mainwindowimpl.cpp` and `src/pixelshroom_upload_optimizer.h` to create an exact patch for your branch.
