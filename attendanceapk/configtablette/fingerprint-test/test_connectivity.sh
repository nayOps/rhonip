#!/bin/bash

echo "🔍 Test de connectivité pour l'APK de Présence"
echo "=============================================="

echo "1. Test du backend Python..."
curl -s http://192.168.1.73:8082/api/data > /tmp/backend_test.json
if [ $? -eq 0 ]; then
    echo "✅ Backend Python accessible"
    echo "📊 Données disponibles:"
    cat /tmp/backend_test.json | jq '.total // "N/A"'
    echo "👥 Employés avec biométrie:"
    cat /tmp/backend_test.json | jq '.data[] | select(.biometricEnrolled == true) | {id, firstName, lastName}'
else
    echo "❌ Backend Python inaccessible"
    echo "💡 Solution: Démarrer le backend avec:"
    echo "   cd /home/nayops/Documents/architecture/connectivite/backend-python"
    echo "   python3 simple_server.py"
fi

echo ""
echo "2. Test du frontend Next.js..."
curl -s http://192.168.1.73:3001 > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Frontend Next.js accessible"
else
    echo "❌ Frontend Next.js inaccessible"
    echo "💡 Solution: Démarrer le frontend avec:"
    echo "   cd /home/nayops/Documents/architecture/glow/frontend"
    echo "   npm run dev"
fi

echo ""
echo "3. Test de l'APK..."
echo "📱 Pour tester l'APK:"
echo "   1. Compiler: ./gradlew assembleDebug"
echo "   2. Installer: adb install app/build/outputs/apk/debug/presence.apk"
echo "   3. Vérifier les logs: adb logcat | grep FingerprintTest"

echo ""
echo "🎯 URLs importantes:"
echo "   Backend: http://192.168.1.73:8082"
echo "   Frontend: http://192.168.1.73:3001"
echo "   API Data: http://192.168.1.73:8082/api/data"
echo "   API Attendance: http://192.168.1.73:8082/api/attendance"

