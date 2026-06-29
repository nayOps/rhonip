# Build APK Enrôlement ONIP
Set-Location $PSScriptRoot
.\gradlew.bat assembleDebug
Write-Host "APK: app\build\outputs\apk\debug\enroll.apk"
