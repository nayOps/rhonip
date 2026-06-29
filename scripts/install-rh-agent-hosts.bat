@echo off
:: ============================================================
:: ONIP-RH — Acces local pour employes (test)
:: Double-clic (acceptez l'elevation admin), puis ouvrez :
::   http://rh.onip.gouv.local/login/
::
:: MODIFIEZ l'IP ci-dessous avant de distribuer ce fichier :
set SERVER_IP=192.168.10.104
:: ============================================================

net session >nul 2>&1
if %errorLevel% neq 0 (
    echo Demande des droits administrateur...
    powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "& '%~dp0rh-local-hosts.ps1' -Ip '%SERVER_IP%'"

ipconfig /flushdns >nul 2>&1

echo.
echo Termine. Ouvrez votre navigateur :
echo   http://rh.onip.gouv.local/login/
echo.
echo Identifiants de test :
echo   - E-mail pro OU matricule
echo   - Mot de passe initial : votre matricule
echo.
start http://rh.onip.gouv.local/login/
pause
