@echo off
setlocal EnableExtensions
if not defined ICAO_FACE_PORT set "ICAO_FACE_PORT=50270"

echo Arret du service ICAO sur le port %ICAO_FACE_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-icao-face-service.ps1"
endlocal
exit /b %ERRORLEVEL%
