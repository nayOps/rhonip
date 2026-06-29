@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

set "SVC_DIR=%CD%\icao-face-service"
set "VENV=%SVC_DIR%\.venv"
if not defined ICAO_FACE_PORT set "ICAO_FACE_PORT=50270"

set "PY_EXE="

REM py -3 (launcher Windows / python.org)
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
  for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "PY_EXE=%%P"
)

REM python direct
if not defined PY_EXE (
  python -c "import sys" >nul 2>&1
  if not errorlevel 1 (
    for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "PY_EXE=%%P"
  )
)

if not defined PY_EXE (
  echo.
  echo  [ERREUR] Python 3.10+ introuvable.
  echo.
  echo  Dans PowerShell, testez :   py -3 --version
  echo  Si OK, relancez :          .\start-icao-face-service.cmd
  echo.
  echo  Sinon installez Python : https://www.python.org/downloads/
  echo  Cochez "Add python.exe to PATH", puis redemarrez PowerShell.
  echo.
  pause
  exit /b 1
)

echo Python detecte : %PY_EXE%

if not exist "%VENV%\Scripts\python.exe" (
  echo Creation de l'environnement virtuel...
  "%PY_EXE%" -m venv "%VENV%"
  if errorlevel 1 (
    echo Echec creation venv.
    pause
    exit /b 1
  )
  echo Installation des dependances ^(peut prendre plusieurs minutes^)...
  "%VENV%\Scripts\python.exe" -m pip install --upgrade pip
  "%VENV%\Scripts\pip.exe" install -r "%SVC_DIR%\requirements.txt"
  if errorlevel 1 (
    echo Echec pip install - verifiez la connexion Internet.
    pause
    exit /b 1
  )
)

echo.
echo Verification du port %ICAO_FACE_PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-RestMethod -Uri 'http://127.0.0.1:%ICAO_FACE_PORT%/health' -TimeoutSec 3; if ($r.status -eq 'ok') { Write-Host ''; Write-Host '  [OK] Service ICAO deja actif.' -ForegroundColor Green; Write-Host '       http://127.0.0.1:%ICAO_FACE_PORT%/health'; Write-Host '       Actualisez la page Photo - pas besoin de relancer.'; Write-Host ''; exit 0 } exit 1 } catch { exit 1 }"
if not errorlevel 1 (
  pause
  exit /b 0
)

set "ICAO_PORT_SELECTED="
for %%P in (%ICAO_FACE_PORT% 50300 50420 50520) do (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=%%P; try { $l=[System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Parse('127.0.0.1'),$p); $l.Start(); $l.Stop(); exit 0 } catch { exit 1 }" >nul 2>&1
  if not errorlevel 1 (
    set "ICAO_PORT_SELECTED=%%P"
    goto :port_found
  )
)

echo.
echo  [ERREUR] Aucun port disponible pour ICAO (tests: %ICAO_FACE_PORT%,50300,50420,50520).
echo  Essayez en admin ou changez: set ICAO_FACE_PORT=50620
echo.
pause
exit /b 1

:port_found
if not "%ICAO_PORT_SELECTED%"=="%ICAO_FACE_PORT%" (
  echo  [INFO] Port %ICAO_FACE_PORT% indisponible, bascule auto sur %ICAO_PORT_SELECTED%.
)
set "ICAO_FACE_PORT=%ICAO_PORT_SELECTED%"

echo ICAO Face Service - http://127.0.0.1:%ICAO_FACE_PORT%
echo Laissez cette fenetre ouverte pendant l'enrolement photo.
echo Si erreur 10013 : Windows peut bloquer certains ports. Le script essaie plusieurs ports automatiquement.
echo.
cd /d "%SVC_DIR%"
"%VENV%\Scripts\python.exe" -m app.main
endlocal
