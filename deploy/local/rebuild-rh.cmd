@echo off
REM Reconstruit l'image RH (apres ajout whitenoise ou autre dep dans requirements.txt)
setlocal
cd /d "%~dp0..\.."

if not exist .env (
  echo [INFO] Creation .env depuis .env.example
  copy /Y .env.example .env >nul
)

echo.
echo == Rebuild rh_server + rh_worker ==
docker compose --profile rh build rh_server rh_worker
if errorlevel 1 exit /b 1

echo.
echo == Redemarrage ==
docker compose --profile rh up -d rh_server rh_worker
if errorlevel 1 exit /b 1

echo.
echo == Verification ==
timeout /t 8 /nobreak >nul
curl -s -o nul -w "RH login HTTP %%{http_code}\n" http://localhost:8100/login/
curl -s -H "X-Guichet-Internal-Key: fgp_guichet_internal_dev" -o nul -w "API guichet HTTP %%{http_code}\n" http://localhost:8100/api/guichet/refs/

echo.
echo OK — http://localhost:8100/login/
pause
