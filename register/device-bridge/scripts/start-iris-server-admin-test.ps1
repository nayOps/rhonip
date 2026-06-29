# Suite a start-iris-server-admin.bat : declenche Capture et sonde le JD5.
param(
    [string]$BaseUrl = "http://127.0.0.1:50219"
)

$ErrorActionPreference = "Continue"
$ok = $false

Write-Host "Declenchement Capture (session JD5)..." -ForegroundColor Cyan
$body = '{"mode":1,"eye":3,"timeout_seconds":12,"exposure":0,"quality":60,"fake_eye_enable":0,"lens_eye_enable":0}'
$captureJob = Start-Job -ScriptBlock {
    param($url, $json)
    try {
        Invoke-RestMethod -Uri "$url/device/Capture" -Method POST -Body $json -ContentType "text/plain" -TimeoutSec 60
    } catch {
        $_.Exception.Message
    }
} -ArgumentList $BaseUrl, $body

Start-Sleep -Seconds 2
Write-Host "Placez les yeux devant le lecteur (environ 20 s)..." -ForegroundColor Yellow

$liveUrl = "$BaseUrl/image/living/left.bmp?width=320&height=240"
for ($i = 0; $i -lt 25; $i++) {
    try {
        $img = Invoke-WebRequest -Uri $liveUrl -TimeoutSec 3 -UseBasicParsing
        if ($img.RawContentLength -gt 200) {
            Write-Host "Live OK ($($img.RawContentLength) octets)" -ForegroundColor Green
            $ok = $true
            break
        }
    } catch {
        # retry
    }

    try {
        $m = Invoke-RestMethod -Uri "$BaseUrl/device/Model" -Method POST -Body "{}" -ContentType "text/plain" -TimeoutSec 5
        if ($m.model) {
            Write-Host "Model: $($m.model)" -ForegroundColor Green
            $ok = $true
            break
        }
    } catch {
        # retry
    }

    Start-Sleep -Milliseconds 800
}

try {
    Invoke-RestMethod -Uri "$BaseUrl/device/Stop" -Method POST -Body "" -ContentType "text/plain" -TimeoutSec 5 | Out-Null
} catch {
    # ignore
}

if ($captureJob.State -eq "Running") {
    Stop-Job $captureJob -ErrorAction SilentlyContinue
    Remove-Job $captureJob -Force -ErrorAction SilentlyContinue
}

Write-Host ""
if ($ok) {
    Write-Host "OK  JD5 actif - redemarrez Device Bridge (dotnet run) puis Ouvrir lecteur." -ForegroundColor Green
    exit 0
}

Write-Host "KO  Pas d'aperçu live / model vide." -ForegroundColor Red
Write-Host "    Utilisez start-iris-server-admin-console.bat et cherchez 'JD5 is opened' dans la console." -ForegroundColor Yellow
exit 1
