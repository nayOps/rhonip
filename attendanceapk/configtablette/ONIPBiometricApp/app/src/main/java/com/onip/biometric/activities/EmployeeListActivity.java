package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.onip.biometric.R;

public class EmployeeListActivity extends Activity {
    
    private static final String TAG = "EmployeeListActivity";
    
    private TextView titleTextView;
    private Button backButton;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_employee_list);
        
        initializeViews();
        setupUI();
    }
    
    private void initializeViews() {
        titleTextView = findViewById(R.id.title_text);
        backButton = findViewById(R.id.back_button);
    }
    
    private void setupUI() {
        titleTextView.setText("Liste des Employés");
        
        backButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
    }
}