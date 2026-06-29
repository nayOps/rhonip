#!/bin/bash

echo "🎯 COMPILATION DE L'APK DE PRÉSENCE"
echo "=================================="

# Nettoyer et compiler
echo "🧹 Nettoyage du projet..."
./gradlew clean

echo "🔨 Compilation de l'APK..."
./gradlew assembleDebug

# Vérifier si l'APK a été créé
if [ -f "app/build/outputs/apk/debug/presence.apk" ]; then
    echo "✅ APK compilé avec succès !"
    echo "📱 Fichier: app/build/outputs/apk/debug/presence.apk"
    echo "📏 Taille: $(du -h app/build/outputs/apk/debug/presence.apk | cut -f1)"
    echo ""
    echo "🚀 Pour installer sur la tablette:"
    echo "   adb install app/build/outputs/apk/debug/presence.apk"
else
    echo "❌ Erreur: APK non trouvé"
    echo "📋 Vérifiez les logs de compilation ci-dessus"
fi


