package com.onip.cameratest;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AppCompatActivity;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import org.json.JSONObject;

public class ConnectivityTestActivity extends AppCompatActivity {

    private EditText editFirstName, editLastName, editEmail;
    private Button btnTestConnection, btnSendData;
    private TextView textStatus, textResponse;
    
    // URL du serveur Python (à modifier selon votre IP)
    private static final String SERVER_URL = "http://192.168.1.73:8082/api/test";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connectivity_test);
        
        initViews();
        setupListeners();
    }
    
    private void initViews() {
        editFirstName = findViewById(R.id.editFirstName);
        editLastName = findViewById(R.id.editLastName);
        editEmail = findViewById(R.id.editEmail);
        btnTestConnection = findViewById(R.id.btnTestConnection);
        btnSendData = findViewById(R.id.btnSendData);
        textStatus = findViewById(R.id.textStatus);
        textResponse = findViewById(R.id.textResponse);
    }
    
    private void setupListeners() {
        btnTestConnection.setOnClickListener(v -> testConnection());
        btnSendData.setOnClickListener(v -> sendData());
    }
    
    private void testConnection() {
        textStatus.setText("🔄 Test de connexion...");
        textResponse.setText("");
        
        new Thread(() -> {
            try {
                URL url = new URL(SERVER_URL);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("GET");
                conn.setConnectTimeout(5000);
                conn.setReadTimeout(5000);
                
                int responseCode = conn.getResponseCode();
                
                runOnUiThread(() -> {
                    if (responseCode == 200) {
                        textStatus.setText("✅ Connexion réussie !");
                        textResponse.setText("Serveur Python accessible");
                        Toast.makeText(this, "Connexion OK !", Toast.LENGTH_SHORT).show();
                    } else {
                        textStatus.setText("❌ Erreur de connexion");
                        textResponse.setText("Code: " + responseCode);
                    }
                });
                
            } catch (Exception e) {
                runOnUiThread(() -> {
                    textStatus.setText("❌ Erreur de connexion");
                    textResponse.setText("Erreur: " + e.getMessage());
                });
            }
        }).start();
    }
    
    private void sendData() {
        String firstName = editFirstName.getText().toString().trim();
        String lastName = editLastName.getText().toString().trim();
        String email = editEmail.getText().toString().trim();
        
        if (firstName.isEmpty() || lastName.isEmpty() || email.isEmpty()) {
            Toast.makeText(this, "Veuillez remplir tous les champs", Toast.LENGTH_SHORT).show();
            return;
        }
        
        textStatus.setText("📤 Envoi des données...");
        textResponse.setText("");
        
        new Thread(() -> {
            try {
                // Créer le JSON
                JSONObject jsonData = new JSONObject();
                jsonData.put("firstName", firstName);
                jsonData.put("lastName", lastName);
                jsonData.put("email", email);
                jsonData.put("timestamp", System.currentTimeMillis());
                
                // Envoyer la requête
                URL url = new URL(SERVER_URL);
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json; utf-8");
                conn.setRequestProperty("Accept", "application/json");
                conn.setDoOutput(true);
                conn.setConnectTimeout(10000);
                conn.setReadTimeout(10000);
                
                try (OutputStream os = conn.getOutputStream()) {
                    byte[] input = jsonData.toString().getBytes(StandardCharsets.UTF_8);
                    os.write(input, 0, input.length);
                }
                
                int responseCode = conn.getResponseCode();
                
                runOnUiThread(() -> {
                    if (responseCode == 200) {
                        textStatus.setText("✅ Données envoyées avec succès !");
                        textResponse.setText("Réponse du serveur: " + responseCode);
                        Toast.makeText(this, "Données envoyées !", Toast.LENGTH_SHORT).show();
                    } else {
                        textStatus.setText("❌ Erreur d'envoi");
                        textResponse.setText("Code: " + responseCode);
                    }
                });
                
            } catch (Exception e) {
                runOnUiThread(() -> {
                    textStatus.setText("❌ Erreur d'envoi");
                    textResponse.setText("Erreur: " + e.getMessage());
                });
            }
        }).start();
    }
}

