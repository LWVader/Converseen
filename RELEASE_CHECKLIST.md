# Pixel Shroom Image Studio v1.0.0 — Release acceptance checklist

**Status: DRAFT.** Do not label the release production-ready until these checks are completed.

## Source integrity and licensing

- [ ] All final source modifications, resources, headers, and build/installer scripts committed in the correct GitHub fork.
- [ ] The committed HEAD **matches the source actually used to build this exact installer** (rebuild if unsure).
- [ ] Complete corresponding source available with installer; not merely a link to upstream unmodified Converseen.
- [ ] Preserve Converseen authorship and GPL license, modification notices, and copyright notices.
- [ ] Review runtime library licensing (Qt, ImageMagick, FLIF, OpenEXR, etc.) and include all required license texts/notices and fulfillment options.
- [ ] Check Git history and source files for embedded passwords, tokens, local secrets, personal files, build output, or other material not for publication.

## Installer functional acceptance

- [ ] Install as a non-admin Windows user; Start Menu shortcut opens application.
- [ ] Optional desktop shortcut opens application.
- [ ] About shows Pixel Shroom branding, original Converseen credits, and no obsolete donation prompts.
- [ ] No unexpected Converseen site redirects or upstream auto-updater.
- [ ] Convert at least one JPEG, PNG, and WebP image successfully.
- [ ] Run a multi-image batch with a custom output directory containing spaces.
- [ ] Verify no image is overwritten without the intended user action.
- [ ] Verify a 4800 × 4800 PNG set to 300 DPI with ImageMagick: `Density: ~118.11 x 118.11; Units: PixelsPerCentimeter`.
- [ ] Test live enhancement preview, compression quality, compare output, and linked zoom.
- [ ] Uninstall and confirm exports are retained and shortcuts removed.

## Test on a clean Windows environment (REQUIRED before public release)

- [ ] Test install and uninstall on a second Windows 64-bit PC or fresh VM **without MSYS2, ImageMagick, or Qt developer tools**.
- [ ] Confirm the app launches and actual JPEG/PNG/WebP conversions work.
- [ ] Confirm printer-resolution metadata in resulting output file.
- [ ] Check installer and runtime with Windows security tools; review unsigned installer warnings and consider code signing.

## Publication

- [ ] Confirm version 1.0.0 in the installer, About, and release notes.
- [ ] Run `py -3 .\pixel_shroom_phase10_release.py --verify` and confirm all PASS.
- [ ] Create annotated Git tag `v1.0.0` at the matching commit and push to the correct fork.
- [ ] Create a **draft** GitHub release with installer, source ZIP, checksums, release notes, and optional portable ZIP.
- [ ] Review the draft, then explicitly publish the release.
