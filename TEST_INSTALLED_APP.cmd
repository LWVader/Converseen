@echo off
setlocal EnableExtensions
set "APP=%LOCALAPPDATA%\Programs\Pixel Shroom Image Studio\PixelShroomImageStudio.exe"
set "FORMATS=%TEMP%\pixelshroom_v1_formats.txt"
set "ERRORS=%TEMP%\pixelshroom_v1_errors.txt"
echo Pixel Shroom Image Studio — clean Windows smoke test
echo ------------------------------------------------------
if not exist "%APP%" (
  echo FAIL: Installed executable not found at:
  echo   %APP%
  echo Install the Phase 9 setup package first, or change APP to its install path.
  pause
  exit /b 2
)
rem No MSYS2, ImageMagick or Qt from the developer's PATH.
set "PATH=%SystemRoot%\System32;%SystemRoot%"
"%APP%" --supported-formats > "%FORMATS%" 2> "%ERRORS%"
if errorlevel 1 (
  echo FAIL: Could not enumerate image formats.
  echo Error log: %ERRORS%
  type "%ERRORS%"
  pause
  exit /b 3
)
for %%F in (JPEG PNG WEBP) do (
  findstr /I /C:"%%F" "%FORMATS%" >nul
  if errorlevel 1 (
    echo FAIL: Missing %%F in supported format list.
    pause
    exit /b 4
  ) else (
    echo PASS: %%F supported
  )
)
echo.
echo PASS: Installed application and core image-format registry load.
echo NEXT: Open Image Studio from the Start Menu, convert one image of each
 echo format, check a 4800x4800 300-DPI PNG, and test uninstall.
echo Saved logs: %FORMATS% and %ERRORS%
pause
exit /b 0
