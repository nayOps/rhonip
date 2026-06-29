# Build APK attendance (Windows) — sans Android Studio
# Prérequis : JDK 17+, Android SDK (sdk.dir dans local.properties)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot
$SdkJarSource = Join-Path $ProjectRoot "..\sdk\Customer_support_package-2.8\Code_Samples\Main_Demo\MorphoSmart_SDK_6.19.4.0\MorphoSmart_SDK_6.19.4.0.jar"
$LibsDir = Join-Path $ProjectRoot "app\libs"
$SdkJarTarget = Join-Path $LibsDir "MorphoSmart_SDK_6.19.4.0.jar"

if (-not (Test-Path $LibsDir)) {
    New-Item -ItemType Directory -Path $LibsDir | Out-Null
}

if (-not (Test-Path $SdkJarTarget)) {
    if (Test-Path $SdkJarSource) {
        Copy-Item $SdkJarSource $SdkJarTarget
        Write-Host "SDK Morpho copié vers app/libs/"
    } else {
        Write-Error @"
MorphoSmart_SDK_6.19.4.0.jar introuvable.
Copiez le JAR Morpho dans :
  $SdkJarTarget
Source attendue :
  $SdkJarSource
"@
    }
}

$localProps = Join-Path $ProjectRoot "local.properties"
if (-not (Test-Path $localProps)) {
    $sdkCandidates = @(
        $env:ANDROID_HOME,
        $env:ANDROID_SDK_ROOT,
        (Join-Path $env:LOCALAPPDATA "Android\Sdk"),
        "C:\Android\Sdk"
    ) | Where-Object { $_ -and (Test-Path $_) }

    if (-not $sdkCandidates) {
        Write-Error "Android SDK introuvable. Définissez ANDROID_HOME ou créez local.properties avec sdk.dir=..."
    }

    $sdkDir = ($sdkCandidates | Select-Object -First 1) -replace '\\', '/'
    "sdk.dir=$sdkDir" | Set-Content -Path $localProps -Encoding ASCII
    Write-Host "local.properties créé : sdk.dir=$sdkDir"
}

Push-Location $ProjectRoot
try {
    & .\gradlew.bat assembleDebug --no-daemon
    $apk = Join-Path $ProjectRoot "app\build\outputs\apk\debug\presence.apk"
    if (Test-Path $apk) {
        Write-Host ""
        Write-Host "APK généré : $apk"
    }
} finally {
    Pop-Location
}
