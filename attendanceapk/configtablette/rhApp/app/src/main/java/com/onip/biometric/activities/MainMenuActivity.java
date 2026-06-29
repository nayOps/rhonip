package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;

import com.onip.biometric.R;

public class MainMenuActivity extends Activity {
    
    private static final String TAG = "MainMenuActivity";
    
    private Button btnMarkAttendance;
    private Button btnRegisterEmployee;
    private Button btnSettings;
    private Button btnAbout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_menu);
        
        initializeViews();
        setupListeners();
    }
    
    private void initializeViews() {
        btnMarkAttendance = findViewById(R.id.btn_mark_attendance);
        btnRegisterEmployee = findViewById(R.id.btn_register_employee);
        btnSettings = findViewById(R.id.btn_settings);
        btnAbout = findViewById(R.id.btn_about);
    }
    
    private void setupListeners() {
        // Marquer Présence → Directement à AttendanceActivity
        btnMarkAttendance.setOnClickListener(v -> {
            Intent intent = new Intent(this, AttendanceActivity.class);
            startActivity(intent);
        });
        
        // Enregistrer Employé → Authentification par empreinte
        btnRegisterEmployee.setOnClickListener(v -> {
            Intent intent = new Intent(this, AuthActivity.class);
            startActivity(intent);
        });
        
        // Paramètres
        btnSettings.setOnClickListener(v -> {
            Intent intent = new Intent(this, SettingsActivity.class);
            startActivity(intent);
        });
        
        // À propos (pour l'instant, ne fait rien)
        btnAbout.setOnClickListener(v -> {
            // TODO: Afficher dialog "À propos"
        });
    }
}