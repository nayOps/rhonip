@echo off
setlocal EnableExtensions
cd /d "%~dp0..\.."

set "VPS=adn@102.68.62.85"
set "KEY=fgp_guichet_internal_dev"
set "REMOTE=cd /home/adn/onip-rh 2>/dev/null || cd ~/rhonip; pwd; grep '^GUICHET_INTERNAL_API_KEY=' .env; sed -i 's|^GUICHET_INTERNAL_API_KEY=.*|GUICHET_INTERNAL_API_KEY=%KEY%|' .env; docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml --env-file .env --profile rh up -d --force-recreate rh_server; sleep 15; curl -s -o /dev/null -w 'guichet HTTP %%{http_code}\n' -H 'X-Guichet-Internal-Key: %KEY%' 'http://127.0.0.1:8100/api/guichet/employees/?page=1&page_size=1'"

echo.
echo  === Correction cle guichet sur le VPS ===
echo  Mot de passe SSH demande si pas de cle configuree.
echo.
ssh -o StrictHostKeyChecking=accept-new %VPS% "%REMOTE%"
if errorlevel 1 (
  echo.
  echo  ERREUR SSH. Executez manuellement sur le VPS :
  echo    sed -i 's/^GUICHET_INTERNAL_API_KEY=.*/GUICHET_INTERNAL_API_KEY=%KEY%/' .env
  echo    docker compose -f docker-compose.yml -f compose/prod.yml -f compose/prod.vps.yml --env-file .env --profile rh up -d --force-recreate rh_server
  pause
  exit /b 1
)

echo.
echo  === Recreation frontend local ===
docker compose --profile register up -d --force-recreate frontend

echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0check-guichet-docker.ps1"
echo.
pause
endlocal
