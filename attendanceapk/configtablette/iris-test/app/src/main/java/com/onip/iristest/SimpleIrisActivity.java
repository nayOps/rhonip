package com.onip.iristest;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Version simple sans bibliothèques natives pour tester le crash
 */
public class SimpleIrisActivity extends Activity {

    private static final String TAG = "SimpleIris";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        try {
            Log.d(TAG, "=== DÉBUT SIMPLE IRIS ONCREATE ===");
            
            // Layout simple
            TextView textView = new TextView(this);
            textView.setText("✓ Application Simple Iris lancée avec succès !\n\n" +
                           "Cette version ne charge pas les bibliothèques natives.\n" +
                           "Si vous voyez ce message, le problème vient des bibliothèques JNI.");
            textView.setPadding(20, 20, 20, 20);
            setContentView(textView);
            
            Log.d(TAG, "Layout simple créé");
            Toast.makeText(this, "Application simple lancée !", Toast.LENGTH_SHORT).show();
            
            Log.d(TAG, "=== FIN SIMPLE IRIS ONCREATE ===");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR CRITIQUE dans onCreate: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur critique: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }
}
