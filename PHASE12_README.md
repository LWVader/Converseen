# Pixel Shroom Image Studio — Phase 12: Opal / Smoke Glass

This revision is a UI/UX refinement to the Phase 11 fork. It is **not** an official Apple design or a native Apple Liquid Glass implementation. It is a restrained Apple-inspired glass look implemented in Qt Widgets, with an opal light mode and a smoke dark mode.

## What's different

- **New light opal appearance:** airy cool-white translucent-looking cards, soft depth, mild blue highlights, and neutral typography instead of saturated navy-on-navy panels.
- **Dark smoke appearance:** an optional charcoal/slate version. Use the **Dark glass / Light glass** switch in the Image Studio header. Preference is saved in Windows via `QSettings`.
- **Better hierarchy:** larger Image Studio heading, a small supporting label, simplified **Website** tab title, one clear **Optimize for website** primary action.
- **Better spacing:** breathing room inside Resize, Compress, Enhance, and Website tabs; rounded segmented-looking tabs; lighter scrollbars and cleaner input fields.
- **Original functions untouched:** the Phase 11 10 MiB preview/100 MiB original upload optimizer, print presets, verified 300-DPI export, existing batch converter, live preview, comparison viewer, and packaging scripts are retained.

This is a **Qt Widgets** theme, not native frosted-blur behind the app window. Real OS-background Mica/Acrylic would be a separate Windows 11-only enhancement (Windows 10 requires a fallback). Gradients, opacity, and the single panel shadow provide the glass-inspired visual treatment in both Windows 10 and Windows 11.

## Requirements

- Your local working `Converseen` project including **Phase 11** with `src/pixelshroom_glass_theme.h` and its Upload-ready tab.
- Python 3.
- Existing MSYS2 **UCRT64** toolchain used for previous Qt6/ImageMagick builds.

If Phase 11 was not applied and compiled successfully, do **not** apply Phase 12. First finish verifying Phase 11.

## Safe installation

Keep your verified v1.0.0 installer and any working portable ZIP. Phase 12 edits source only; it does not modify the installed application or existing executable until you rebuild it.

Extract **both** of these files directly into:

`C:\Users\bulls\Documents\Projects\Converseen`

- `pixel_shroom_phase12_liquid_glass.py`
- `pixelshroom_liquid_glass_theme.h`

In **PowerShell**, run a compatibility-only dry run:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase12_liquid_glass.py
```

Only if `DRY RUN PASSED`, apply:

```powershell
py -3 .\pixel_shroom_phase12_liquid_glass.py --apply
```

The script backs up `src/mainwindowimpl.cpp` and the existing theme header under `phase12-backups/<timestamp>/`. It then adds `src/pixelshroom_liquid_glass_theme.h` and changes only `src/mainwindowimpl.cpp`. The previous theme file is left in place for rollback.

Open **MSYS2 UCRT64** (not PowerShell) to compile:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

Run the development build to test before repackaging:

```bash
./build-portable/converseen.exe
```

If that filename is not present, use:

```bash
find build-portable -iname '*converseen*.exe'
```

The branded portable filename is generated at packaging time. Don't run `--replace` until this source build passes.

## Acceptance tests

1. Verify **Image Studio** appears in a clean opal glass panel with pill tabs and less dense spacing; no duplicate processing controls.
2. Switch from **Dark glass** to **Light glass** and restart. Confirm your choice persists.
3. Verify **Resize**, **Compress**, **Enhance** still update conversions and **Website** exports the same `__preview` / `__original` files.
4. Check the preview is <= 10,485,760 bytes and the original <= 104,857,600 bytes, or a clear failure is reported when lossless constraints cannot be met.
5. Confirm print PNG metadata remains 300 DPI using `magick identify`; check Live Preview and Compare Output.
6. Verify the UI at 100% and 150% Windows display scaling, including small window sizes. Make sure the app remains usable if text wraps.
7. Only after verification, repackage with your existing Phase 8 packaging script, then optionally rebuild a new installer version. Preserve the stable v1.0.0 release.

## Revert safely

Close the application. Copy `mainwindowimpl.cpp` from the `phase12-backups/<timestamp>` directory back into `src/`. Remove `src/pixelshroom_liquid_glass_theme.h` if it is no longer referenced. Rebuild `build-portable`. Leave the original `src/pixelshroom_glass_theme.h` as-is.

## Implementation and testing status

The upgrade script passed local **synthetic-source** compatibility, duplicate-install prevention, and safety-marker checks. The original conversion code is deliberately not patched. **C++ compilation and screenshot testing on your exact fork are still required**; no claim is made that the application has been compiled or visually inspected on Windows here.

The design is new and should be reviewed for any contrast or layout regressions on your system before distributing.
