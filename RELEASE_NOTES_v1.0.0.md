# Pixel Shroom Image Studio v1.0.0

The first Pixel Shroom Image Studio Windows release, built from a modified Converseen image-converter fork.

## Included

- Batch image conversion among supported formats, including JPEG, PNG, and WebP.
- Pixel-accurate resizing and print presets, including 4800 × 4800 and 7200 × 7200 pixels.
- Print-resolution selection and verified 300-DPI PNG exports.
- Quality, smoothing, sharpening, and format-specific compression controls.
- Live preview, side-by-side original/export comparison, and linked zoom/pan.
- Configurable output folders.
- Pixel Shroom branding, Windows portable version, and per-user installer with uninstall support.

## Install

Download **PixelShroomImageStudio-Setup-1.0.0-Win64.exe** and run the installer on a 64-bit Windows system. It installs under the current user's application directory by default, and can create an optional desktop shortcut.

For a no-install option, extract **PixelShroomImageStudio-Portable-Win64.zip** (when attached) and run **PixelShroomImageStudio.exe** within its folder. Keep the accompanying DLLs and plugin subfolders intact.

## Print preparation

For 16 × 16-inch artwork at 300 DPI, export 4800 × 4800 pixels. For 24 × 24 inches at 300 DPI, export 7200 × 7200 pixels. Increasing pixels or setting DPI metadata does not guarantee increased original image detail. Confirm your printer's bleed, color, and file-format requirements.

## Source code, credits, and licenses

Pixel Shroom Image Studio is based on the open-source **Converseen** project by **Francesco Mondello**, with modifications by Pixel Shroom Studio. The Converseen-derived code remains subject to its applicable GPL license. The **PixelShroomImageStudio-v1.0.0-source.zip** archive provides the modified application source and build/package scripts for this version. See the source archive and bundled licensing materials for details.

Website: https://www.pixelshroomstudio.com/

## Release validation

The installer and image conversions have been tested on the development Windows machine. **Compatibility on a separate Windows machine without MSYS2/Qt/ImageMagick has not yet been confirmed.** This draft should not be published as a production-ready release until the release checklist is completed.

The installer is not digitally signed. Windows may display an unknown-publisher warning.
