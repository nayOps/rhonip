@echo off
REM Lance IrisDeviceServer en admin dans une console visible (logs comme DeviceUI).
set "IRIS_BIN=C:\Users\HYF\Documents\sdk\iris\bin"
taskkill /f /im DeviceUI.exe >nul 2>&1
taskkill /f /im IrisDeviceServer.exe >nul 2>&1
timeout /t 2 /nobreak >nul
echo Demarrage console admin - acceptez UAC.
echo Dans la fenetre noire, cherchez: "JD5 is opened"
cd /d "%IRIS_BIN%"
mshta vbscript:CreateObject("Shell.Application").ShellExecute("cmd.exe","/k IrisDeviceServer.exe","%IRIS_BIN%","runas",1)(window.close)
echo.
echo Gardez cette fenetre serveur ouverte.
echo Puis: Device Bridge (dotnet run) - Analyse - Ouvrir lecteur.
pause
