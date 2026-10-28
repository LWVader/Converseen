# Read-only verification for a local Converseen Phase 7 build.
param(
    [string]$ProjectRoot = (Join-Path $env:USERPROFILE 'Documents\Projects\Converseen'),
    [string]$OutputFolder = '',
    [string]$TestImage = ''
)
$ErrorActionPreference = 'Stop'
function Show-Path([string]$Label, [string]$Path, [bool]$MustExist = $true) {
    if (-not $Path) { return }
    $exists = Test-Path -LiteralPath $Path
    $status = if ($exists) { '[OK]' } else { '[MISSING]' }
    Write-Host "$status $Label : $Path"
    if ($MustExist -and -not $exists) { $script:Problems++ }
}
$Problems = 0
$ProjectRoot = [IO.Path]::GetFullPath($ProjectRoot)
Write-Host 'Pixel Shroom Converseen Phase 7 path check (read-only)'
Show-Path 'Project root' $ProjectRoot
$required = @('CMakeLists.txt', 'src\mainwindowimpl.cpp',
              'src\pixelshroom_phase6.h', 'src\pixelshroom_phase7.h', 'build\converseen.exe')
foreach ($rel in $required) { Show-Path $rel (Join-Path $ProjectRoot $rel) }
$ucrt = Join-Path $env:SystemDrive 'msys64\ucrt64\bin'
Show-Path 'MSYS2 UCRT64 executables' $ucrt
Show-Path 'CMake executable' (Join-Path $ucrt 'cmake.exe')
Show-Path 'Ninja executable' (Join-Path $ucrt 'ninja.exe')
$magick = Join-Path $ucrt 'magick.exe'
Show-Path 'ImageMagick executable' $magick
if ($OutputFolder) { Show-Path 'Selected output folder' $OutputFolder }
else { Write-Host '[INFO] Set the Save in folder in Converseen; use -OutputFolder to validate that path.' }
if ($TestImage) {
    Show-Path 'Test image' $TestImage
    if ((Test-Path -LiteralPath $TestImage) -and (Test-Path -LiteralPath $magick)) {
        Write-Host 'Export metadata:'
        & $magick identify -format "Dimensions: %wx%h`nDensity: %x x %y`nUnits: %[units]`n" $TestImage
    }
}
if ($Problems -gt 0) { Write-Host "$Problems path checks failed."; exit 1 }
Write-Host 'All required project and build paths exist.'
Write-Host 'NOTE: This validates files and paths, not a C++ compilation or GUI conversion test.'
