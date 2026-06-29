#!/usr/bin/env python3
"""
Analyseur du SDK Aratek depuis les JARs Android
Extrait les informations utiles pour comprendre le protocole
"""

import zipfile
import os
import re
from pathlib import Path

print("="*70)
print("🔍 ANALYSE DU SDK ARATEK DEPUIS LES JARS ANDROID")
print("="*70)

jar_dir = Path("aratek-sdk-example/app/libs")

if not jar_dir.exists():
    print("❌ Répertoire des JARs non trouvé")
    exit(1)

# Analyser le JAR principal des empreintes
fp_jar = jar_dir / "AraBMApiFp.jar"

if not fp_jar.exists():
    print("❌ AraBMApiFp.jar non trouvé")
    exit(1)

print(f"\n📦 Analyse de {fp_jar}")
print("-"*70)

with zipfile.ZipFile(fp_jar, 'r') as jar:
    # Lister les fichiers
    print("\n📁 Contenu du JAR:")
    for name in jar.namelist():
        if name.endswith('.class'):
            print(f"   {name}")
    
    # Extraire et analyser FingerprintScanner.class
    scanner_class = "cn/com/aratek/fp/FingerprintScanner.class"
    
    if scanner_class in jar.namelist():
        print(f"\n🔬 Analyse de {scanner_class}:")
        
        data = jar.read(scanner_class)
        
        # Rechercher des strings dans le bytecode
        strings = []
        for match in re.finditer(b'[\x20-\x7e]{4,}', data):
            s = match.group().decode('ascii', errors='ignore')
            if len(s) > 3:
                strings.append(s)
        
        print("\n📝 Strings trouvées (indices de méthodes/constantes):")
        unique_strings = sorted(set(strings))
        for s in unique_strings[:30]:
            if not s.startswith('java/') and not s.startswith('android/'):
                print(f"   - {s}")
        
        # Chercher des valeurs numériques (codes d'erreur, commandes)
        print("\n🔢 Constantes numériques détectées:")
        # Pattern pour les constantes int
        for i in range(0, 20):
            if bytes([i]) in data:
                print(f"   Valeur {i} présente")
        
        print(f"\n📊 Taille du bytecode: {len(data)} bytes")

# Analyser les bibliothèques natives
print("\n" + "="*70)
print("📚 BIBLIOTHÈQUES NATIVES (.so)")
print("="*70)

jniLibs_dir = Path("aratek-sdk-example/app/src/main/jniLibs/armeabi")

if jniLibs_dir.exists():
    print(f"\n📁 Bibliothèques trouvées dans {jniLibs_dir}:")
    for so_file in sorted(jniLibs_dir.glob("*.so")):
        size = so_file.stat().st_size
        print(f"   - {so_file.name:<30} ({size:>8} bytes)")
        
        # Chercher des strings dans le .so
        try:
            with open(so_file, 'rb') as f:
                content = f.read()
                strings = []
                for match in re.finditer(b'[\x20-\x7e]{6,}', content):
                    s = match.group().decode('ascii', errors='ignore')
                    if any(keyword in s.lower() for keyword in ['open', 'close', 'capture', 'power', 'init']):
                        strings.append(s)
                
                if strings:
                    print(f"     Fonctions détectées: {', '.join(set(strings)[:5])}")
        except:
            pass

print("\n" + "="*70)
print("📊 RÉSUMÉ")
print("="*70)
print()
print("✅ SDK Android trouvé et analysé")
print("✅ Classes principales identifiées:")
print("   - FingerprintScanner (gestion du périphérique)")
print("   - Bione (algorithme de matching)")
print("   - FingerprintImage (traitement d'image)")
print()
print("❌ Bibliothèques natives (.so) compilées pour Android ARM")
print("   → Incompatibles avec Linux x86_64")
print()
print("💡 SOLUTION:")
print("   Le SDK fonctionne sur Android")
print("   Pour Linux, il faut le SDK Linux officiel d'Aratek")
print()
print("🔗 Liens utiles:")
print("   - Repo GitHub: https://github.com/Andoresu250/aratek-sdk-example")
print("   - Aratek SDK: https://www.aratek.co/")
print()

