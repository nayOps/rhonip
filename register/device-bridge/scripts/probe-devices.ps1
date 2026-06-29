# Teste le Device Bridge déjà lancé (sans le démarrer)
$bridgeUrl = "http://127.0.0.1:8765"

Write-Host "GET $bridgeUrl/health"
try {
    Invoke-RestMethod -Uri "$bridgeUrl/health" | ConvertTo-Json -Depth 5
}
catch {
    Write-Host "Bridge non joignable. Lancez d'abord: .\start-device-bridge.ps1" -ForegroundColor Red
    exit 1
}

Write-Host "`nPOST $bridgeUrl/api/v1/devices/fingerprint/probe"
Invoke-RestMethod -Uri "$bridgeUrl/api/v1/devices/fingerprint/probe" -Method Post | ConvertTo-Json -Depth 5

Write-Host "`nGET $bridgeUrl/api/v1/devices/iris/status"
try {
    Invoke-RestMethod -Uri "$bridgeUrl/api/v1/devices/iris/status" | ConvertTo-Json -Depth 5
}
catch {
    Write-Host "Iris: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`nPOST $bridgeUrl/api/v1/devices/iris/probe"
try {
    Invoke-RestMethod -Uri "$bridgeUrl/api/v1/devices/iris/probe" -Method Post | ConvertTo-Json -Depth 5
}
catch {
    Write-Host "Iris probe: $($_.Exception.Message)" -ForegroundColor Yellow
}
