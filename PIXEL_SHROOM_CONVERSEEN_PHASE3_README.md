# Pixel Shroom Converseen — Phase 3 layout cleanup

## What this fixes

Your Phase 2 screenshot shows the new **Image Studio → Resize** panel and the original **Actions Panel → Dimensions** tab at the same time. Both control the same underlying Converseen resize/DPI settings. This Phase 3 patch hides **only the duplicate native Dimensions tab** while leaving all of its Qt widgets in memory so that the Image Studio controls and converter continue working. The native **Rotate / Flip** tab stays accessible in the Actions Panel.

It also stretches the Image Studio's three main tabs evenly across the available width so there's no white gap to the right of **Enhance**.

**Only modified source:** `src/mainwindowimpl.cpp`.

**Left unchanged:** `src/mainwindowimpl.h`, `src/converter.cpp`, `src/converter.h`, `src/dialogconversionstatus.cpp`, `src/main.cpp`, all `.ui` files, CMake, and all original image conversion logic. No new dependencies.

## Install from PowerShell

Close the Converseen window. Extract the ZIP and copy `pixel_shroom_converseen_phase3.py` to:

`C:\Users\bulls\Documents\Projects\Converseen\`

Run a non-modifying compatibility check:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_converseen_phase3.py
```

Only if the result reads `DRY RUN PASSED`, apply it:

```powershell
py -3 .\pixel_shroom_converseen_phase3.py --apply
```

The script creates `Converseen-phase3-working-backup-YYYYMMDD-HHMMSS` next to your project. It backs up the currently working `src/mainwindowimpl.cpp` and `build/converseen.exe` **before** changing source code. It does not clone, reinstall, or reconfigure your project.

In **MSYS2 UCRT64**:

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build --parallel 4
./build/converseen.exe
```

## What you should see

- Image Studio on the right with **Resize**, **Compress**, **Enhance** tabs spanning the width.
- Preview and **Rotate / Flip** in the left Actions Panel.
- **No duplicate Scale Image / Dimensions / Resolution controls** on the left.
- The existing output-format, file-path, batch status, and overwrite options unchanged.

## Test

1. Select a **copy** of a square PNG and a separate output folder.
2. Choose the **600 × 600** preset, then convert; verify 600 × 600 pixels.
3. Select a print preset such as **16 × 16 in / 4800 × 4800**; verify print resolution 300 DPI for a supported format.
4. Switch to the **Rotate / Flip** tab; verify you can still rotate a test image.
5. Confirm compress and enhance controls still work.

The existing FLIF warning is unrelated and is not changed by this update.

## Rollback

Close Converseen. Find the `Converseen-phase3-working-backup-...` folder beside your project, restore its `src/mainwindowimpl.cpp` over the project file, then rebuild:

```bash
cmake --build build --parallel 4
```

If rebuilding fails, the backup also contains the prior `converseen.exe`, which can be restored to your project `build/` folder.

## Notes

This patch was checked against the Phase 2 update script's generated C++ panel and the upstream UI's names (`tabWidget`, `tab`, `tab_2`). It has **not been compiled on your Windows machine**; the local CMake build is the definitive test. The Phase 3 installer refuses to run if Phase 2 markers or exact insertion points are missing. Preserve the GPL license obligations if distributing a modified Converseen binary.
