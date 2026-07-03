@echo off
REM Guichet register en Docker (poste operateur) + RH sur VPS distant
setlocal EnableExtensions
cd /d "%~dp0..\.."

if not exist .env (
  echo [ERREUR] .env absent a la racine du mono-repo.
  echo Copiez .env.example vers .env puis ajoutez les lignes de compose\register.guichet-vps.env.example
  pause
  exit /b 1
)

echo.
echo  Demarrage register Docker (frontend :3000) ...
echo  RH cible : voir NEXT_PUBLIC_RH_API_URL / RH_INTERNAL_API_URL dans .env
echo.

docker compose --profile register up -d --build frontend enrollment_gateway fgp_core fingerprint_service
if errorlevel 1 exit /b 1

echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check-guichet-docker.ps1"
echo.
pause
endlocal
