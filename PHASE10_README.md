# Phase 10 — Prepare Pixel Shroom Image Studio v1.0.0 for GitHub Release

This kit **does not rebuild the installer** and **does not publish or push anything**. It builds a local, versioned release directory from your already working Phase 9 installer, tested portable folder, and the committed source in your own Git repository.

## Files in this kit

- `pixel_shroom_phase10_release.py`: preflight, artifact assembly, SHA-256 manifest, checksum verification.
- `RELEASE_NOTES_v1.0.0.md`: editable release-note template.
- `RELEASE_CHECKLIST.md`: security, compatibility, license, and functional release gates.
- `TEST_INSTALLED_APP.cmd`: dependency-isolated basic smoke test for a clean Windows PC or VM.

## Before you run the script

1. Extract all three files into `C:\Users\bulls\Documents\Projects\Converseen`.
2. Keep your existing installer at `dist\installer\PixelShroomImageStudio-Setup-1.0.0-Win64.exe` and the working portable folder at `dist\PixelShroomImageStudio-Portable`.
3. Commit the **actual source used to compile that installer**. Make sure the app sources (`src`, `ui`, `res`) and build/packaging scripts are tracked. Avoid `git add -A` blindly; it might include your 100-MB distribution and local files.
4. Review Qt, ImageMagick, and Converseen license/attribution obligations. A single COPYING file for Converseen does not necessarily satisfy the license requirements of all distributed dependency DLLs.

## Commands (Windows PowerShell)

```powershell
cd 'C:\Users\bulls\Documents\Projects\Converseen'
git status --short
py -3 .\pixel_shroom_phase10_release.py --check
```

If the checker identifies untracked source/build files, stage only the intended files, then commit. For example, after reviewing each path:

```powershell
git add CMakeLists.txt src ui res PixelShroomImageStudio.iss build_pixel_shroom_installer.py pixel_shroom_phase8_prepare.py pixel_shroom_phase8_package.py PixelShroom_icon.ico
# Also add license text, resources.qrc, converseen.rc, and any other real source/build files you changed.
git commit -m "Release Pixel Shroom Image Studio v1.0.0 source"
```

Run `--check` again until all blockers are resolved. The check refuses to archive uncommitted tracked source or omit important untracked build files.

Then prepare files without modifying the existing installer:

```powershell
py -3 .\pixel_shroom_phase10_release.py --prepare
py -3 .\pixel_shroom_phase10_release.py --verify
```

Output is `dist\release-v1.0.0\`, containing:

- `PixelShroomImageStudio-Setup-1.0.0-Win64.exe` — byte-for-byte copy of your installer.
- `PixelShroomImageStudio-v1.0.0-source.zip` — complete tracked Git source as of HEAD, including your modifications and release build scripts.
- `PixelShroomImageStudio-Portable-Win64.zip` — **only when the ZIP matches the portable folder's EXE**.
- `RELEASE_NOTES_v1.0.0.md` — release notes, with no unsupported clean-PC claim.
- `SHA256SUMS.txt` — SHA-256 hashes of the release assets.
- `RELEASE_MANIFEST.json` — commit SHA, tag intended, hashes, and outstanding validation gates.
- `RELEASE_CHECKLIST.md` — final review form.

The script will refuse to overwrite an existing release output directory. To rerun, move `dist\release-v1.0.0` aside first; don't delete the only good copy.

## Clean PC / VM smoke test

Copy `TEST_INSTALLED_APP.cmd` to a separate Windows PC/VM **without MSYS2**. After installing the release setup, double-click it from File Explorer. It checks the installed program and JPEG/PNG/WebP format loading with a restricted PATH. Then perform manual conversion, 300-DPI metadata, and uninstall tests from `RELEASE_CHECKLIST.md`. A PASS in the smoke test alone is not a substitute for actual conversions.

## Optional: Create a GitHub draft release AFTER all checks

Install GitHub CLI (if needed): `winget install --id GitHub.cli -e`.

After verifying `git remote -v` points to your own fork, and after completing the acceptance checklist:

```powershell
gh auth login
git tag -a v1.0.0 -m 'Pixel Shroom Image Studio v1.0.0'
git push origin v1.0.0

$release = '.\dist\release-v1.0.0'
gh release create v1.0.0 `
  "$release\PixelShroomImageStudio-Setup-1.0.0-Win64.exe" `
  "$release\PixelShroomImageStudio-v1.0.0-source.zip" `
  "$release\SHA256SUMS.txt" `
  --title 'Pixel Shroom Image Studio v1.0.0' `
  --notes-file "$release\RELEASE_NOTES_v1.0.0.md" `
  --draft
```

If `PixelShroomImageStudio-Portable-Win64.zip` is present and validated, attach it to the draft through GitHub Releases or via:

```powershell
gh release upload v1.0.0 '.\dist\release-v1.0.0\PixelShroomImageStudio-Portable-Win64.zip'
```

To **publish** after a final manual review, use the GitHub Releases UI or run `gh release edit v1.0.0 --draft=false`. Publishing is an explicit, separate action and is never performed by the kit.

GitHub CLI docs: https://cli.github.com/manual/gh_release_create

## Limits

- This script cannot inspect the user’s Windows installation, confirm installer matches final Git HEAD, audit every dependency license, or validate another Windows PC. These are manual release gates.
- The repository's own source ZIP must contain the *actual modifications and scripts used to compile this build*. GitHub's autogenerated upstream archive should not substitute for a complete corresponding source distribution.
- The application installer is unsigned. Consider signing it before wider public distribution.
- If you want to distribute commercially, review GPL and dependency licenses and the Inno Setup commercial licensing terms.
