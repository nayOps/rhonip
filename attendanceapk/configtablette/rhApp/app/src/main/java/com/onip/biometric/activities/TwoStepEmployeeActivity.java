package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.biometric.R;
import com.onip.biometric.models.EmployeeData;
import com.onip.biometric.services.EmployeeApiService;
import com.onip.biometric.services.BiometricCaptureService;

import java.util.Map;

/**
 * Activité avec deux étapes pour l'enregistrement d'employé
 * Étape 1: Informations personnelles
 * Étape 2: Capture biométrique (photo + empreintes)
 */
public class TwoStepEmployeeActivity extends Activity {
    
    private static final String TAG = "TwoStepEmployeeActivity";
    private static final int STEP_PERSONAL_INFO = 1;
    private static final int STEP_BIOMETRIC = 2;
    
    // État actuel
    private int currentStep = STEP_PERSONAL_INFO;
    
    // Vues communes
    private TextView stepTitle;
    private TextView stepProgress;
    private Button btnPrevious;
    private Button btnNext;
    private Button btnSave;
    
    // Étape 1 - Informations personnelles
    private LinearLayout step1Layout;
    private EditText editNin;
    private EditText editFirstName;
    private EditText editLastName;
    private EditText editMiddleName;
    private EditText editEmail;
    private EditText editPhone;
    private EditText editJobTitle;
    private EditText editDepartment;
    private EditText editSalary;
    private EditText editHireDate;
    
    // Étape 2 - Capture biométrique
    private LinearLayout step2Layout;
    private ImageView imgPhotoPreview;
    private Button btnCapturePhoto;
    private TextView txtFingerprintStatus;
    private Button btnCaptureFingerprints;
    
    // Services
    private EmployeeApiService apiService;
    private BiometricCaptureService biometricService;
    private EmployeeData employeeData;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_two_step_employee);
        
        Log.d(TAG, "Initialisation de l'activité à deux étapes");
        
        initializeViews();
        initializeData();
        setupListeners();
        showStep(STEP_PERSONAL_INFO);
        
        // Initialiser le service biométrique
        biometricService.initialize();
    }
    
    private void initializeViews() {
        // Vues communes
        stepTitle = findViewById(R.id.step_title);
        stepProgress = findViewById(R.id.step_progress);
        btnPrevious = findViewById(R.id.btn_previous);
        btnNext = findViewById(R.id.btn_next);
        btnSave = findViewById(R.id.btn_save);
        
        // Étape 1 - Informations personnelles
        step1Layout = findViewById(R.id.step1_layout);
        editNin = findViewById(R.id.edit_nin);
        editFirstName = findViewById(R.id.edit_first_name);
        editLastName = findViewById(R.id.edit_last_name);
        editMiddleName = findViewById(R.id.edit_middle_name);
        editEmail = findViewById(R.id.edit_email);
        editPhone = findViewById(R.id.edit_phone);
        editJobTitle = findViewById(R.id.edit_job_title);
        editDepartment = findViewById(R.id.edit_department);
        editSalary = findViewById(R.id.edit_salary);
        editHireDate = findViewById(R.id.edit_hire_date);
        
        // Étape 2 - Capture biométrique
        step2Layout = findViewById(R.id.step2_layout);
        imgPhotoPreview = findViewById(R.id.img_photo_preview);
        btnCapturePhoto = findViewById(R.id.btn_capture_photo);
        txtFingerprintStatus = findViewById(R.id.txt_fingerprint_status);
        btnCaptureFingerprints = findViewById(R.id.btn_capture_fingerprints);
        
        Log.d(TAG, "Vues initialisées");
    }
    
    private void initializeData() {
        employeeData = new EmployeeData();
        apiService = new EmployeeApiService(this);
        
        // Initialiser le service biométrique
        biometricService = new BiometricCaptureService(this, new BiometricCaptureService.BiometricCallback() {
            @Override
            public void onPhotoCaptured(String photoPath) {
                runOnUiThread(() -> {
                    employeeData.setPhotoPath(photoPath);
                    imgPhotoPreview.setImageResource(R.drawable.ic_camera);
                    imgPhotoPreview.setVisibility(View.VISIBLE);
                    showToast("Photo capturée: " + photoPath);
                    Log.d(TAG, "Photo capturée: " + photoPath);
                });
            }
            
            @Override
            public void onFingerprintCaptured(String fingerName, byte[] template) {
                runOnUiThread(() -> {
                    showToast("Empreinte " + fingerName + " capturée");
                    Log.d(TAG, "Empreinte " + fingerName + " capturée: " + template.length + " bytes");
                });
            }
            
            @Override
            public void onAllFingerprintsCaptured(Map<String, byte[]> fingerprints) {
                runOnUiThread(() -> {
                    // Combiner tous les templates
                    StringBuilder allTemplates = new StringBuilder();
                    for (Map.Entry<String, byte[]> entry : fingerprints.entrySet()) {
                        allTemplates.append(entry.getKey()).append(":").append(entry.getValue().length).append(";");
                    }
                    
                    employeeData.setFingerprintTemplate(allTemplates.toString());
                    employeeData.setFingerprintFinger("all_fingers");
                    employeeData.setBiometricEnrolled(true);
                    
                    txtFingerprintStatus.setText("✅ 10 empreintes capturées avec succès");
                    txtFingerprintStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
                    showToast("Toutes les empreintes capturées !");
                    Log.d(TAG, "Toutes les empreintes capturées: " + fingerprints.size());
                });
            }
            
            @Override
            public void onError(String error) {
                runOnUiThread(() -> {
                    showToast("Erreur biométrique: " + error);
                    Log.e(TAG, "Erreur biométrique: " + error);
                });
            }
            
            @Override
            public void onProgress(String message) {
                runOnUiThread(() -> {
                    txtFingerprintStatus.setText(message);
                    Log.d(TAG, "Progrès biométrique: " + message);
                });
            }
        });
        
        Log.d(TAG, "Données initialisées");
    }
    
    private void setupListeners() {
        btnPrevious.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (currentStep == STEP_BIOMETRIC) {
                    showStep(STEP_PERSONAL_INFO);
                }
            }
        });
        
        btnNext.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (currentStep == STEP_PERSONAL_INFO) {
                    if (validateStep1()) {
                        collectStep1Data();
                        showStep(STEP_BIOMETRIC);
                    }
                }
            }
        });
        
        btnSave.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if (currentStep == STEP_BIOMETRIC) {
                    if (validateStep2()) {
                        collectStep2Data();
                        saveEmployee();
                    }
                }
            }
        });
        
        btnCapturePhoto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                capturePhoto();
            }
        });
        
        btnCaptureFingerprints.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                captureFingerprints();
            }
        });
        
        Log.d(TAG, "Listeners configurés");
    }
    
    private void showStep(int step) {
        currentStep = step;
        
        if (step == STEP_PERSONAL_INFO) {
            stepTitle.setText("Informations Personnelles");
            stepProgress.setText("Étape 1 sur 2");
            step1Layout.setVisibility(View.VISIBLE);
            step2Layout.setVisibility(View.GONE);
            btnPrevious.setVisibility(View.GONE);
            btnNext.setVisibility(View.VISIBLE);
            btnSave.setVisibility(View.GONE);
        } else if (step == STEP_BIOMETRIC) {
            stepTitle.setText("Capture Biométrique");
            stepProgress.setText("Étape 2 sur 2");
            step1Layout.setVisibility(View.GONE);
            step2Layout.setVisibility(View.VISIBLE);
            btnPrevious.setVisibility(View.VISIBLE);
            btnNext.setVisibility(View.GONE);
            btnSave.setVisibility(View.VISIBLE);
        }
        
        Log.d(TAG, "Affichage de l'étape " + step);
    }
    
    private boolean validateStep1() {
        Log.d(TAG, "Validation de l'étape 1");
        
        if (editFirstName.getText().toString().trim().isEmpty()) {
            showToast("Le prénom est requis");
            return false;
        }
        
        if (editLastName.getText().toString().trim().isEmpty()) {
            showToast("Le nom est requis");
            return false;
        }
        
        if (editEmail.getText().toString().trim().isEmpty()) {
            showToast("L'email est requis");
            return false;
        }
        
        if (editPhone.getText().toString().trim().isEmpty()) {
            showToast("Le téléphone est requis");
            return false;
        }
        
        return true;
    }
    
    private boolean validateStep2() {
        Log.d(TAG, "Validation de l'étape 2");
        
        if (employeeData.getPhotoPath() == null || employeeData.getPhotoPath().isEmpty()) {
            showToast("La photo est requise");
            return false;
        }
        
        if (employeeData.getFingerprintTemplate() == null || employeeData.getFingerprintTemplate().isEmpty()) {
            showToast("Les empreintes sont requises");
            return false;
        }
        
        return true;
    }
    
    private void collectStep1Data() {
        Log.d(TAG, "=== COLLECTE ÉTAPE 1 ===");
        
        try {
            String nin = editNin.getText().toString().trim();
            String firstName = editFirstName.getText().toString().trim();
            String lastName = editLastName.getText().toString().trim();
            String middleName = editMiddleName.getText().toString().trim();
            String email = editEmail.getText().toString().trim();
            String phone = editPhone.getText().toString().trim();
            String jobTitle = editJobTitle.getText().toString().trim();
            String department = editDepartment.getText().toString().trim();
            String salary = editSalary.getText().toString().trim();
            String hireDate = editHireDate.getText().toString().trim();
            
            Log.d(TAG, "NIN: '" + nin + "'");
            Log.d(TAG, "Prénom: '" + firstName + "'");
            Log.d(TAG, "Nom: '" + lastName + "'");
            Log.d(TAG, "Nom du milieu: '" + middleName + "'");
            Log.d(TAG, "Email: '" + email + "'");
            Log.d(TAG, "Téléphone: '" + phone + "'");
            Log.d(TAG, "Poste: '" + jobTitle + "'");
            Log.d(TAG, "Département: '" + department + "'");
            Log.d(TAG, "Salaire: '" + salary + "'");
            Log.d(TAG, "Date d'embauche: '" + hireDate + "'");
            
            // Assigner les données
            employeeData.setNin(nin);
            employeeData.setFirstName(firstName);
            employeeData.setLastName(lastName);
            employeeData.setMiddleName(middleName);
            employeeData.setEmail(email);
            employeeData.setPhoneNumber(phone);
            employeeData.setJobTitle(jobTitle);
            employeeData.setDepartment(department);
            employeeData.setGrossSalary(salary);
            employeeData.setHireDate(hireDate);
            
            Log.d(TAG, "=== DONNÉES ÉTAPE 1 COLLECTÉES ===");
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte étape 1: " + e.getMessage());
        }
    }
    
    private void collectStep2Data() {
        Log.d(TAG, "=== COLLECTE ÉTAPE 2 ===");
        
        try {
            // Données biométriques simulées
            employeeData.setPhotoPath("/path/to/photo.jpg");
            employeeData.setFingerprintTemplate("template_data_10_fingers");
            employeeData.setFingerprintFinger("all_fingers");
            employeeData.setBiometricEnrollmentDate("24 oct. 2025");
            employeeData.setBiometricEnrolled(true);
            employeeData.setNumberOfChildren(0);
            
            Log.d(TAG, "=== DONNÉES ÉTAPE 2 COLLECTÉES ===");
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte étape 2: " + e.getMessage());
        }
    }
    
    private void capturePhoto() {
        Log.d(TAG, "Capture de photo réelle");
        showToast("Capture de photo en cours...");
        
        // Capture réelle de photo
        biometricService.capturePhoto();
    }
    
    private void captureFingerprints() {
        Log.d(TAG, "Capture des empreintes réelles");
        showToast("Capture des 10 empreintes en cours...");
        
        // Capture réelle des empreintes
        biometricService.startFingerprintCapture();
    }
    
    private void saveEmployee() {
        Log.d(TAG, "=== DÉBUT SAUVEGARDE ===");
        
        try {
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
    
    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (biometricService != null) {
            biometricService.cleanup();
        }
    }
}
