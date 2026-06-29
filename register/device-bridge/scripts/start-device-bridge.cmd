@echo off
setlocal
cd /d "%~dp0"

echo Verification SDK FAP60...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0copy-fap60-sdk.ps1"
if errorlevel 1 (
    echo.
    echo ERREUR: SDK FAP60 absent. Fermez toute instance du bridge ^(Ctrl+C^) puis relancez.
    exit /b 1
)

netstat -ano | findstr ":8765" | findstr "LISTENING" >nul 2>&1
if not errorlevel 1 (
    echo.
    echo ATTENTION: le port 8765 est deja utilise.
    echo Lancez d abord: stop-device-bridge.cmd
    echo Puis relancez start-device-bridge.cmd
    echo.
    pause
    exit /b 1
)

where dotnet >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERREUR: dotnet introuvable. Installez .NET 8 SDK puis rouvrez ce terminal.
    echo https://dotnet.microsoft.com/download/dotnet/8.0
    exit /b 1
)

echo.
dotnet --version
echo Device Bridge: http://127.0.0.1:8765
echo Dans un 2e terminal: probe-devices.cmd
echo.

set ASPNETCORE_ENVIRONMENT=Development
cd /d "%~dp0..\src\Fgp.DeviceBridge.Api"
dotnet run
