package com.onip.biometric.activities;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.onip.biometric.R;

public class SettingsActivity extends Activity {
    
    private static final String TAG = "SettingsActivity";
    
    private TextView titleTextView;
    private Button backButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);
        
        initializeViews();
        setupUI();
    }
    
    private void initializeViews() {
        titleTextView = findViewById(R.id.title_text);
        backButton = findViewById(R.id.back_button);
    }
    
    private void setupUI() {
        titleTextView.setText("Paramètres");
        
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }
}