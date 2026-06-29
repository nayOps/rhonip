# Licence algorithme FAP60 (`fingerprint.dll`)

Placez ici le fichier fourni par le fabricant / ONIP, par exemple :

- `license.dat` (recommandé)
- ou `fingerprint.license` (cache après `zzAuth`)

**Ne pas committer** ces fichiers (secrets liés au poste).

## Configuration bridge (`appsettings.Development.json`)

```json
"Fingerprint": {
  "LicenseFilePath": "license.dat",
  "RequireAlgorithmLicense": true
}
```

## Serveur licence (option)

Si vous avez un compte fournisseur :

```json
"TryLicenseServerOnMissingFile": true,
"LicenseServer": {
  "Ip": "183.129.171.153",
  "Port": 1902,
  "UserId": "VOTRE_ID",
  "Password": "VOTRE_CLE"
}
```

Le bridge enregistre alors `fingerprint.license` dans ce dossier.

## Mode dégradé (tests sans licence)

```json
"RequireAlgorithmLicense": false
```

→ OpenDevice + capture + aperçu live OK ; NFIQ désactivé.
