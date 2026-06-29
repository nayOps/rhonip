package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import com.onip.biometric.R;
import com.onip.biometric.models.EmployeeData;
import com.onip.biometric.services.EmployeeApiService;

/**
 * Activité simplifiée pour l'enregistrement d'employé
 * Une seule étape avec les champs essentiels
 */
public class SimpleEmployeeActivity extends Activity {
    
    private static final String TAG = "SimpleEmployeeActivity";
    
    // Champs du formulaire
    private EditText editNin;
    private EditText editFirstName;
    private EditText editLastName;
    private EditText editMiddleName;
    private EditText editEmail;
    private EditText editPhone;
    private EditText editJobTitle;
    private EditText editDepartment;
    
    // Boutons
    private Button btnSave;
    private Button btnCancel;
    
    // Services
    private EmployeeApiService apiService;
    private EmployeeData employeeData;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_simple_employee);
        
        Log.d(TAG, "Initialisation de l'activité simplifiée");
        
        initializeViews();
        initializeData();
        setupListeners();
    }
    
    private void initializeViews() {
        // Champs du formulaire
        editNin = findViewById(R.id.edit_nin);
        editFirstName = findViewById(R.id.edit_first_name);
        editLastName = findViewById(R.id.edit_last_name);
        editMiddleName = findViewById(R.id.edit_middle_name);
        editEmail = findViewById(R.id.edit_email);
        editPhone = findViewById(R.id.edit_phone);
        editJobTitle = findViewById(R.id.edit_job_title);
        editDepartment = findViewById(R.id.edit_department);
        
        // Boutons
        btnSave = findViewById(R.id.btn_save);
        btnCancel = findViewById(R.id.btn_cancel);
        
        Log.d(TAG, "Vues initialisées");
    }
    
    private void initializeData() {
        employeeData = new EmployeeData();
        apiService = new EmployeeApiService(this);
        Log.d(TAG, "Données initialisées");
    }
    
    private void setupListeners() {
        btnSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveEmployee();
            }
        });
        
        btnCancel.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                finish();
            }
        });
        
        Log.d(TAG, "Listeners configurés");
    }
    
    private void saveEmployee() {
        Log.d(TAG, "=== DÉBUT SAUVEGARDE ===");
        
        try {
            // Collecter les données du formulaire
            collectFormData();
            
            // Afficher un message de chargement
            showToast("Enregistrement en cours...");
            
            // Envoyer les données vers l'API
            apiService.saveEmployee(employeeData, new EmployeeApiService.ApiCallback() {
                @Override
                public void onSuccess(String message) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            showToast(message);
                            Log.d(TAG, "Succès: " + message);
                            // Optionnel: retourner à l'activité précédente
                            // finish();
                        }
                    });
                }
                
                @Override
                public void onError(String error) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            showToast("Erreur: " + error);
                            Log.e(TAG, "Erreur: " + error);
                        }
                    });
                }
            });
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la sauvegarde: " + e.getMessage());
            showToast("Erreur: " + e.getMessage());
        }
    }
    
    private void collectFormData() {
        Log.d(TAG, "=== COLLECTE DES DONNÉES ===");
        
        try {
            // Collecter les données avec logs détaillés
            String nin = editNin.getText().toString().trim();
            String firstName = editFirstName.getText().toString().trim();
            String lastName = editLastName.getText().toString().trim();
            String middleName = editMiddleName.getText().toString().trim();
            String email = editEmail.getText().toString().trim();
            String phone = editPhone.getText().toString().trim();
            String jobTitle = editJobTitle.getText().toString().trim();
            String department = editDepartment.getText().toString().trim();
            
            Log.d(TAG, "NIN: '" + nin + "'");
            Log.d(TAG, "Prénom: '" + firstName + "'");
            Log.d(TAG, "Nom: '" + lastName + "'");
            Log.d(TAG, "Nom du milieu: '" + middleName + "'");
            Log.d(TAG, "Email: '" + email + "'");
            Log.d(TAG, "Téléphone: '" + phone + "'");
            Log.d(TAG, "Poste: '" + jobTitle + "'");
            Log.d(TAG, "Département: '" + department + "'");
            
            // Assigner les données
            employeeData.setNin(nin);
            employeeData.setFirstName(firstName);
            employeeData.setLastName(lastName);
            employeeData.setMiddleName(middleName);
            employeeData.setEmail(email);
            employeeData.setPhoneNumber(phone);
            employeeData.setJobTitle(jobTitle);
            employeeData.setDepartment(department);
            
            // Données biométriques simulées
            employeeData.setPhotoPath("/path/to/photo.jpg");
            employeeData.setFingerprintTemplate("template_data");
            employeeData.setFingerprintFinger("index_finger");
            employeeData.setBiometricEnrollmentDate("24 oct. 2025");
            employeeData.setBiometricEnrolled(true);
            employeeData.setNumberOfChildren(0);
            
            Log.d(TAG, "=== DONNÉES COLLECTÉES AVEC SUCCÈS ===");
            Log.d(TAG, "Prénom final: '" + employeeData.getFirstName() + "'");
            Log.d(TAG, "Nom final: '" + employeeData.getLastName() + "'");
            Log.d(TAG, "Email final: '" + employeeData.getEmail() + "'");
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données: " + e.getMessage());
            throw e;
        }
    }
    
    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
}
