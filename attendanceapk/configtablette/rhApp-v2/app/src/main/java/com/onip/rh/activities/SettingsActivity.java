package com.onip.rh.activities;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import com.onip.rh.R;
import com.onip.rh.utils.ConfigManager;

/**
 * Activité de configuration pour modifier l'IP et le port du backend
 */
public class SettingsActivity extends Activity {
    
    private static final String TAG = "SettingsActivity";
    
    private EditText editBackendIp;
    private EditText editBackendPort;
    private Button btnSave;
    private Button btnReset;
    private Button btnTest;
    private Button btnBack;
    private TextView txtStatus;
    
    private ConfigManager configManager;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        
        configManager = new ConfigManager(this);
        
        initializeViews();
        loadCurrentConfig();
        setupListeners();
    }
    
    private void initializeViews() {
        editBackendIp = findViewById(R.id.edit_backend_ip);
        editBackendPort = findViewById(R.id.edit_backend_port);
        btnSave = findViewById(R.id.btn_save_settings);
        btnReset = findViewById(R.id.btn_reset_settings);
        btnTest = findViewById(R.id.btn_test_connection);
        btnBack = findViewById(R.id.btn_back_settings);
        txtStatus = findViewById(R.id.txt_settings_status);
    }
    
    private void loadCurrentConfig() {
        editBackendIp.setText(configManager.getBackendIp());
        editBackendPort.setText(configManager.getBackendPort());
        txtStatus.setText("Configuration actuelle chargée");
    }
    
    private void setupListeners() {
        btnSave.setOnClickListener(v -> saveConfig());
        btnReset.setOnClickListener(v -> resetConfig());
        btnTest.setOnClickListener(v -> testConnection());
        btnBack.setOnClickListener(v -> finish());
    }
    
    private void saveConfig() {
        String ip = editBackendIp.getText().toString().trim();
        String port = editBackendPort.getText().toString().trim();
        
        if (ip.isEmpty() || port.isEmpty()) {
            Toast.makeText(this, "Veuillez remplir tous les champs", Toast.LENGTH_SHORT).show();
            return;
        }
        
        configManager.setBackendConfig(ip, port);
        txtStatus.setText("✅ Configuration sauvegardée\nIP: " + ip + "\nPort: " + port);
        Toast.makeText(this, "Configuration sauvegardée", Toast.LENGTH_SHORT).show();
        
        Log.d(TAG, "Configuration sauvegardée: " + ip + ":" + port);
    }
    
    private void resetConfig() {
        configManager.resetToDefault();
        loadCurrentConfig();
        txtStatus.setText("✅ Configuration réinitialisée aux valeurs par défaut");
        Toast.makeText(this, "Configuration réinitialisée", Toast.LENGTH_SHORT).show();
    }
    
    private void testConnection() {
        String ip = editBackendIp.getText().toString().trim();
        String port = editBackendPort.getText().toString().trim();
        
        if (ip.isEmpty() || port.isEmpty()) {
            Toast.makeText(this, "Veuillez remplir tous les champs", Toast.LENGTH_SHORT).show();
            return;
        }
        
        txtStatus.setText("Test de connexion en cours...");
        btnTest.setEnabled(false);
        
        new Thread(() -> {
            try {
                String urlString = "http://" + ip + ":" + port + "/api/test";
                Log.d(TAG, "Test connexion: " + urlString);
                
                java.net.URL url = new java.net.URL(urlString);
                java.net.HttpURLConnection connection = (java.net.HttpURLConnection) url.openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(5000);
                connection.setReadTimeout(5000);
                
                int responseCode = connection.getResponseCode();
                connection.disconnect();
                
                final boolean success = (responseCode == 200);
                final String message = success ? "✅ Connexion réussie" : "❌ Erreur HTTP: " + responseCode;
                
                runOnUiThread(() -> {
                    txtStatus.setText(message + "\n\nBackend: " + ip + ":" + port);
                    btnTest.setEnabled(true);
                    Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
                });
                
            } catch (java.net.ConnectException e) {
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Connexion refusée\n\nVérifiez que le backend est démarré sur " + ip + ":" + port);
                    btnTest.setEnabled(true);
                    Toast.makeText(this, "Connexion refusée", Toast.LENGTH_LONG).show();
                });
            } catch (java.net.UnknownHostException e) {
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Host inconnu\n\nIP invalide: " + ip);
                    btnTest.setEnabled(true);
                    Toast.makeText(this, "Host inconnu", Toast.LENGTH_LONG).show();
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Erreur: " + e.getMessage());
                    btnTest.setEnabled(true);
                    Toast.makeText(this, "Erreur: " + e.getMessage(), Toast.LENGTH_LONG).show();
                });
            }
        }).start();
    }
}

