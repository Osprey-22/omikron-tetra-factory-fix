@echo off
setlocal
title Omikron Tetra Factory Death Fix
echo.
echo  Omikron: The Nomad Soul - Tetra Factory Death Fix
echo  Changes 1 byte in MESHES\DECORS\STtra03.3DO (a backup is created).
echo.

set "GAMEDIR="
if exist "C:\Program Files (x86)\Steam\steamapps\common\Omikron\MESHES\DECORS\STtra03.3DO" set "GAMEDIR=C:\Program Files (x86)\Steam\steamapps\common\Omikron"
if exist "C:\GOG Games\Omikron The Nomad Soul\MESHES\DECORS\STtra03.3DO" set "GAMEDIR=C:\GOG Games\Omikron The Nomad Soul"

if defined GAMEDIR (
  echo  Found game at: %GAMEDIR%
  choice /M "  Use this folder"
  if errorlevel 2 set "GAMEDIR="
)
if not defined GAMEDIR (
  echo  Could not auto-detect the game. Example path:
  echo    C:\SteamLibrary\steamapps\common\Omikron
  echo.
  set /p "GAMEDIR=  Paste your Omikron folder path and press Enter: "
)

set "TARGET=%GAMEDIR%\MESHES\DECORS\STtra03.3DO"
if not exist "%TARGET%" (
  echo.
  echo  ERROR: could not find %TARGET%
  echo  Nothing was changed.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$p=$env:TARGET; $b=[IO.File]::ReadAllBytes($p);" ^
 "if($b.Length -lt 0x7C48B){Write-Host ' VERIFY FAILED: file too small - wrong file/version. Nothing changed.'; exit 1};" ^
 "$n=[Text.Encoding]::ASCII.GetString($b,0x7C484,7);" ^
 "if($n -ne 'TTain04'){Write-Host ' VERIFY FAILED: unexpected file layout - wrong file/version. Nothing changed.'; exit 1};" ^
 "if($b[0x7C478] -eq 0){Write-Host ' Already patched - nothing to do.'; exit 0};" ^
 "if($b[0x7C478] -ne 8){Write-Host ' VERIFY FAILED: unexpected byte value - nothing changed.'; exit 1};" ^
 "if(!(Test-Path ($p+'.orig'))){Copy-Item -LiteralPath $p -Destination ($p+'.orig'); Write-Host (' Backup written: '+$p+'.orig')};" ^
 "$b[0x7C478]=0; [IO.File]::WriteAllBytes($p,$b);" ^
 "Write-Host ' PATCHED OK - the train can no longer kill on contact.';" ^
 "Write-Host ' To undo: delete STtra03.3DO and rename STtra03.3DO.orig back.'"

echo.
pause