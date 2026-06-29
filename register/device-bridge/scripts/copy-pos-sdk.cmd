@echo off
setlocal
set SRC=C:\Users\HYF\Documents\sdk\POS-SDK\SDK
set DST=%~dp0..\sdk\pos-x86
if not exist "%SRC%\POS_SDK.dll" (
  echo POS_SDK.dll introuvable dans %SRC%
  exit /b 1
)
if not exist "%DST%" mkdir "%DST%"
copy /Y "%SRC%\POS_SDK.dll" "%DST%\"
echo Copie OK: %DST%\POS_SDK.dll
exit /b 0
