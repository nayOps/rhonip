@echo off
echo Sidecar COM (8766):
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { (Invoke-RestMethod 'http://127.0.0.1:8766/api/v1/devices/camera/devices' -TimeoutSec 5).devices | Format-Table id,name } catch { $_.Exception.Message }"
echo.
echo Bridge proxy (8765):
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-RestMethod 'http://127.0.0.1:8765/api/v1/devices/camera/status' -TimeoutSec 5 | ConvertTo-Json } catch { $_.Exception.Message }"
echo.
echo Port WebSocket GPY (9002):
netstat -ano | findstr ":9002" | findstr LISTENING
pause
