@echo off
setlocal
set "IRIS_BIN=C:\Users\HYF\Documents\sdk\iris\bin"
set "SCRIPT_DIR=%~dp0"

if not exist "%IRIS_BIN%\IrisDeviceServer.exe" (
    echo KO  IrisDeviceServer.exe introuvable: %IRIS_BIN%
    pause
    exit /b 1
)

echo [1/4] Fermeture DeviceUI / anciens serveurs...
taskkill /f /im DeviceUI.exe >nul 2>&1
taskkill /f /im IrisDeviceServer.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Demarrage IrisDeviceServer (UAC)...
cd /d "%IRIS_BIN%"
mshta vbscript:CreateObject("Shell.Application").ShellExecute("IrisDeviceServer.exe","","%IRIS_BIN%","runas",1)(window.close)
timeout /t 8 /nobreak >nul

echo [3/4] Test Capture + apercu live...
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%start-iris-server-admin-test.ps1"
set "TEST_RC=%ERRORLEVEL%"

echo.
if not "%TEST_RC%"=="0" (
    echo Si KO: start-iris-server-admin-console.bat pour voir les logs JD5.
)
echo Ne pas relancer start-iris-server.ps1 sans admin apres ce script.
echo Device Bridge : port 8765 - Analyse - Ouvrir lecteur.
pause
exit /b %TEST_RC%
