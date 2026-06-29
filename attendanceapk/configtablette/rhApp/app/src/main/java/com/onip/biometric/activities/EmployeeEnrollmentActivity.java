package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.biometric.R;
import com.onip.biometric.models.EmployeeData;
import com.onip.biometric.services.EmployeeApiService;
public class EmployeeEnrollmentActivity extends Activity {
    
    private static final String TAG = "EmployeeEnrollmentActivity";
    
    // Étapes du formulaire
    public enum FormStep {
        IDENTITY(0, "Identité"),
        ORIGIN(1, "Origine"),
        ADDRESS(2, "Adresse"),
        FAMILY(3, "Situation Familiale"),
        EDUCATION(4, "Formation"),
        PROFESSIONAL(5, "Informations Professionnelles"),
        DOCUMENTS(6, "Documents"),
        EMERGENCY(7, "Contact d'Urgence"),
        BANKING(8, "Informations Bancaires"),
        MEDICAL(9, "Informations Médicales"),
        EQUIPMENT(10, "Équipements"),
        BIOMETRIC(11, "Données Biométriques");
        
        private final int stepNumber;
        private final String stepName;
        
        FormStep(int stepNumber, String stepName) {
            this.stepNumber = stepNumber;
            this.stepName = stepName;
        }
        
        public int getStepNumber() { return stepNumber; }
        public String getStepName() { return stepName; }
    }
    
    private FormStep currentStep = FormStep.IDENTITY;
    private EmployeeData employeeData;
    
    // Views
    private TextView stepTitleTextView;
    private TextView stepDescriptionTextView;
    private ProgressBar progressBar;
    private TextView progressTextView;
    private Button previousButton;
    private Button nextButton;
    private Button saveButton;
    private Button cancelButton;
    
    // Container pour les étapes
    private ViewGroup stepContainer;
    
    // Variables pour la gestion des enfants
    private LinearLayout childrenContainer;
    private Button addChildButton;
    private int childCount = 0;
    
    // Variables pour la gestion des documents
    private Spinner documentTypeSpinner;
    private Spinner numberTypeSpinner;
    private LinearLayout documentFieldsContainer;
    private LinearLayout numberFieldsContainer;
    
    // Service API
    private EmployeeApiService apiService;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_employee_enrollment);
        
        initializeViews();
        initializeData();
        setupUI();
        updateStepDisplay();
    }
    
    private void initializeViews() {
        stepTitleTextView = findViewById(R.id.step_title);
        stepDescriptionTextView = findViewById(R.id.step_description);
        progressBar = findViewById(R.id.progress_bar);
        progressTextView = findViewById(R.id.progress_text);
        previousButton = findViewById(R.id.previous_button);
        nextButton = findViewById(R.id.next_button);
        saveButton = findViewById(R.id.save_button);
        cancelButton = findViewById(R.id.cancel_button);
        stepContainer = findViewById(R.id.step_container);
    }
    
    private void initializeData() {
        employeeData = new EmployeeData();
        apiService = new EmployeeApiService(this);
        Log.d(TAG, "Données employé initialisées");
    }
    
    private void setupUI() {
        // Configuration des boutons
        previousButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                goToPreviousStep();
            }
        });
        
        nextButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                goToNextStep();
            }
        });
        
        saveButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                saveEmployee();
            }
        });
        
        cancelButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                cancelEnrollment();
            }
        });
        
        // Masquer le bouton précédent pour la première étape
        updateButtonVisibility();
    }
    
    private void updateStepDisplay() {
        stepTitleTextView.setText(currentStep.getStepName());
        stepDescriptionTextView.setText(getStepDescription(currentStep));
        
        // Mise à jour de la progression
        int progress = (currentStep.getStepNumber() * 100) / FormStep.values().length;
        progressBar.setProgress(progress);
        progressTextView.setText(String.format("Étape %d sur %d", 
            currentStep.getStepNumber() + 1, FormStep.values().length));
        
        // Charger le layout correspondant à l'étape
        loadStepLayout();
        
        updateButtonVisibility();
    }
    
    private void loadStepLayout() {
        // Vider le container
        stepContainer.removeAllViews();
        
        // Charger le layout selon l'étape
        int layoutId = getLayoutForStep(currentStep);
        if (layoutId != 0) {
            LayoutInflater inflater = LayoutInflater.from(this);
            View stepView = inflater.inflate(layoutId, stepContainer, false);
            stepContainer.addView(stepView);
            
            // Configuration spéciale pour l'étape famille
            if (currentStep == FormStep.FAMILY) {
                setupFamilyStep(stepView);
            }
            
            // Configuration spéciale pour l'étape documents
            if (currentStep == FormStep.DOCUMENTS) {
                setupDocumentsStep(stepView);
            }
        }
    }
    
    private void setupFamilyStep(View stepView) {
        // Initialiser les vues pour la gestion des enfants
        childrenContainer = stepView.findViewById(R.id.children_container);
        addChildButton = stepView.findViewById(R.id.btn_add_child);
        
        if (addChildButton != null) {
            addChildButton.setOnClickListener(new View.OnClickListener() {
                @Override
                public void onClick(View v) {
                    addChild();
                }
            });
        }
    }
    
    private void addChild() {
        childCount++;
        
        LayoutInflater inflater = LayoutInflater.from(this);
        View childView = inflater.inflate(R.layout.child_item, childrenContainer, false);
        
        // Configurer le numéro de l'enfant
        TextView childNumberText = childView.findViewById(R.id.txt_child_number);
        childNumberText.setText("Enfant " + childCount);
        
        // Configurer le bouton supprimer
        Button removeButton = childView.findViewById(R.id.btn_remove_child);
        removeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                removeChild(childView);
            }
        });
        
        // Ajouter l'enfant au container
        childrenContainer.addView(childView);
        
        Log.d(TAG, "Enfant ajouté: " + childCount);
    }
    
    private void removeChild(View childView) {
        childrenContainer.removeView(childView);
        childCount--;
        
        // Mettre à jour les numéros des enfants restants
        updateChildNumbers();
        
        Log.d(TAG, "Enfant supprimé. Total: " + childCount);
    }
    
    private void updateChildNumbers() {
        for (int i = 0; i < childrenContainer.getChildCount(); i++) {
            View childView = childrenContainer.getChildAt(i);
            TextView childNumberText = childView.findViewById(R.id.txt_child_number);
            childNumberText.setText("Enfant " + (i + 1));
        }
    }
    
    private void setupDocumentsStep(View stepView) {
        // Initialiser les vues pour la gestion des documents
        documentTypeSpinner = stepView.findViewById(R.id.spinner_document_type);
        numberTypeSpinner = stepView.findViewById(R.id.spinner_number_type);
        documentFieldsContainer = stepView.findViewById(R.id.document_fields_container);
        numberFieldsContainer = stepView.findViewById(R.id.number_fields_container);
        
        // Configurer le spinner des pièces d'identité
        setupDocumentTypeSpinner();
        
        // Configurer le spinner des numéros administratifs
        setupNumberTypeSpinner();
    }
    
    private void setupDocumentTypeSpinner() {
        String[] documentTypes = {
            "Sélectionner une pièce...",
            "Carte d'identité nationale",
            "Passeport",
            "Permis de travail",
            "Carte d'électeur"
        };
        
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, documentTypes);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        documentTypeSpinner.setAdapter(adapter);
        
        documentTypeSpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                if (position > 0) {
                    documentFieldsContainer.setVisibility(View.VISIBLE);
                    Log.d(TAG, "Pièce sélectionnée: " + documentTypes[position]);
                } else {
                    documentFieldsContainer.setVisibility(View.GONE);
                }
            }
            
            @Override
            public void onNothingSelected(android.widget.AdapterView<?> parent) {
                documentFieldsContainer.setVisibility(View.GONE);
            }
        });
    }
    
    private void setupNumberTypeSpinner() {
        String[] numberTypes = {
            "Sélectionner un numéro...",
            "Numéro INSS (Sécurité sociale)",
            "Numéro fiscal"
        };
        
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, numberTypes);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        numberTypeSpinner.setAdapter(adapter);
        
        numberTypeSpinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(android.widget.AdapterView<?> parent, View view, int position, long id) {
                if (position > 0) {
                    numberFieldsContainer.setVisibility(View.VISIBLE);
                    Log.d(TAG, "Numéro sélectionné: " + numberTypes[position]);
                } else {
                    numberFieldsContainer.setVisibility(View.GONE);
                }
            }
            
            @Override
            public void onNothingSelected(android.widget.AdapterView<?> parent) {
                numberFieldsContainer.setVisibility(View.GONE);
            }
        });
    }
    
    private int getLayoutForStep(FormStep step) {
        switch (step) {
            case IDENTITY:
                return R.layout.step_identity;
            case ORIGIN:
                return R.layout.step_origin;
            case ADDRESS:
                return R.layout.step_address;
            case FAMILY:
                return R.layout.step_family;
            case EDUCATION:
                return R.layout.step_education;
            case PROFESSIONAL:
                return R.layout.step_professional;
            case DOCUMENTS:
                return R.layout.step_documents;
            case EMERGENCY:
                return R.layout.step_emergency;
            case BANKING:
                return R.layout.step_banking;
            case MEDICAL:
                return R.layout.step_medical;
            case EQUIPMENT:
                return R.layout.step_equipment;
            case BIOMETRIC:
                return R.layout.step_biometric;
            default:
                return 0;
        }
    }
    
    private String getStepDescription(FormStep step) {
        switch (step) {
            case IDENTITY:
                return "Informations personnelles de l'employé";
            case ORIGIN:
                return "Lieu d'origine de l'employé";
            case ADDRESS:
                return "Adresse actuelle de l'employé";
            case FAMILY:
                return "Situation familiale et enfants";
            case EDUCATION:
                return "Formation et diplômes";
            case PROFESSIONAL:
                return "Informations professionnelles";
            case DOCUMENTS:
                return "Documents administratifs";
            case EMERGENCY:
                return "Personne à contacter en cas d'urgence";
            case BANKING:
                return "Informations bancaires et salariales";
            case MEDICAL:
                return "Informations médicales";
            case EQUIPMENT:
                return "Équipements et accès";
            case BIOMETRIC:
                return "Capture de la photo et des empreintes digitales";
            default:
                return "Étape du formulaire";
        }
    }
    
    private void updateButtonVisibility() {
        // Bouton précédent
        previousButton.setVisibility(currentStep == FormStep.IDENTITY ? View.GONE : View.VISIBLE);
        
        // Bouton suivant
        nextButton.setVisibility(currentStep == FormStep.BIOMETRIC ? View.GONE : View.VISIBLE);
        
        // Bouton sauvegarder
        saveButton.setVisibility(currentStep == FormStep.BIOMETRIC ? View.VISIBLE : View.GONE);
    }
    
    private void goToPreviousStep() {
        if (currentStep.getStepNumber() > 0) {
            FormStep[] steps = FormStep.values();
            currentStep = steps[currentStep.getStepNumber() - 1];
            updateStepDisplay();
        }
    }
    
    private void goToNextStep() {
        if (validateCurrentStep()) {
            if (currentStep.getStepNumber() < FormStep.values().length - 1) {
                FormStep[] steps = FormStep.values();
                currentStep = steps[currentStep.getStepNumber() + 1];
                updateStepDisplay();
            }
        }
    }
    
    private boolean validateCurrentStep() {
        // TODO: Implémenter la validation selon l'étape courante
        switch (currentStep) {
            case IDENTITY:
                return validateIdentityStep();
            case BIOMETRIC:
                return validateBiometricStep();
            default:
                return true; // Pour l'instant, on accepte toutes les autres étapes
        }
    }
    
    private boolean validateIdentityStep() {
        // TODO: Validation des champs d'identité
        return true;
    }
    
    private boolean validateBiometricStep() {
        // TODO: Validation des données biométriques
        return true;
    }
    
    private void saveEmployee() {
        if (validateCurrentStep()) {
            // Collecter TOUTES les données de TOUTES les étapes
            collectAllStepsData();
            
            // Afficher un message de chargement
            showSuccess("Enregistrement en cours...");
            
            // Envoyer les données vers l'API
            apiService.saveEmployee(employeeData, new EmployeeApiService.ApiCallback() {
                @Override
                public void onSuccess(String message) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            showSuccess(message);
                            
                            // Retour au menu principal
                            Intent intent = new Intent(EmployeeEnrollmentActivity.this, MainMenuActivity.class);
                            startActivity(intent);
                            finish();
                        }
                    });
                }
                
                @Override
                public void onError(String error) {
                    runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            showError("Erreur: " + error);
                        }
                    });
                }
            });
        }
    }
    
    private void cancelEnrollment() {
        // TODO: Demander confirmation
        Intent intent = new Intent(this, MainMenuActivity.class);
        startActivity(intent);
        finish();
    }
    
    private void showError(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
    
    private void showSuccess(String message) {
        Toast.makeText(this, message, Toast.LENGTH_SHORT).show();
    }
    
    /**
     * Collecte les données de l'étape courante
     */
    private void collectAllStepsData() {
        try {
            Log.d(TAG, "Collecte de TOUTES les données de TOUTES les étapes");
            
            // Collecter les données de l'étape courante d'abord
            collectCurrentStepData();
            
            // Maintenant, collecter les données de toutes les étapes en parcourant les vues
            // Nous allons utiliser une approche différente : collecter directement depuis les vues racines
            
            // Étape 1: Identité
            collectIdentityDataFromRoot();
            
            // Étape 2: Origine  
            collectOriginDataFromRoot();
            
            // Étape 3: Adresse
            collectAddressDataFromRoot();
            
            // Étape 4: Famille
            collectFamilyDataFromRoot();
            
            // Étape 5: Éducation
            collectEducationDataFromRoot();
            
            // Étape 6: Professionnel
            collectProfessionalDataFromRoot();
            
            // Étape 7: Documents
            collectDocumentsDataFromRoot();
            
            // Étape 8: Urgence
            collectEmergencyDataFromRoot();
            
            // Étape 9: Bancaire
            collectBankingDataFromRoot();
            
            // Étape 10: Médical
            collectMedicalDataFromRoot();
            
            // Étape 11: Équipement
            collectEquipmentDataFromRoot();
            
            // Étape 12: Biométrie
            collectBiometricDataFromRoot();
            
            Log.d(TAG, "Toutes les données collectées avec succès");
            Log.d(TAG, "Prénom: '" + employeeData.getFirstName() + "'");
            Log.d(TAG, "Nom: '" + employeeData.getLastName() + "'");
            Log.d(TAG, "Email: '" + employeeData.getEmail() + "'");
            Log.d(TAG, "Téléphone: '" + employeeData.getPhoneNumber() + "'");
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données: " + e.getMessage());
        }
    }

    private void collectCurrentStepData() {
        try {
            // Récupérer la vue courante
            View currentStepView = stepContainer.getChildAt(0);
            if (currentStepView == null) {
                Log.w(TAG, "Aucune vue d'étape trouvée");
                return;
            }
            
            switch (currentStep) {
                case IDENTITY:
                    collectIdentityData(currentStepView);
                    break;
                case ORIGIN:
                    collectOriginData(currentStepView);
                    break;
                case ADDRESS:
                    collectAddressData(currentStepView);
                    break;
                case FAMILY:
                    collectFamilyData(currentStepView);
                    break;
                case EDUCATION:
                    collectEducationData(currentStepView);
                    break;
                case PROFESSIONAL:
                    collectProfessionalData(currentStepView);
                    break;
                case DOCUMENTS:
                    collectDocumentsData(currentStepView);
                    break;
                case EMERGENCY:
                    collectEmergencyData(currentStepView);
                    break;
                case BANKING:
                    collectBankingData(currentStepView);
                    break;
                case MEDICAL:
                    collectMedicalData(currentStepView);
                    break;
                case EQUIPMENT:
                    collectEquipmentData(currentStepView);
                    break;
                case BIOMETRIC:
                    collectBiometricData(currentStepView);
                    break;
            }
            
            Log.d(TAG, "Données collectées pour l'étape: " + currentStep.getStepName());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données", e);
        }
    }
    
    /**
     * Collecte les données d'identité depuis la racine de l'activité
     */
    private void collectIdentityDataFromRoot() {
        try {
            Log.d(TAG, "=== DÉBUT COLLECTE IDENTITÉ ===");
            
            android.widget.EditText firstNameField = findViewById(R.id.edit_first_name);
            android.widget.EditText lastNameField = findViewById(R.id.edit_last_name);
            android.widget.EditText emailField = findViewById(R.id.edit_email);
            android.widget.EditText phoneField = findViewById(R.id.edit_phone);
            
            Log.d(TAG, "firstNameField trouvé: " + (firstNameField != null));
            Log.d(TAG, "lastNameField trouvé: " + (lastNameField != null));
            Log.d(TAG, "emailField trouvé: " + (emailField != null));
            Log.d(TAG, "phoneField trouvé: " + (phoneField != null));
            
            if (firstNameField != null) {
                String firstName = firstNameField.getText().toString().trim();
                employeeData.setFirstName(firstName);
                Log.d(TAG, "Prénom collecté: '" + firstName + "'");
            } else {
                Log.w(TAG, "Champ prénom non trouvé !");
            }
            
            if (lastNameField != null) {
                String lastName = lastNameField.getText().toString().trim();
                employeeData.setLastName(lastName);
                Log.d(TAG, "Nom collecté: '" + lastName + "'");
            } else {
                Log.w(TAG, "Champ nom non trouvé !");
            }
            
            if (emailField != null) {
                String email = emailField.getText().toString().trim();
                employeeData.setEmail(email);
                Log.d(TAG, "Email collecté: '" + email + "'");
            } else {
                Log.w(TAG, "Champ email non trouvé !");
            }
            
            if (phoneField != null) {
                String phone = phoneField.getText().toString().trim();
                employeeData.setPhoneNumber(phone);
                Log.d(TAG, "Téléphone collecté: '" + phone + "'");
            } else {
                Log.w(TAG, "Champ téléphone non trouvé !");
            }
            
            Log.d(TAG, "=== FIN COLLECTE IDENTITÉ ===");
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte identité: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données d'origine depuis la racine
     */
    private void collectOriginDataFromRoot() {
        try {
            android.widget.EditText originProvinceField = findViewById(R.id.edit_origin_province);
            if (originProvinceField != null) {
                employeeData.setOriginProvince(originProvinceField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte origine: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données d'adresse depuis la racine
     */
    private void collectAddressDataFromRoot() {
        try {
            android.widget.EditText currentProvinceField = findViewById(R.id.edit_current_province);
            if (currentProvinceField != null) {
                employeeData.setCurrentProvince(currentProvinceField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte adresse: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données familiales depuis la racine
     */
    private void collectFamilyDataFromRoot() {
        try {
            android.widget.EditText spouseNameField = findViewById(R.id.edit_spouse_name);
            if (spouseNameField != null) {
                employeeData.setSpouseName(spouseNameField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte famille: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données d'éducation depuis la racine
     */
    private void collectEducationDataFromRoot() {
        try {
            android.widget.EditText educationLevelField = findViewById(R.id.edit_education_level);
            if (educationLevelField != null) {
                employeeData.setEducationLevel(educationLevelField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte éducation: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données professionnelles depuis la racine
     */
    private void collectProfessionalDataFromRoot() {
        try {
            android.widget.EditText employeeIdField = findViewById(R.id.edit_employee_id);
            if (employeeIdField != null) {
                employeeData.setEmployeeId(employeeIdField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte professionnel: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données de documents depuis la racine
     */
    private void collectDocumentsDataFromRoot() {
        try {
            android.widget.EditText documentNumberField = findViewById(R.id.edit_document_number);
            if (documentNumberField != null) {
                employeeData.setNationalIdNumber(documentNumberField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte documents: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données d'urgence depuis la racine
     */
    private void collectEmergencyDataFromRoot() {
        try {
            android.widget.EditText emergencyNameField = findViewById(R.id.edit_emergency_name);
            if (emergencyNameField != null) {
                employeeData.setEmergencyContactName(emergencyNameField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte urgence: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données bancaires depuis la racine
     */
    private void collectBankingDataFromRoot() {
        try {
            android.widget.EditText bankNameField = findViewById(R.id.edit_bank_name);
            if (bankNameField != null) {
                employeeData.setBankName(bankNameField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte bancaire: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données médicales depuis la racine
     */
    private void collectMedicalDataFromRoot() {
        try {
            android.widget.EditText bloodTypeField = findViewById(R.id.edit_blood_type);
            if (bloodTypeField != null) {
                employeeData.setBloodType(bloodTypeField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte médical: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données d'équipement depuis la racine
     */
    private void collectEquipmentDataFromRoot() {
        try {
            android.widget.EditText badgeNumberField = findViewById(R.id.edit_badge_number);
            if (badgeNumberField != null) {
                employeeData.setAccessBadge(badgeNumberField.getText().toString().trim());
            }
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte équipement: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données biométriques depuis la racine
     */
    private void collectBiometricDataFromRoot() {
        try {
            // Données biométriques simulées
            employeeData.setPhotoPath("/path/to/photo.jpg");
            employeeData.setFingerprintTemplate("template_data");
            employeeData.setFingerprintFinger("index_finger");
            employeeData.setBiometricEnrollmentDate("24 oct. 2025");
            employeeData.setBiometricEnrolled(true);
            employeeData.setNumberOfChildren(0);
            
            Log.d(TAG, "Données biométriques simulées ajoutées");
        } catch (Exception e) {
            Log.e(TAG, "Erreur collecte biométrie: " + e.getMessage());
        }
    }
    
    /**
     * Collecte les données d'identité
     */
    private void collectIdentityData(View stepView) {
        try {
            // Récupérer les champs d'identité
            android.widget.EditText ninField = stepView.findViewById(R.id.edit_nin);
            android.widget.EditText firstNameField = stepView.findViewById(R.id.edit_first_name);
            android.widget.EditText lastNameField = stepView.findViewById(R.id.edit_last_name);
            android.widget.EditText middleNameField = stepView.findViewById(R.id.edit_middle_name);
            android.widget.EditText otherNamesField = stepView.findViewById(R.id.edit_other_names);
            android.widget.RadioGroup genderRadioGroup = stepView.findViewById(R.id.radio_gender);
            android.widget.EditText birthPlaceField = stepView.findViewById(R.id.edit_birth_place);
            android.widget.EditText birthDateField = stepView.findViewById(R.id.edit_birth_date);
            android.widget.EditText nationalityField = stepView.findViewById(R.id.edit_nationality);
            android.widget.EditText emailField = stepView.findViewById(R.id.edit_email);
            android.widget.EditText phoneField = stepView.findViewById(R.id.edit_phone);
            
            // Collecter les données
            if (ninField != null) employeeData.setNin(ninField.getText().toString().trim());
            if (firstNameField != null) employeeData.setFirstName(firstNameField.getText().toString().trim());
            if (lastNameField != null) employeeData.setLastName(lastNameField.getText().toString().trim());
            if (middleNameField != null) employeeData.setMiddleName(middleNameField.getText().toString().trim());
            if (otherNamesField != null) employeeData.setOtherNames(otherNamesField.getText().toString().trim());
            if (genderRadioGroup != null) {
                int selectedId = genderRadioGroup.getCheckedRadioButtonId();
                if (selectedId == R.id.radio_male) {
                    employeeData.setGender("Masculin");
                } else if (selectedId == R.id.radio_female) {
                    employeeData.setGender("Féminin");
                }
            }
            if (birthPlaceField != null) employeeData.setBirthPlace(birthPlaceField.getText().toString().trim());
            if (birthDateField != null) employeeData.setBirthDate(birthDateField.getText().toString().trim());
            if (nationalityField != null) employeeData.setNationality(nationalityField.getText().toString().trim());
            if (emailField != null) employeeData.setEmail(emailField.getText().toString().trim());
            if (phoneField != null) employeeData.setPhoneNumber(phoneField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données d'identité", e);
        }
    }
    
    /**
     * Collecte les données d'origine
     */
    private void collectOriginData(View stepView) {
        try {
            android.widget.EditText provinceField = stepView.findViewById(R.id.edit_origin_province);
            android.widget.EditText territoryField = stepView.findViewById(R.id.edit_origin_territory);
            android.widget.EditText communeField = stepView.findViewById(R.id.edit_origin_commune);
            android.widget.EditText groupementField = stepView.findViewById(R.id.edit_origin_groupement);
            android.widget.EditText villageField = stepView.findViewById(R.id.edit_origin_village);
            
            if (provinceField != null) employeeData.setOriginProvince(provinceField.getText().toString().trim());
            if (territoryField != null) employeeData.setOriginTerritory(territoryField.getText().toString().trim());
            if (communeField != null) employeeData.setOriginCommune(communeField.getText().toString().trim());
            if (groupementField != null) employeeData.setOriginGroupement(groupementField.getText().toString().trim());
            if (villageField != null) employeeData.setOriginVillage(villageField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données d'origine", e);
        }
    }
    
    /**
     * Collecte les données d'adresse
     */
    private void collectAddressData(View stepView) {
        try {
            android.widget.EditText provinceField = stepView.findViewById(R.id.edit_current_province);
            android.widget.EditText territoryField = stepView.findViewById(R.id.edit_current_territory);
            android.widget.EditText communeField = stepView.findViewById(R.id.edit_current_commune);
            android.widget.EditText groupementField = stepView.findViewById(R.id.edit_current_groupement);
            android.widget.EditText villageField = stepView.findViewById(R.id.edit_current_village);
            
            if (provinceField != null) employeeData.setCurrentProvince(provinceField.getText().toString().trim());
            if (territoryField != null) employeeData.setCurrentTerritory(territoryField.getText().toString().trim());
            if (communeField != null) employeeData.setCurrentCommune(communeField.getText().toString().trim());
            if (groupementField != null) employeeData.setCurrentGroupement(groupementField.getText().toString().trim());
            if (villageField != null) employeeData.setCurrentVillage(villageField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données d'adresse", e);
        }
    }
    
    /**
     * Collecte les données familiales
     */
    private void collectFamilyData(View stepView) {
        try {
            android.widget.RadioGroup maritalStatusRadioGroup = stepView.findViewById(R.id.radio_marital_status);
            android.widget.EditText spouseNameField = stepView.findViewById(R.id.edit_spouse_name);
            android.widget.EditText spouseFirstNameField = stepView.findViewById(R.id.edit_spouse_first_name);
            android.widget.EditText spouseBirthDateField = stepView.findViewById(R.id.edit_spouse_birth_date);
            
            if (maritalStatusRadioGroup != null) {
                int selectedId = maritalStatusRadioGroup.getCheckedRadioButtonId();
                if (selectedId == R.id.radio_single) {
                    employeeData.setMaritalStatus("Célibataire");
                } else if (selectedId == R.id.radio_married) {
                    employeeData.setMaritalStatus("Marié(e)");
                } else if (selectedId == R.id.radio_divorced) {
                    employeeData.setMaritalStatus("Divorcé(e)");
                } else if (selectedId == R.id.radio_widowed) {
                    employeeData.setMaritalStatus("Veuf/Veuve");
                }
            }
            if (spouseNameField != null) employeeData.setSpouseName(spouseNameField.getText().toString().trim());
            if (spouseFirstNameField != null) employeeData.setSpouseFirstName(spouseFirstNameField.getText().toString().trim());
            if (spouseBirthDateField != null) employeeData.setSpouseBirthDate(spouseBirthDateField.getText().toString().trim());
            
            // Compter les enfants
            employeeData.setNumberOfChildren(childCount);
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données familiales", e);
        }
    }
    
    /**
     * Collecte les données de formation
     */
    private void collectEducationData(View stepView) {
        try {
            android.widget.EditText levelField = stepView.findViewById(R.id.edit_education_level);
            android.widget.EditText institutionField = stepView.findViewById(R.id.edit_institution);
            android.widget.EditText fieldField = stepView.findViewById(R.id.edit_field_of_study);
            android.widget.EditText startYearField = stepView.findViewById(R.id.edit_study_start_year);
            android.widget.EditText endYearField = stepView.findViewById(R.id.edit_study_end_year);
            
            if (levelField != null) employeeData.setEducationLevel(levelField.getText().toString().trim());
            if (institutionField != null) employeeData.setEducationInstitution(institutionField.getText().toString().trim());
            if (fieldField != null) employeeData.setEducationField(fieldField.getText().toString().trim());
            if (startYearField != null) employeeData.setEducationStartYear(startYearField.getText().toString().trim());
            if (endYearField != null) employeeData.setEducationEndYear(endYearField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données de formation", e);
        }
    }
    
    /**
     * Collecte les données professionnelles
     */
    private void collectProfessionalData(View stepView) {
        try {
            android.widget.EditText employeeIdField = stepView.findViewById(R.id.edit_employee_id);
            android.widget.EditText hireDateField = stepView.findViewById(R.id.edit_hire_date);
            android.widget.RadioGroup contractTypeRadioGroup = stepView.findViewById(R.id.radio_contract_type);
            android.widget.EditText positionField = stepView.findViewById(R.id.edit_position);
            android.widget.EditText departmentField = stepView.findViewById(R.id.edit_department);
            
            if (employeeIdField != null) employeeData.setEmployeeId(employeeIdField.getText().toString().trim());
            if (hireDateField != null) employeeData.setHireDate(hireDateField.getText().toString().trim());
            if (contractTypeRadioGroup != null) {
                int selectedId = contractTypeRadioGroup.getCheckedRadioButtonId();
                if (selectedId == R.id.radio_cdi) {
                    employeeData.setContractType("CDI");
                } else if (selectedId == R.id.radio_cdd) {
                    employeeData.setContractType("CDD");
                } else if (selectedId == R.id.radio_internship) {
                    employeeData.setContractType("Stage");
                } else if (selectedId == R.id.radio_freelance) {
                    employeeData.setContractType("Freelance");
                }
            }
            if (positionField != null) employeeData.setJobTitle(positionField.getText().toString().trim());
            if (departmentField != null) employeeData.setDepartment(departmentField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données professionnelles", e);
        }
    }
    
    /**
     * Collecte les données de documents
     */
    private void collectDocumentsData(View stepView) {
        try {
            // Documents d'identité
            android.widget.EditText idNumberField = stepView.findViewById(R.id.edit_document_number);
            android.widget.EditText idIssueDateField = stepView.findViewById(R.id.edit_document_issue_date);
            android.widget.EditText idExpiryDateField = stepView.findViewById(R.id.edit_document_expiry_date);
            
            if (idNumberField != null) employeeData.setNationalIdNumber(idNumberField.getText().toString().trim());
            if (idIssueDateField != null) employeeData.setNationalIdDocument(idIssueDateField.getText().toString().trim());
            if (idExpiryDateField != null) employeeData.setNationalIdDocument(idExpiryDateField.getText().toString().trim());
            
            // Numéros administratifs
            android.widget.EditText numberField = stepView.findViewById(R.id.edit_number_value);
            if (numberField != null) {
                String numberValue = numberField.getText().toString().trim();
                if (!numberValue.isEmpty()) {
                    // Déterminer le type de numéro sélectionné
                    if (numberTypeSpinner != null && numberTypeSpinner.getSelectedItemPosition() > 0) {
                        String selectedType = numberTypeSpinner.getSelectedItem().toString();
                        if (selectedType.contains("INSS")) {
                            employeeData.setInssNumber(numberValue);
                        } else if (selectedType.contains("fiscal")) {
                            employeeData.setTaxNumber(numberValue);
                        }
                    }
                }
            }
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données de documents", e);
        }
    }
    
    /**
     * Collecte les données d'urgence
     */
    private void collectEmergencyData(View stepView) {
        try {
            android.widget.EditText nameField = stepView.findViewById(R.id.edit_emergency_name);
            android.widget.EditText addressField = stepView.findViewById(R.id.edit_emergency_address);
            android.widget.EditText phoneField = stepView.findViewById(R.id.edit_emergency_phone);
            
            if (nameField != null) employeeData.setEmergencyContactName(nameField.getText().toString().trim());
            if (addressField != null) employeeData.setEmergencyContactAddress(addressField.getText().toString().trim());
            if (phoneField != null) employeeData.setEmergencyContactPhone(phoneField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données d'urgence", e);
        }
    }
    
    /**
     * Collecte les données bancaires
     */
    private void collectBankingData(View stepView) {
        try {
            android.widget.EditText bankNameField = stepView.findViewById(R.id.edit_bank_name);
            android.widget.EditText accountNumberField = stepView.findViewById(R.id.edit_account_number);
            android.widget.EditText grossSalaryField = stepView.findViewById(R.id.edit_gross_salary);
            android.widget.EditText netSalaryField = stepView.findViewById(R.id.edit_net_salary);
            
            if (bankNameField != null) employeeData.setBankName(bankNameField.getText().toString().trim());
            if (accountNumberField != null) employeeData.setBankAccountNumber(accountNumberField.getText().toString().trim());
            if (grossSalaryField != null) employeeData.setGrossSalary(grossSalaryField.getText().toString().trim());
            if (netSalaryField != null) employeeData.setNetSalary(netSalaryField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données bancaires", e);
        }
    }
    
    /**
     * Collecte les données médicales
     */
    private void collectMedicalData(View stepView) {
        try {
            android.widget.EditText bloodTypeField = stepView.findViewById(R.id.edit_blood_type);
            android.widget.EditText allergiesField = stepView.findViewById(R.id.edit_allergies);
            android.widget.EditText disabilityField = stepView.findViewById(R.id.edit_disability);
            android.widget.EditText doctorField = stepView.findViewById(R.id.edit_doctor);
            
            if (bloodTypeField != null) employeeData.setBloodType(bloodTypeField.getText().toString().trim());
            if (allergiesField != null) employeeData.setAllergies(allergiesField.getText().toString().trim());
            if (disabilityField != null) employeeData.setDisabilities(disabilityField.getText().toString().trim());
            if (doctorField != null) employeeData.setDoctorName(doctorField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données médicales", e);
        }
    }
    
    /**
     * Collecte les données d'équipements
     */
    private void collectEquipmentData(View stepView) {
        try {
            android.widget.EditText badgeField = stepView.findViewById(R.id.edit_badge_number);
            android.widget.EditText officeField = stepView.findViewById(R.id.edit_office_location);
            android.widget.EditText equipmentField = stepView.findViewById(R.id.edit_equipment);
            android.widget.EditText accountsField = stepView.findViewById(R.id.edit_computer_accounts);
            
            if (badgeField != null) employeeData.setAccessBadge(badgeField.getText().toString().trim());
            if (officeField != null) employeeData.setWorkLocation(officeField.getText().toString().trim());
            if (equipmentField != null) employeeData.setWorkEquipment(equipmentField.getText().toString().trim());
            if (accountsField != null) employeeData.setComputerAccounts(accountsField.getText().toString().trim());
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données d'équipements", e);
        }
    }
    
    /**
     * Collecte les données biométriques
     */
    private void collectBiometricData(View stepView) {
        try {
            // Pour l'instant, on simule les données biométriques
            employeeData.setPhotoPath("/path/to/photo.jpg");
            employeeData.setFingerprintTemplate("template_data");
            employeeData.setFingerprintFinger("index_finger");
            employeeData.setBiometricEnrollmentDate(java.text.SimpleDateFormat.getDateInstance().format(new java.util.Date()));
            employeeData.setBiometricEnrolled(true);
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la collecte des données biométriques", e);
        }
    }
    
}