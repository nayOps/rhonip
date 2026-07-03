@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

REM 1) .env.local (RH VPS + cle guichet)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-guichet-env.ps1" %*
if errorlevel 1 (
  echo [AVERTISSEMENT] setup-guichet-env.ps1 a signale un probleme — verifiez frontend\.env.local
)

if not defined GUICHET_PORT set "GUICHET_PORT=3000"

where node >nul 2>&1
if errorlevel 1 (
  echo [ERREUR] Node.js introuvable. Installez Node 18+ puis relancez.
  pause
  exit /b 1
)

cd frontend
if not exist node_modules (
  echo Installation npm (premiere fois)...
  call npm install
  if errorlevel 1 exit /b 1
)

echo.
echo  Guichet ONIP local  -  http://localhost:%GUICHET_PORT%
echo  Config            -  frontend\.env.local
echo.
echo  Avant la photo :
echo    register\device-bridge\scripts\start-device-bridge.cmd
echo    register\scripts\start-icao-face-service.cmd
echo.

set PORT=%GUICHET_PORT%
call npm run dev

endlocal
