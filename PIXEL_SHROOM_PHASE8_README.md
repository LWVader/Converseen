# Pixel Shroom Image Studio — Phase 8 standalone Windows preparation

This package creates a **separate portable Windows release** without replacing your working Phase 7 build. The separate build uses Windows DLL-loading restrictions and resolves ImageMagick configuration and coder modules **relative to the packaged executable**.

## What this first release accomplishes

- Leaves `build/converseen.exe` and all of your Phase 7 development output files untouched.
- Adds a guarded startup routine to `src/main.cpp` that is compiled **only** for `PIXELSHROOM_PORTABLE_BUILD`.
- Creates a second build directory, `build-portable`, using UCRT64 + Qt6 + ImageMagick Q16-HDRI.
- Uses Qt's `windeployqt6` to gather Qt libraries and plugins.
- Copies ImageMagick's essential JPEG, PNG and WebP coders, plus optional popular formats, XML config and recursive UCRT64 DLL dependencies into the portable application folder.
- Creates `dist/PixelShroomImageStudio-Portable` and `dist/PixelShroomImageStudio-Portable-Win64.zip` **on your Windows computer**.

The image-conversion interface and verified 300-DPI export logic are not modified by this packaging phase. The portable build is deliberately narrower than your full development environment: not all upstream formats are included.

## Paths for your machine

| Purpose | Path |
| --- | --- |
| Project | `C:\Users\bulls\Documents\Projects\Converseen` |
| MSYS2 UCRT64 | `C:\msys64\ucrt64` |
| Working Phase 7 executable | `build\converseen.exe` — unchanged |
| Separate portable build | `build-portable\converseen.exe` |
| Finished portable app | `dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio.exe` |
| ZIP | `dist\PixelShroomImageStudio-Portable-Win64.zip` |

## 1. Back up a working checkpoint

Close Converseen. In **MSYS2 UCRT64**, from the repository:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
git status
```

If you've reviewed your source changes, you can commit them as a checkpoint. The two Python scripts never overwrite the existing `build` folder. The prepare script backs up `src/main.cpp` to `phase8-backups` before changing the source.

## 2. Install the Phase 8 files and prepare the portable startup

Extract this ZIP into your Converseen project **root**, beside `CMakeLists.txt`.

In **Windows PowerShell**:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase8_prepare.py
```

Continue only when the output says **DRY RUN PASSED**:

```powershell
py -3 .\pixel_shroom_phase8_prepare.py --apply
```

The source change runs only in a special portable build; normal Phase 7 builds remain on their previous startup path.

## 3. Build a separate portable target

In **MSYS2 UCRT64**:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake -S . -B build-portable -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DUSE_QT6=ON \
  '-DCMAKE_CXX_FLAGS=-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16 -DPIXELSHROOM_PORTABLE_BUILD'
cmake --build build-portable --parallel 4
```

If your fork's build configuration requires additional CMake flags, use your known-good settings *plus* `-DPIXELSHROOM_PORTABLE_BUILD`.

## 4. Package the portable Windows folder

Return to **PowerShell**:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase8_package.py
```

Packaging requires `windeployqt6.exe`, `objdump.exe`, Qt plugins, ImageMagick coders and libraries from `C:\msys64\ucrt64`. It checks recursive PE DLL imports before creating a ZIP. If a dependency is unavailable, packaging stops and lists it rather than claiming a working standalone build.

If you repackage after updating the portable build, run:

```powershell
py -3 .\pixel_shroom_phase8_package.py --replace
```

This intentionally replaces the prior `dist/PixelShroomImageStudio-Portable` folder and ZIP, *not* your normal `build` directory.

## 5. Test without an MSYS2 shell

Use Windows File Explorer to open:

`C:\Users\bulls\Documents\Projects\Converseen\dist\PixelShroomImageStudio-Portable`

First double-click **`TEST_PORTABLE.cmd`**. It uses a clean Windows PATH and writes any runtime error log to `%TEMP%\pixelshroom-errors.txt`. Then double-click **`PixelShroomImageStudio.exe`**.

Verify a JPEG, PNG and WebP conversion, Live Preview, Compare Output, changing output directories, and a `4800 × 4800 @ 300 DPI` PNG export. Test the packaged app after moving its entire folder to a new location; ideally validate it on a second Windows computer **without MSYS2 installed**.

## 6. Important limits and licensing

- Qt's deployment tool cannot cover all third-party dependencies automatically, which is why the script also scans and packages ImageMagick modules and DLLs.
- FLIF, PDF/Ghostscript, EXR and other niche delegates are deliberately not included in the first portable build. Future broader-format bundles require additional testing.
- Runtime validation of the actual Windows executable cannot be performed here. The preparation and packaging scripts can be statically checked, but you must compile and run the result on Windows.
- The program is based on GPL-licensed Converseen. Before sharing an installer or portable ZIP with other people, provide the corresponding source and appropriate attribution and comply with Converseen, Qt, ImageMagick and other dependency license obligations.
- Your existing image files and output directories are not moved or modified by the packaging scripts.

## Rollback

The original `src/main.cpp` is copied into `phase8-backups/main.cpp.before-phase8-<timestamp>.bak`. Close the application, copy that file back to `src/main.cpp` and rebuild your normal project if you ever need to undo the source patch. Phase 7 `build/converseen.exe` remains intact throughout Phase 8.
