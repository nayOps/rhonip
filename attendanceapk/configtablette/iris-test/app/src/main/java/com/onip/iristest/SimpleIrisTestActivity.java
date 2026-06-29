package com.onip.iristest;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.widget.Button;
import android.widget.TextView;
import android.widget.Toast;

/**
 * Version ultra-simple pour tester le lancement
 */
public class SimpleIrisTestActivity extends Activity {

    private static final String TAG = "SimpleIrisTest";
    private TextView txtStatus;
    private Button btnTest;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        try {
            Log.d(TAG, "=== DÉBUT SIMPLE ONCREATE ===");
            
            // Layout ultra-simple
            setContentView(R.layout.activity_simple_iris_test);
            Log.d(TAG, "Layout simple chargé");
            
            // Views basiques
            txtStatus = findViewById(R.id.txt_simple_status);
            btnTest = findViewById(R.id.btn_simple_test);
            
            Log.d(TAG, "Views simples trouvées");
            
            // Test basique
            txtStatus.setText("✓ Application lancée avec succès !");
            btnTest.setOnClickListener(v -> {
                Toast.makeText(this, "Bouton test cliqué !", Toast.LENGTH_SHORT).show();
                txtStatus.setText("✓ Test réussi - Application fonctionne !");
            });
            
            Log.d(TAG, "=== FIN SIMPLE ONCREATE ===");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR dans SimpleIrisTest: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }
}


