@echo off
setlocal
cd /d "%~dp0.."
call "%~dp0copy-pos-sdk.cmd"
if errorlevel 1 exit /b 1

taskkill /F /IM Fgp.PosPrinter.Bridge.exe 2>nul
echo === Build Fgp.PosPrinter.Bridge x86 ===
dotnet build src\Fgp.PosPrinter.Bridge\Fgp.PosPrinter.Bridge.csproj -c Debug
if errorlevel 1 exit /b 1

set "SRC=%~dp0..\src\Fgp.PosPrinter.Bridge\bin\Debug\net8.0"
set "DST=%~dp0..\src\Fgp.DeviceBridge.Api\bin\Debug\net8.0\pos-sidecar"
if not exist "%SRC%\Fgp.PosPrinter.Bridge.exe" (
    echo KO  Fgp.PosPrinter.Bridge.exe introuvable apres build
    exit /b 1
)

copy /Y "sdk\pos-x86\POS_SDK.dll" "%SRC%\" >nul 2>&1
if not exist "%DST%" mkdir "%DST%"
echo === Copie sidecar POS vers %DST% ===
xcopy /Y /E /I "%SRC%\*" "%DST%\"
echo OK  Sidecar POS copie (sans ecraser appsettings du Device Bridge)
echo Relancez: start-device-bridge.cmd
exit /b 0
