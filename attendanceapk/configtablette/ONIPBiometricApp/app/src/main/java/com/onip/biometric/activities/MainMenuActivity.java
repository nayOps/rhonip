package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.onip.biometric.R;

public class MainMenuActivity extends Activity {
    
    private static final String TAG = "MainMenuActivity";
    
    private ImageView logoImageView;
    private TextView welcomeTextView;
    private Button addEmployeeButton;
    private Button viewEmployeesButton;
    private Button settingsButton;
    private Button logoutButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main_menu);
        
        initializeViews();
        setupUI();
    }
    
    private void initializeViews() {
        logoImageView = findViewById(R.id.logo_image);
        welcomeTextView = findViewById(R.id.welcome_text);
        addEmployeeButton = findViewById(R.id.add_employee_button);
        viewEmployeesButton = findViewById(R.id.view_employees_button);
        settingsButton = findViewById(R.id.settings_button);
        logoutButton = findViewById(R.id.logout_button);
    }
    
    private void setupUI() {
        // Message de bienvenue
        welcomeTextView.setText("Bienvenue dans le système\nde gestion des employés ONIP");
        
        // Configuration des boutons
        addEmployeeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startEmployeeEnrollment();
            }
        });
        
        viewEmployeesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                viewEmployees();
            }
        });
        
        settingsButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                openSettings();
            }
        });
        
        logoutButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                logout();
            }
        });
    }
    
    private void startEmployeeEnrollment() {
        Intent intent = new Intent(this, EmployeeEnrollmentActivity.class);
        startActivity(intent);
    }
    
    private void viewEmployees() {
        Intent intent = new Intent(this, EmployeeListActivity.class);
        startActivity(intent);
    }
    
    private void openSettings() {
        Intent intent = new Intent(this, SettingsActivity.class);
        startActivity(intent);
    }
    
    private void logout() {
        Intent intent = new Intent(this, AuthenticationActivity.class);
        intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TASK);
        startActivity(intent);
        finish();
    }
}