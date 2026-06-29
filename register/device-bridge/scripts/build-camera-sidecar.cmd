@echo off
setlocal
cd /d "%~dp0"

echo === Enregistrement OCX (admin requis si echec) ===
if exist "C:\CameraGPSDK\Install.bat" (
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath 'C:\CameraGPSDK\Install.bat' -Verb RunAs -Wait"
) else (
    echo KO  C:\CameraGPSDK introuvable - installer CameraGPSDKsetup.exe
    exit /b 1
)

echo.
echo === Recherche MSBuild ===
set "MSBUILD="
for %%P in (
    "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
    "%ProgramFiles(x86)%\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    "%ProgramFiles%\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe"
    "%ProgramFiles%\Microsoft Visual Studio\2022\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
    "%ProgramFiles(x86)%\Microsoft Visual Studio\2019\BuildTools\MSBuild\Current\Bin\MSBuild.exe"
) do if exist %%P set "MSBUILD=%%~P"

if not defined MSBUILD (
    echo.
    echo KO  MSBuild introuvable.
    echo Installez Visual Studio 2022 Build Tools avec charge "Developpement .NET Desktop":
    echo   https://visualstudio.microsoft.com/fr/downloads/#build-tools-for-visual-studio-2022
    echo Puis relancez: build-camera-sidecar.cmd
    exit /b 1
)

echo OK  %MSBUILD%
echo.
echo === Build Fgp.CameraGp.Bridge x86 ===
"%MSBUILD%" "%~dp0..\src\Fgp.CameraGp.Bridge\Fgp.CameraGp.Bridge.csproj" /restore /p:Configuration=Debug
if errorlevel 1 exit /b 1

echo.
echo === Copie vers sortie Device Bridge Api ===
set "SRC=%~dp0..\src\Fgp.CameraGp.Bridge\bin\Debug\net8.0-windows"
set "DST=%~dp0..\src\Fgp.DeviceBridge.Api\bin\Debug\net8.0"
if not exist "%SRC%\Fgp.CameraGp.Bridge.exe" (
    echo KO  Fgp.CameraGp.Bridge.exe introuvable apres build
    exit /b 1
)
xcopy /Y /E /I "%SRC%\*" "%DST%\"
echo OK  Sidecar copie vers %DST%
echo.
echo Relancez: start-device-bridge.cmd puis verify-camera-gp.cmd
pause
