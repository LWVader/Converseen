# Pixel Shroom Image Studio — Phase 8.2 About-screen cleanup

This update corrects the **About** dialog that still displays Converseen's original author block, PayPal donation invitation, and "Follow Converseen" section.

**This is a source-only patch**, not an executable. Your already-working portable program remains unchanged until you rebuild and repackage.

## Target

Project directory: `C:\Users\bulls\Documents\Projects\Converseen`

The patch only modifies:

- `src/dialoginfo.cpp`: sets the visible About screen content, credits, icon sizing and compact layout; disables the original donation/social actions.
- `ui/dialoginfo.ui`: updates static texts and labels before Qt generates the interface.

The patch does **not** touch the image converter, DPI handling, Image Studio sliders, build configuration, logo assets, or packaging script. It preserves the original author attribution, GPL license notice, and link to the Converseen source project.

## Install (PowerShell)

Extract `pixel_shroom_phase8_about_fix.py` from the ZIP into the root of your cloned Converseen project.

Open PowerShell:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase8_about_fix.py
```

Stop if the compatibility check fails. Do **not** force it or apply patches to a different source revision without review.

After `DRY RUN PASSED`:

```powershell
py -3 .\pixel_shroom_phase8_about_fix.py --apply
```

A timestamped copy of both original files is stored under `phase8-backups\about-8.2-*`.

## Rebuild (MSYS2 UCRT64)

Ensure the app is closed, then run:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

This uses your existing Qt6 portable build settings and compiles only the changed files and their dependencies. Don't delete or recreate the `build-portable` folder. If the build finishes successfully, proceed to packaging.

## Repackage (PowerShell)

Optionally preserve the currently working portable ZIP before replacing it:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
if (Test-Path '.\dist\PixelShroomImageStudio-Portable-Win64.zip') {
    Copy-Item '.\dist\PixelShroomImageStudio-Portable-Win64.zip' '.\PixelShroomImageStudio-Working-Before-About-Fix.zip'
}
py -3 .\pixel_shroom_phase8_package.py --replace
```

The app is then at:

`C:\Users\bulls\Documents\Projects\Converseen\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio.exe`

Run `TEST_PORTABLE.cmd` and then the executable.

## Expected About screen

- App: Pixel Shroom Image Studio (current version)
- Customization/maintenance: Pixel Shroom Studio
- Website: https://www.pixelshroomstudio.com/
- Short description: image resizing, print preparation, compression, enhancement and comparison
- Qt and ImageMagick versions
- Credits: original Converseen project by Francesco Mondello and contributors, linked under "Open-source foundation"
- License: GNU GPL v3 or later
- No upstream PayPal, donation, or "Follow Converseen" section displayed

## Validation

The script was dry-run/applied on a simulated Qt dialog source and checked for source integrity, backups and repeat-install protection. **It was not built on your Windows machine.** Because your source has been customized across several phases, its dry-run must succeed before application.

## Rollback

Copy the two files from the printed `phase8-backups\about-8.2-*` path back to `src\dialoginfo.cpp` and `ui\dialoginfo.ui`, and rerun `cmake --build build-portable --parallel 4`. The working ZIP backup can also be restored if necessary.

## GPL notes

The fork's branding can be Pixel Shroom, but retained copyright notices, GNU GPL license information, upstream credit, and applicable source-code distribution obligations are still required when distributing the modified application. Your Phase 8 portable packaging tool already collects root-level `COPYING*` and `LICENSE*` files; make sure you provide access to your corresponding modified source code when releasing builds.
