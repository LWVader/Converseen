PIXEL SHROOM IMAGE STUDIO — PORTABLE WINDOWS TEST RELEASE
=======================================================

This is a portable TEST build derived from Converseen, not an installer.

HOW TO START
1. Extract the ENTIRE folder from the ZIP (do not extract only the EXE).
2. Double-click PixelShroomImageStudio.exe.
3. Use JPEG, PNG, and WebP first; the bundled ImageMagick coder set is
   intentionally smaller than the full developer installation.
4. If startup fails, double-click TEST_PORTABLE.cmd; read the error log in
   your Windows %TEMP% folder. It deliberately uses a clean Windows PATH.

PORTABLE FILES
PixelShroomImageStudio.exe   Application
Qt6*.dll                    Qt libraries (plus other required runtime DLLs)
platforms/qwindows.dll      Qt Windows platform plugin
modules/coders/             ImageMagick supported image modules (plus magick.la index)
imagemagick/config/         ImageMagick XML settings
qt.conf                     Qt portable plugin discovery

TESTING CHECKLIST
[ ] Launch without an MSYS2 UCRT64 terminal.
[ ] Run TEST_PORTABLE.cmd and confirm JPEG, PNG and WEBP appear.
[ ] Open one JPEG, PNG and WebP and convert each to a fresh output folder.
[ ] Test Live Preview and Compare Output.
[ ] Export PNG 4800x4800 @ 300 DPI; verify density and dimensions.
[ ] Move the whole extracted folder elsewhere and launch again.
[ ] Test on a clean Windows PC without MSYS2 if distributing to others.

IMPORTANT LIMITATIONS
- PDF, HEIC, EXR, FLIF and many nonessential ImageMagick delegates are NOT
  included in this first portable build. Only tested formats should be
  advertised as supported.
- Do not move the EXE away from its bundled DLLs and subfolders.
- This build has not been code-signed or tested on a clean Windows PC.
- See source repository and bundled license files before redistribution.
- Converseen is GPL licensed. Redistributing a modified app requires
  fulfilling applicable GPL source, license and attribution obligations.
  Third-party Qt/ImageMagick and DLL dependency licenses also apply.
