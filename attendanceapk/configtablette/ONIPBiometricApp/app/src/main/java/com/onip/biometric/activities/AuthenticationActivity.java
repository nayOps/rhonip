package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import com.onip.biometric.R;

public class AuthenticationActivity extends Activity {
    
    private static final String TAG = "AuthenticationActivity";
    
    private ImageView logoImageView;
    private TextView titleTextView;
    private TextView descriptionTextView;
    private Button authenticateButton;
    private TextView statusTextView;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_authentication);
        
        initializeViews();
        setupUI();
    }
    
    private void initializeViews() {
        logoImageView = findViewById(R.id.logo_image);
        titleTextView = findViewById(R.id.title_text);
        descriptionTextView = findViewById(R.id.description_text);
        authenticateButton = findViewById(R.id.authenticate_button);
        statusTextView = findViewById(R.id.status_text);
    }
    
    private void setupUI() {
        // Configuration du titre et description
        titleTextView.setText("ONIP - Office National\nd'Identification de la Population");
        descriptionTextView.setText("Gestion des Ressources Humaines\nEnregistrement des Employés");
        
        // Configuration du bouton d'authentification - NAVIGATION DIRECTE
        authenticateButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                // Navigation directe vers le menu principal
                navigateToMainMenu();
            }
        });
        
        // Statut initial
        statusTextView.setText("Appuyez sur 'Authentification' pour continuer");
    }
    
    
    private void navigateToMainMenu() {
        Intent intent = new Intent(this, MainMenuActivity.class);
        startActivity(intent);
        finish();
    }
}
