package com.onip.rh.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import com.onip.rh.RHApplication;
import com.onip.rh.R;

/**
 * Écran principal de l'application
 * Affiche 2 grandes cartes : Marquer Présence et Enregistrer Employé
 */
public class HomeActivity extends Activity {
    
    private static final String TAG = "HomeActivity";
    
    private Button btnMarkAttendance;
    private Button btnRegisterEmployee;
    private Button btnSettings;
    private TextView txtStatus;
    
    private RHApplication app;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        
        app = (RHApplication) getApplication();
        
        initializeViews();
        setupListeners();
        updateStatus();
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        updateStatus();
    }
    
    private void initializeViews() {
        btnMarkAttendance = findViewById(R.id.btn_mark_attendance);
        btnRegisterEmployee = findViewById(R.id.btn_register_employee);
        btnSettings = findViewById(R.id.btn_settings);
        txtStatus = findViewById(R.id.txt_home_status);
    }
    
    private void setupListeners() {
        // Marquer Présence → Directement à AttendanceActivity
        btnMarkAttendance.setOnClickListener(v -> {
            Log.d(TAG, "Navigation vers AttendanceActivity");
            Intent intent = new Intent(this, AttendanceActivity.class);
            startActivity(intent);
        });
        
        // Enregistrer Employé → Authentification puis formulaire
        btnRegisterEmployee.setOnClickListener(v -> {
            Log.d(TAG, "Navigation vers AuthActivity");
            Intent intent = new Intent(this, AuthActivity.class);
            startActivity(intent);
        });
        
        // Paramètres
        if (btnSettings != null) {
            btnSettings.setOnClickListener(v -> {
                Log.d(TAG, "Navigation vers SettingsActivity");
                Intent intent = new Intent(this, SettingsActivity.class);
                startActivity(intent);
            });
        }
    }
    
    private void updateStatus() {
        boolean deviceReady = app.isDeviceInitialized();
        boolean dataReady = app.isDataLoaded();
        int employeesCount = app.getGlobalEmployees().size();
        
        StringBuilder status = new StringBuilder();
        status.append("Capteur: ").append(deviceReady ? "✅" : "❌");
        status.append(" | Données: ").append(dataReady ? "✅" : "❌");
        status.append(" | Employés: ").append(employeesCount);
        
        txtStatus.setText(status.toString());
        
        // Activer/désactiver les boutons selon l'état
        btnMarkAttendance.setEnabled(deviceReady && dataReady);
        btnRegisterEmployee.setEnabled(deviceReady);
        
        Log.d(TAG, "Status: " + status.toString());
    }
}

