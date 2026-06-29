@echo off
setlocal
set "EXE=C:\CameraGPSDK\CameraGPSDK.exe"
if not exist "%EXE%" (
    echo KO  %EXE% introuvable - installer CameraGPSDKsetup.exe
    pause
    exit /b 1
)
echo Demarrage CameraGPSDK (service WebSocket port 9002)...
start "" "%EXE%"
timeout /t 3 /nobreak >nul
netstat -ano | findstr ":9002" | findstr LISTENING >nul 2>&1
if errorlevel 1 (
    echo INFO  Port 9002 pas encore ouvert - attendez l icone GPY dans la barre des taches
) else (
    echo OK  Port 9002 en ecoute
)
echo Branchez la XHY-D500 puis relancez la photo dans le guichet.
pause
