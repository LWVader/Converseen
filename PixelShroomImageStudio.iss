; Pixel Shroom Image Studio — Phase 9 Windows Installer
; Run via build_pixel_shroom_installer.py from the Converseen project root.
; This installer copies the EXISTING tested portable folder; it does not
; compile C++, collect DLLs or change the original development build.
;
; Stable AppId: DO NOT change in future releases; it allows in-place upgrades.
;
#define ProductName "Pixel Shroom Image Studio"
#define PublisherName "Pixel Shroom Studio"
#define ProductURL "https://www.pixelshroomstudio.com/"
#define ProductExecutable "PixelShroomImageStudio.exe"
#ifndef ProductVersion
  #define ProductVersion "1.0.0"
#endif
#ifndef PortableFolder
  #define PortableFolder AddBackslash(SourcePath) + "dist\PixelShroomImageStudio-Portable"
#endif
#ifndef InstallerOutFolder
  #define InstallerOutFolder AddBackslash(SourcePath) + "dist\installer"
#endif
#ifndef BrandIconFile
  #define BrandIconFile AddBackslash(SourcePath) + "PixelShroom_icon.ico"
#endif

[Setup]
AppId={{3CC4EF0E-8884-4454-A817-8B85D5B71E58}
AppName={#ProductName}
AppVersion={#ProductVersion}
AppVerName={#ProductName} {#ProductVersion}
AppPublisher={#PublisherName}
AppPublisherURL={#ProductURL}
AppSupportURL={#ProductURL}
AppUpdatesURL={#ProductURL}
DefaultDirName={localappdata}\Programs\Pixel Shroom Image Studio
DefaultGroupName={#ProductName}
DisableProgramGroupPage=yes
DisableDirPage=no
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir={#InstallerOutFolder}
OutputBaseFilename=PixelShroomImageStudio-Setup-{#ProductVersion}-Win64
SetupIconFile={#BrandIconFile}
UninstallDisplayIcon={app}\{#ProductExecutable}
UninstallDisplayName={#ProductName}
VersionInfoCompany={#PublisherName}
VersionInfoDescription={#ProductName} Windows Installer
VersionInfoProductName={#ProductName}
VersionInfoProductVersion={#ProductVersion}
VersionInfoVersion={#ProductVersion}
WizardStyle=modern
Compression=lzma2
SolidCompression=yes
CloseApplications=yes
RestartApplications=no
UsePreviousAppDir=yes
UsePreviousTasks=yes
; Never install to Program Files by default or touch users' artwork folders.

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Files]
; The entire portable dependency tree is required (Qt plugins, ImageMagick
; coder modules, XML, licenses). Only omit the developer-only test helper.
Source: "{#PortableFolder}\*"; DestDir: "{app}"; Excludes: "TEST_PORTABLE.cmd,PHASE8_PACKAGING_REPORT.txt"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#ProductName}"; Filename: "{app}\{#ProductExecutable}"; WorkingDir: "{app}"
Name: "{group}\Uninstall {#ProductName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#ProductName}"; Filename: "{app}\{#ProductExecutable}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#ProductExecutable}"; Description: "Launch {#ProductName}"; Flags: nowait postinstall skipifsilent
