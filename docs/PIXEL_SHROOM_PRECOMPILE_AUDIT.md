# Pixel Shroom Image Studio — precompile audit

**Reviewed branch:** `main` at `7052a35b50d22fefa748e7b43e93a0d7793d7c6f` (2026-11-13).

This is a static source review, **not** a completed Windows compile or exhaustive per-line proof. Keep the existing verified portable installer unchanged until a clean UCRT64 build and runtime smoke tests pass.

## Included changes

1. Remove the unused **Hide Controls** widget and its connection. The editor's tabs remain visible.
2. Remove the dead Converseen thank-you URL variable (the upstream redirect had already been disabled).
3. Make **Website > Optimize** honor checked rows in the image queue, like the normal conversion path. No checked rows now show a clear message.
4. When **Image's directory** is selected and checked source images span multiple directories, stop with an explanation instead of silently saving every output in the first image's directory. A dedicated per-source-directory export workflow would be a separate feature.

## Audit observations requiring follow-up

- `src/mainwindowimpl.cpp` is about 2,600 lines and contains layered Phase 1–21 UI construction, late widget reparenting, redundant style declarations, and dependencies on hidden legacy widgets. Break into smaller classes **only after tests**, preserving all signals and settings.
- Hidden Rotate/Flip widgets are reset to neutral at setup (`mainwindowimpl.cpp` ~1233–1248), but conditional rotation and flip application remains in `startConversion()` (~1778–1799). Refactor only after confirming saved settings and reset behavior.
- The standalone editor still uses hidden Converseen Dimensions and Resolution widgets to communicate with the converter (~391–443, ~1733–1775). Don't delete them during UI cleanup.
- `main.cpp` still identifies the Linux desktop file as `net.fasterland.converseen`, and contains commented-out Windows ImageMagick environment overrides. Review cross-platform branding and remove obsolete comments in a separate commit.
- `CMakeLists.txt` defaults `DISABLE_CHECK_UPDATES` to OFF; branded release builds must explicitly pass ON. Check Qt MOC preprocessor definitions for both Qt5 and Qt6 configurations.
- `pixelshroom_upload_optimizer.h` verifies 10 MiB previews and strictly less-than-50 MiB originals, but the optimizer should get regression tests for metadata preservation, EXIF orientation, byte-for-byte original preservation when possible, filename collisions, failed writes, and cancellation.
- `pixelshroom_phase7.h` preview uses a downsampled image and extrapolates file size; its estimates cannot guarantee the final compressed size or visual quality.
- Repo includes historical Python one-time patches, a tracked `src/main.cpp.before-fix.bak`, and older README files. Archive them methodically rather than removing files referenced by packaging or GPL source instructions.
- CI `.github/workflows/build.yaml` runs on manual dispatch only and does not exercise the Pixel Shroom portable UCRT64 configuration. Add a pinned automated Windows build, static checks, and conversion smoke tests before release.

## Windows verification (from your local checked-out review branch)

```bash
git fetch origin
git switch audit/precompile-cleanup-20261113
cmake -S . -B build-audit -G Ninja -DCMAKE_BUILD_TYPE=Release -DUSE_QT6=ON -DDISABLE_CHECK_UPDATES=ON '-DCMAKE_CXX_FLAGS=-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16 -DPIXELSHROOM_PORTABLE_BUILD'
cmake --build build-audit --parallel 4
```

**Important:** A portable executable expects bundled ImageMagick paths. Test through a fresh copy of the complete portable runtime, not directly from `build-audit`, and keep the existing installer untouched. Validate: checked versus unchecked website exports, mixed-folder behavior, 10/50 MiB constraints, JPEG/PNG/WebP output, 300-DPI PNG metadata, and windowed/fullscreen resizing.

**Release gate:** code review + successful compile + runtime tests + package/test on clean Windows before merging or rebuilding the installer.
