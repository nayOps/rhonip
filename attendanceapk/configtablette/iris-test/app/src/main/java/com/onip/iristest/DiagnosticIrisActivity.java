package com.onip.iristest;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Version de diagnostic pour identifier le problème de crash
 */
public class DiagnosticIrisActivity extends Activity {

    private static final String TAG = "DiagnosticIris";
    private TextView statusText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        try {
            Log.d(TAG, "=== DÉBUT DIAGNOSTIC ONCREATE ===");
            
            // Layout simple pour diagnostic
            statusText = new TextView(this);
            statusText.setText("Diagnostic en cours...");
            setContentView(statusText);
            
            Log.d(TAG, "Layout diagnostic créé");
            
            // Test 1: Vérifier la disponibilité des bibliothèques
            testNativeLibraries();
            
            // Test 2: Vérifier l'initialisation de l'interface
            testIrisInterface();
            
            Log.d(TAG, "=== FIN DIAGNOSTIC ONCREATE ===");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR CRITIQUE dans onCreate: " + e.getMessage(), e);
            updateStatus("ERREUR CRITIQUE: " + e.getMessage());
            Toast.makeText(this, "Erreur critique: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void testNativeLibraries() {
        try {
            Log.d(TAG, "Test 1: Vérification des bibliothèques natives");
            updateStatus("Test 1: Vérification des bibliothèques natives...");
            
            // Test 1.0: Vérifier l'existence des fichiers .so
            checkSoFiles();
            
            // Test 1.1: Vérifier gnustl_shared.so d'abord (dépendance)
            try {
                System.loadLibrary("gnustl_shared");
                Log.d(TAG, "✓ gnustl_shared.so chargée");
                updateStatus(getStatusText() + "\n✓ gnustl_shared.so chargée");
            } catch (UnsatisfiedLinkError e) {
                Log.e(TAG, "✗ Erreur gnustl_shared.so: " + e.getMessage());
                updateStatus(getStatusText() + "\n✗ gnustl_shared.so ERREUR: " + e.getMessage());
                return; // Arrêter si gnustl ne charge pas
            }
            
            // Test 1.2: Vérifier irisInterfaceJNI.so
            try {
                System.loadLibrary("irisInterfaceJNI");
                Log.d(TAG, "✓ irisInterfaceJNI.so chargée");
                updateStatus(getStatusText() + "\n✓ irisInterfaceJNI.so chargée");
            } catch (UnsatisfiedLinkError e) {
                Log.e(TAG, "✗ Erreur irisInterfaceJNI.so: " + e.getMessage());
                updateStatus(getStatusText() + "\n✗ irisInterfaceJNI.so ERREUR: " + e.getMessage());
                
                // Diagnostic détaillé
                String errorMsg = e.getMessage();
                if (errorMsg.contains("dlopen failed")) {
                    updateStatus(getStatusText() + "\n\n🔍 DIAGNOSTIC: dlopen failed");
                    updateStatus(getStatusText() + "\n- Vérifiez l'architecture (armeabi-v7a)");
                    updateStatus(getStatusText() + "\n- Vérifiez les dépendances manquantes");
                } else if (errorMsg.contains("library not found")) {
                    updateStatus(getStatusText() + "\n\n🔍 DIAGNOSTIC: library not found");
                    updateStatus(getStatusText() + "\n- Vérifiez le chemin jniLibs");
                    updateStatus(getStatusText() + "\n- Vérifiez le nom de la bibliothèque");
                }
            }
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR test bibliothèques: " + e.getMessage(), e);
            updateStatus(getStatusText() + "\nERREUR test bibliothèques: " + e.getMessage());
        }
    }

    private void checkSoFiles() {
        try {
            Log.d(TAG, "Vérification des fichiers .so");
            updateStatus(getStatusText() + "\n\nVérification des fichiers .so:");
            
            String[] soFiles = {
                "/data/app/" + getPackageName() + "/lib/arm/libgnustl_shared.so",
                "/data/app/" + getPackageName() + "/lib/arm/libirisInterfaceJNI.so"
            };
            
            for (String soFile : soFiles) {
                java.io.File file = new java.io.File(soFile);
                if (file.exists()) {
                    Log.d(TAG, "✓ Fichier trouvé: " + soFile);
                    updateStatus(getStatusText() + "\n✓ " + file.getName() + " trouvé");
                } else {
                    Log.e(TAG, "✗ Fichier manquant: " + soFile);
                    updateStatus(getStatusText() + "\n✗ " + file.getName() + " MANQUANT");
                }
            }
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR vérification fichiers: " + e.getMessage(), e);
            updateStatus(getStatusText() + "\nERREUR vérification fichiers: " + e.getMessage());
        }
    }

    private void testIrisInterface() {
        try {
            Log.d(TAG, "Test 2: Vérification de l'interface IrisInterface");
            updateStatus(getStatusText() + "\n\nTest 2: Interface IrisInterface...");
            
            // Test de création de l'interface
            IrisInterface irisInterface = new IrisInterface();
            Log.d(TAG, "✓ IrisInterface créée");
            updateStatus(getStatusText() + "\n✓ IrisInterface créée");
            
            // Test d'initialisation
            int ret = irisInterface.initialize();
            Log.d(TAG, "Initialize result: " + ret);
            updateStatus(getStatusText() + "\n✓ Initialize: " + ret);
            
            if (ret == 0) {
                // Test des méthodes statiques
                String deviceId = IrisInterface.getDeviceId();
                String cameraModel = IrisInterface.getCameraModelId();
                String version = IrisInterface.getMobIrisVersion();
                
                Log.d(TAG, "Device: " + deviceId + ", Camera: " + cameraModel + ", Version: " + version);
                updateStatus(getStatusText() + "\n✓ Device: " + deviceId + "\n✓ Camera: " + cameraModel + "\n✓ Version: " + version);
                
                Toast.makeText(this, "Interface iris fonctionnelle !", Toast.LENGTH_SHORT).show();
                
            } else {
                Log.e(TAG, "Erreur d'initialisation: " + ret);
                updateStatus(getStatusText() + "\n✗ Erreur d'initialisation: " + ret);
            }
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR test interface: " + e.getMessage(), e);
            updateStatus(getStatusText() + "\n✗ ERREUR interface: " + e.getMessage());
            Toast.makeText(this, "Erreur interface: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void updateStatus(String text) {
        if (statusText != null) {
            statusText.setText(text);
        }
    }

    private String getStatusText() {
        if (statusText != null) {
            return statusText.getText().toString();
        }
        return "";
    }
}
