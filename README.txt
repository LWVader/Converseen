PIXEL SHROOM IMAGE STUDIO — OFFICIAL LOGO ASSET KIT

Uses the uploaded Pixel Shroom Studio logo exactly as supplied. The small-icon
asset shows only the colored mushroom symbol so it remains recognizable at
Windows taskbar/Start-menu sizes. The supplied original full logo is included
for future About/splash artwork.

Files:
  PixelShroom_icon.png      512x512 image for res/icon.png (Qt app and About icon)
  PixelShroom_icon.ico      Windows multi-size icon 16,24,32,48,64,128,256
  PixelShroom_full_logo.png  Full original 1254x1254 logo for later branding
  install_pixel_shroom_brand_assets.py  Safe two-file installer

IMPORTANT: USER HAS NOT RUN FINAL REPACKAGING YET. THAT IS GOOD.
Do the following in this order, in Windows PowerShell:

1. Extract this ZIP INTO:
   C:\Users\bulls\Documents\Projects\Converseen

2. Close any running Image Studio windows.
   cd 'C:\Users\bulls\Documents\Projects\Converseen'
   py -3 .\install_pixel_shroom_brand_assets.py
   If DRY RUN PASSED:
   py -3 .\install_pixel_shroom_brand_assets.py --apply

3. Ensure prior Phase 8.1 source branding patch is applied (window title,
   web links, product metadata, etc.). If NOT already applied:
   py -3 .\pixel_shroom_branding.py
   If DRY RUN PASSED:
   py -3 .\pixel_shroom_branding.py --apply
   If it reports already branded, DO NOT run --apply a second time.
   (These are separate scripts: this ZIP installs icons only.)

4. In MSYS2 UCRT64:
   cd /c/Users/bulls/Documents/Projects/Converseen
   touch resources.qrc converseen.rc
   cmake -S . -B build-portable -G Ninja -DCMAKE_BUILD_TYPE=Release -DUSE_QT6=ON -DDISABLE_CHECK_UPDATES=ON '-DCMAKE_CXX_FLAGS=-DMAGICKCORE_HDRI_ENABLE=1 -DMAGICKCORE_QUANTUM_DEPTH=16 -DPIXELSHROOM_PORTABLE_BUILD'
   cmake --build build-portable --parallel 4

5. Back in PowerShell:
   cd 'C:\Users\bulls\Documents\Projects\Converseen'
   py -3 .\pixel_shroom_phase8_package.py

6. Launch the newly packaged executable, not the old copy:
   dist\PixelShroomImageStudio-Portable\PixelShroomImageStudio.exe
   Check taskbar/window icon, window title, About, no automatic redirect,
   JPEG/PNG/WebP conversion and 300 DPI metadata.

NOTES:
- Do not rename res/icon.png or res/converseen.ico; keeping these filenames
  means the existing resources.qrc and converseen.rc references still work.
- Source file named 'converseen.rc' and the icon resource filename may retain
  the upstream word Converseen internally. The VISIBLE product branding is
  supplied by the new artwork and the Phase 8.1 source branding patch.
- If Windows Explorer displays an old icon, verify you're testing the newly
  packaged executable; Windows may cache thumbnails/icons.
- Original code remains GPL-licensed. Keep copyright, credits, license,
  source-availability obligations when distributing your derivative.
- Full logo is provided as a separate asset; it is not automatically embedded
  in a splash screen. The mushroom app icon *is* embedded by the build.
