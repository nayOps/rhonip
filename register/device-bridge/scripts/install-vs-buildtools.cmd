@echo off
setlocal
echo Installation Visual Studio 2022 Build Tools + .NET Desktop (MSBuild COM)...
echo Duree typique: 15-30 min. Acceptez UAC si demande.
echo.

set "WINGET=%LOCALAPPDATA%\Microsoft\WindowsApps\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe\winget.exe"
if not exist "%WINGET%" set "WINGET=%LOCALAPPDATA%\Microsoft\WindowsApps\winget.exe"
if not exist "%WINGET%" (
    echo KO  winget absent - installez manuellement Build Tools 2022:
    echo https://visualstudio.microsoft.com/fr/downloads/#build-tools-for-visual-studio-2022
    echo Cochez: Developpement .NET Desktop
    pause
    exit /b 1
)

"%WINGET%" install -e --id Microsoft.VisualStudio.2022.BuildTools --accept-package-agreements --accept-source-agreements --override "--wait --passive --add Microsoft.VisualStudio.Workload.ManagedDesktopBuildTools --includeRecommended"

if errorlevel 1 (
    echo Note: deja installe ou pas de mise a jour - verifiez MSBuild puis build-camera-sidecar.cmd
) else (
    echo Installation terminee.
)

echo.
echo Lancez: build-camera-sidecar.cmd
pause
