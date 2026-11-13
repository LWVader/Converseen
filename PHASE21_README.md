# Pixel Shroom Image Studio — Phase 21

## Remove the broken Orientation / Rotate / Flip dialog

The screenshot shows an empty Orientation dialog whose only visible action is **Back to Resize**. This patch removes that nonfunctional dialog and the **Orientation… Rotate / Flip** button from Image Studio's Resize tab. It does not touch the Phase 20 single-window sidebar, Image Queue, appearance controls, Resize/DPI logic, conversion engine, or website compression.

### How it works

- **Only** `src/mainwindowimpl.cpp` is modified.
- The Phase 19 Orientation button, dialog and signal connections are removed from source rather than merely hidden by a stylesheet.
- Qt's existing native rotation/flip widgets are retained behind the scenes to avoid invalidating converter references, but their tab is hidden and both options are set to **No rotation** and **No flip**.
- A source backup is created in `phase21-backups/<timestamp>/src/mainwindowimpl.cpp` before applying.
- The script checks for the exact expected Phase 19/20 source structure and refuses changes if it differs.
- **No files are overwritten in the portable distribution or installer.**

### Install (Windows PowerShell)

Copy `pixel_shroom_phase21_remove_orientation.py` into:

`C:\Users\bulls\Documents\Projects\Converseen`

Run a dry run first:

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
py -3 .\pixel_shroom_phase21_remove_orientation.py
```

Only after **DRY RUN PASSED**:

```powershell
py -3 .\pixel_shroom_phase21_remove_orientation.py --apply
```

### Rebuild (MSYS2 UCRT64 — not MINGW64)

```bash
cd /c/Users/bulls/Documents/Projects/Converseen
cmake --build build-portable --parallel 4
```

### Test without replacing your existing working executable (PowerShell)

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
Copy-Item '.\build-portable\converseen.exe' `
  '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase21-Test.exe'
& '.\dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio-Phase21-Test.exe'
```

Confirm:
1. Resize tab no longer has **Orientation… Rotate / Flip**.
2. No empty Orientation dialog opens.
3. Image Studio remains above Preview in the same fixed window.
4. Test one image for JPEG/PNG/WebP conversion and check the 300-DPI output and Website upload workflow as before.

**The last two checks still need to be performed on your Windows machine; the patch has not been compiled locally against your fork.**

### Rollback

Close the app. Copy the backed-up `mainwindowimpl.cpp` from the `phase21-backups/<timestamp>/src` folder over `src/mainwindowimpl.cpp`, then rebuild using the same CMake command. The original portable executable was never replaced by the patch.

### Note on the source

This is intentionally a small UI removal. It does **not** remove the Qt-generated tab or rewrite the rotation/flip conversion internals, which might cause unrelated image-processing regressions. Those hidden controls are reset to their no-op values.
