package com.onip.biometric.activities;

import android.app.Activity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.biometric.R;
import com.onip.biometric.utils.ConfigManager;

import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;

public class SettingsActivity extends Activity {
    
    private static final String TAG = "SettingsActivity";
    
    private TextView titleTextView;
    private Button backButton;
    
    // Configuration backend
    private EditText editBackendIp;
    private EditText editBackendPort;
    private Button btnTestConnection;
    private Button btnSaveConfig;
    private TextView textConnectionStatus;
    
    private ConfigManager configManager;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        
        configManager = new ConfigManager(this);
        
        initializeViews();
        setupUI();
        loadCurrentConfig();
    }
    
    private void initializeViews() {
        titleTextView = findViewById(R.id.title_text);
        backButton = findViewById(R.id.back_button);
        
        editBackendIp = findViewById(R.id.edit_backend_ip);
        editBackendPort = findViewById(R.id.edit_backend_port);
        btnTestConnection = findViewById(R.id.btn_test_connection);
        btnSaveConfig = findViewById(R.id.btn_save_config);
        textConnectionStatus = findViewById(R.id.text_connection_status);
    }
    
    private void setupUI() {
        titleTextView.setText("Paramètres");
        
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
        
        btnTestConnection.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                testConnection();
            }
        });
        
        btnSaveConfig.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveConfig();
            }
        });
    }
    
    /**
     * Charge la configuration actuelle dans les champs
     */
    private void loadCurrentConfig() {
        editBackendIp.setText(configManager.getBackendIp());
        editBackendPort.setText(configManager.getBackendPort());
        textConnectionStatus.setText("Configuration actuelle: " + configManager.getBackendIp() + ":" + configManager.getBackendPort());
    }
    
    /**
     * Teste la connexion au backend
     */
    private void testConnection() {
        String ip = editBackendIp.getText().toString().trim();
        String port = editBackendPort.getText().toString().trim();
        
        if (ip.isEmpty() || port.isEmpty()) {
            Toast.makeText(this, "Veuillez remplir l'IP et le port", Toast.LENGTH_SHORT).show();
            return;
        }
        
        textConnectionStatus.setText("🔄 Test de connexion en cours...");
        btnTestConnection.setEnabled(false);
        
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String testUrl = "http://" + ip + ":" + port + "/api/test";
                    Log.d(TAG, "Test connexion à: " + testUrl);
                    
                    URL url = new URL(testUrl);
                    HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                    conn.setRequestMethod("GET");
                    conn.setConnectTimeout(5000);
                    conn.setReadTimeout(5000);
                    
                    int responseCode = conn.getResponseCode();
                    
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            btnTestConnection.setEnabled(true);
                            if (responseCode == 200) {
                                textConnectionStatus.setText("✅ Connexion réussie ! (Code: " + responseCode + ")");
                                textConnectionStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
                                Toast.makeText(SettingsActivity.this, "Connexion OK !", Toast.LENGTH_SHORT).show();
                            } else {
                                textConnectionStatus.setText("❌ Erreur de connexion (Code: " + responseCode + ")");
                                textConnectionStatus.setTextColor(getResources().getColor(android.R.color.holo_red_dark));
                                Toast.makeText(SettingsActivity.this, "Erreur: Code " + responseCode, Toast.LENGTH_SHORT).show();
                            }
                        }
                    });
                    
                } catch (Exception e) {
                    Log.e(TAG, "Erreur test connexion: " + e.getMessage());
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            btnTestConnection.setEnabled(true);
                            textConnectionStatus.setText("❌ Erreur: " + e.getMessage());
                            textConnectionStatus.setTextColor(getResources().getColor(android.R.color.holo_red_dark));
                            Toast.makeText(SettingsActivity.this, "Erreur: " + e.getMessage(), Toast.LENGTH_LONG).show();
                        }
                    });
                }
            }
        }).start();
    }
    
    /**
     * Sauvegarde la configuration
     */
    private void saveConfig() {
        String ip = editBackendIp.getText().toString().trim();
        String port = editBackendPort.getText().toString().trim();
        
        if (ip.isEmpty() || port.isEmpty()) {
            Toast.makeText(this, "Veuillez remplir l'IP et le port", Toast.LENGTH_SHORT).show();
            return;
        }
        
        // Validation basique de l'IP
        if (!isValidIp(ip)) {
            Toast.makeText(this, "Format d'IP invalide", Toast.LENGTH_SHORT).show();
            return;
        }
        
        // Validation du port
        try {
            int portNum = Integer.parseInt(port);
            if (portNum < 1 || portNum > 65535) {
                Toast.makeText(this, "Port invalide (1-65535)", Toast.LENGTH_SHORT).show();
                return;
            }
        } catch (NumberFormatException e) {
            Toast.makeText(this, "Port invalide", Toast.LENGTH_SHORT).show();
            return;
        }
        
        configManager.setBackendConfig(ip, port);
        textConnectionStatus.setText("✅ Configuration sauvegardée: " + ip + ":" + port);
        textConnectionStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
        Toast.makeText(this, "Configuration sauvegardée !", Toast.LENGTH_SHORT).show();
        
        Log.d(TAG, "Configuration sauvegardée: " + ip + ":" + port);
    }
    
    /**
     * Validation basique de l'IP
     */
    private boolean isValidIp(String ip) {
        if (ip == null || ip.isEmpty()) {
            return false;
        }
        String[] parts = ip.split("\\.");
        if (parts.length != 4) {
            return false;
        }
        for (String part : parts) {
            try {
                int num = Integer.parseInt(part);
                if (num < 0 || num > 255) {
                    return false;
                }
            } catch (NumberFormatException e) {
                return false;
            }
        }
        return true;
    }
}