@echo off
setlocal
set BRIDGE_SDK=%~dp0..\sdk\fap60-x64
set DEMO_SDK=C:\Users\HYF\Documents\sdk\FAP60 Windows CSharp SDKV2.0.14C-2025091817\FAP60 Windows CSharp SDKV2.0.14C-2025091817\samplecode\FAP60Demo\Bin64

echo Bridge SdkPath (appsettings):
echo   %BRIDGE_SDK%
echo.
echo Demo Bin64 (FAP60Demo.exe):
echo   %DEMO_SDK%
echo.

fc /b "%BRIDGE_SDK%\FAP60-02.dll" "%DEMO_SDK%\FAP60-02.dll" >nul 2>&1
if %errorlevel%==0 (echo [OK] FAP60-02.dll identique) else (echo [!!] FAP60-02.dll DIFFERENT)

fc /b "%BRIDGE_SDK%\fingerprint.dll" "%DEMO_SDK%\fingerprint.dll" >nul 2>&1
if %errorlevel%==0 (echo [OK] fingerprint.dll identique) else (echo [!!] fingerprint.dll DIFFERENT)

if exist "%DEMO_SDK%\MXOpenSSLDll.dll" (
  if exist "%BRIDGE_SDK%\MXOpenSSLDll.dll" (
    echo [OK] MXOpenSSLDll.dll present dans bridge
  ) else (
    echo [MANQUE] MXOpenSSLDll.dll — lancez copy-fap60-sdk.cmd
  )
)

if exist "%BRIDGE_SDK%\license.dat" (echo [OK] license.dat) else (echo [--] license.dat absent dans bridge)

echo.
echo DLL bridge uniquement:
dir /b "%BRIDGE_SDK%\*.dll" 2>nul
echo.
echo DLL demo absentes du bridge:
for %%f in ("%DEMO_SDK%\*.dll") do if not exist "%BRIDGE_SDK%\%%~nxf" echo   MANQUE: %%~nxf
pause
