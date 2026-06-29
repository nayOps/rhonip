@echo off
echo Arret Device Bridge et sidecars (camera, POS)...
taskkill /F /IM Fgp.DeviceBridge.Api.exe 2>nul
taskkill /F /IM Fgp.CameraGp.Bridge.exe 2>nul
taskkill /F /IM Fgp.PosPrinter.Bridge.exe 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8765" ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8766" ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8767" ^| findstr LISTENING') do taskkill /F /PID %%a 2>nul
echo OK - vous pouvez rebuild ou relancer start-device-bridge.cmd
pause
