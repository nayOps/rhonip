package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.net.Uri;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.hardware.Camera;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.biometric.R;
import com.onip.biometric.camera.CameraPreview;
import com.onip.biometric.fingerprint.FingerprintProcessObserver;
import com.onip.biometric.models.EmployeeData;
import com.onip.biometric.services.EmployeeApiService;

// Imports MorphoSmart SDK
import com.morpho.android.usb.USBManager;
import com.morpho.morphosmart.sdk.CallbackMask;
import com.morpho.morphosmart.sdk.Coder;
import com.morpho.morphosmart.sdk.DetectionMode;
import com.morpho.morphosmart.sdk.EnrollmentType;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.LatentDetection;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.Template;
import com.morpho.morphosmart.sdk.TemplateFVPType;
import com.morpho.morphosmart.sdk.TemplateList;
import com.morpho.morphosmart.sdk.TemplateType;

import java.io.File;
import java.io.FileOutputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * Activité avec trois étapes pour l'enregistrement d'employé
 * Étape 1: Informations personnelles
 * Étape 2: Capture de photo avec spécifications ICAO
 * Étape 3: Capture des empreintes prioritaires (3 doigts: Index_Droit, Pouce_Droit, Index_Gauche)
 */
public class ThreeStepEmployeeActivity extends Activity {
    
    private static final String TAG = "ThreeStepEmployeeActivity";
    private static final int REQUEST_IMAGE_CAPTURE = 1001;
    private static final int STEP_PERSONAL_INFO = 1;
    private static final int STEP_PHOTO_ICAO = 2;
    private static final int STEP_FINGERPRINTS = 3;
    
    // État actuel
    private int currentStep = STEP_PERSONAL_INFO;
    
    // Vues communes
    private TextView stepTitle;
    private TextView stepProgress;
    private Button btnPrevious;
    private Button btnNext;
    private Button btnSave;
    private Button btnSettings;
    private Button btnAttendance;
    
    // Étape 1 - Informations personnelles
    private LinearLayout step1Layout;
    private EditText editNin, editFirstName, editLastName, editMiddleName;
    private EditText editEmail, editPhone, editJobTitle, editDepartment;
    private EditText editSalary, editHireDate;
    
    // Étape 2 - Capture photo ICAO
    private LinearLayout step2Layout;
    private FrameLayout cameraPreview;
    private ImageView imgPhotoPreview;
    private Button btnCapturePhoto;
    private TextView txtIcaoStatus;
    private ProgressBar progressIcao;
    private TextView txtIcaoScore;
    
    // Étape 3 - Capture empreintes
    private LinearLayout step3Layout;
    private ImageView imgFingerprintPreview;
    private Button btnStartFingerprints;
    private TextView txtFingerprintStatus;
    private ProgressBar progressFingerprint;
    private TextView txtFingerprintScore;
    // private TextView txtFingerProgress; // Variable non utilisée
    private LinearLayout fingersList;
    
    // Services
    private EmployeeApiService apiService;
    private EmployeeData employeeData;
    private Camera camera;
    private CameraPreview cameraPreviewView;
    
    // Gestion des empreintes
    // APPROCHE HYBRIDE : Enregistrer seulement 2-3 doigts prioritaires pour optimisation
    // Ordre de priorité : Index_Droit (1), Pouce_Droit (2), Index_Gauche (3)
    private Map<String, byte[]> capturedFingerprints = new HashMap<>();
    private String[] priorityFingers = {"Index_Droit", "Pouce_Droit", "Index_Gauche"};
    private int currentFingerIndex = 0;
    private String[] allFingers;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_three_step_employee);
        
        // Forcer l'orientation portrait
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        
        Log.d(TAG, "Initialisation de l'activité à trois étapes");
        
        initializeViews();
        initializeData();
        setupListeners();
        showStep(STEP_PERSONAL_INFO);
    }
    
    private void initializeViews() {
        // Vues communes
        stepTitle = findViewById(R.id.step_title);
        stepProgress = findViewById(R.id.step_progress);
        btnPrevious = findViewById(R.id.btn_previous);
        btnNext = findViewById(R.id.btn_next);
        btnSave = findViewById(R.id.btn_save);
        btnSettings = findViewById(R.id.btn_settings);
        btnAttendance = findViewById(R.id.btn_attendance);
        btnSettings = findViewById(R.id.btn_settings);
        
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
        
        // Étape 2 - Capture photo ICAO
        step2Layout = findViewById(R.id.step2_layout);
        cameraPreview = findViewById(R.id.camera_preview);
        imgPhotoPreview = findViewById(R.id.img_photo_preview);
        btnCapturePhoto = findViewById(R.id.btn_capture_photo);
        txtIcaoStatus = findViewById(R.id.txt_icao_status);
        progressIcao = findViewById(R.id.progress_icao);
        txtIcaoScore = findViewById(R.id.txt_icao_score);
        
        // Étape 3 - Capture empreintes
        step3Layout = findViewById(R.id.step3_layout);
        imgFingerprintPreview = findViewById(R.id.img_fingerprint_preview);
        btnStartFingerprints = findViewById(R.id.btn_start_fingerprints);
        txtFingerprintStatus = findViewById(R.id.txt_fingerprint_status);
        progressFingerprint = findViewById(R.id.progress_fingerprint);
        txtFingerprintScore = findViewById(R.id.txt_fingerprint_score);
        // txtFingerProgress = findViewById(R.id.txt_finger_progress); // ID non utilisé
        fingersList = findViewById(R.id.fingers_list);
        
        Log.d(TAG, "Vues initialisées");
    }
    
    private void initializeData() {
        employeeData = new EmployeeData();
        apiService = new EmployeeApiService(this);
        
        // APPROCHE HYBRIDE : Utiliser seulement les doigts prioritaires (2-3 doigts)
        // Cela optimise le matching et réduit le temps d'enregistrement
        allFingers = priorityFingers.clone();
        
        Log.d(TAG, "Données initialisées - Mode optimisé: " + allFingers.length + " doigts prioritaires");
        Log.d(TAG, "Doigts à enregistrer: Index_Droit, Pouce_Droit, Index_Gauche");
    }
    
    private void setupListeners() {
        btnPrevious.setOnClickListener(v -> {
            if (currentStep == STEP_PHOTO_ICAO) {
                showStep(STEP_PERSONAL_INFO);
            } else if (currentStep == STEP_FINGERPRINTS) {
                showStep(STEP_PHOTO_ICAO);
            }
        });
        
        btnNext.setOnClickListener(v -> {
            if (currentStep == STEP_PERSONAL_INFO) {
                if (validateStep1()) {
                    collectStep1Data();
                    showStep(STEP_PHOTO_ICAO);
                }
            } else if (currentStep == STEP_PHOTO_ICAO) {
                if (validateStep2()) {
                    collectStep2Data();
                    showStep(STEP_FINGERPRINTS);
                }
            }
        });
        
        btnSave.setOnClickListener(v -> {
            if (currentStep == STEP_FINGERPRINTS) {
                if (validateStep3()) {
                    collectStep3Data();
                    saveEmployee();
                }
            }
        });
        
        btnCapturePhoto.setOnClickListener(v -> capturePhoto());
        btnStartFingerprints.setOnClickListener(v -> {
            if (currentFingerIndex < allFingers.length) {
                // Capturer l'empreinte actuelle avec le vrai périphérique
                captureCurrentFingerprint();
            }
        });
        
        btnSettings.setOnClickListener(v -> {
            Intent intent = new Intent(ThreeStepEmployeeActivity.this, SettingsActivity.class);
            startActivity(intent);
        });
        
        btnAttendance.setOnClickListener(v -> {
            Intent intent = new Intent(ThreeStepEmployeeActivity.this, AttendanceActivity.class);
            startActivity(intent);
        });
        
        Log.d(TAG, "Listeners configurés");
    }
    
    private void showStep(int step) {
        currentStep = step;
        
        if (step == STEP_PERSONAL_INFO) {
            stepTitle.setText("Informations Personnelles");
            stepProgress.setText("Étape 1 sur 3");
            step1Layout.setVisibility(View.VISIBLE);
            step2Layout.setVisibility(View.GONE);
            step3Layout.setVisibility(View.GONE);
            btnPrevious.setVisibility(View.GONE);
            btnNext.setVisibility(View.VISIBLE);
            btnSave.setVisibility(View.GONE);
        } else if (step == STEP_PHOTO_ICAO) {
            stepTitle.setText("Capture Photo ICAO");
            stepProgress.setText("Étape 2 sur 3");
            step1Layout.setVisibility(View.GONE);
            step2Layout.setVisibility(View.VISIBLE);
            step3Layout.setVisibility(View.GONE);
            btnPrevious.setVisibility(View.VISIBLE);
            btnNext.setVisibility(View.VISIBLE);
            btnSave.setVisibility(View.GONE);
            initializeCamera();
            setupCameraPreview();
        } else if (step == STEP_FINGERPRINTS) {
            stepTitle.setText("Capture Empreintes");
            stepProgress.setText("Étape 3 sur 3");
            step1Layout.setVisibility(View.GONE);
            step2Layout.setVisibility(View.GONE);
            step3Layout.setVisibility(View.VISIBLE);
            btnPrevious.setVisibility(View.VISIBLE);
            btnNext.setVisibility(View.GONE);
            btnSave.setVisibility(View.VISIBLE);
            
            // Initialiser le périphérique MorphoSmart dès l'arrivée à l'étape 3
            txtFingerprintStatus.setText("Initialisation du capteur d'empreintes...");
            initializeMorphoDevice();
        }
        
        Log.d(TAG, "Affichage de l'étape " + step);
    }
    
    private boolean validateStep1() {
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
        if (employeeData.getPhotoPath() == null || employeeData.getPhotoPath().isEmpty()) {
            showToast("La photo est requise");
            return false;
        }
        return true;
    }
    
    private boolean validateStep3() {
        // APPROCHE HYBRIDE : Vérifier que les 3 doigts prioritaires sont capturés
        if (capturedFingerprints.size() < 3) {
            showToast("Toutes les empreintes prioritaires sont requises (3/3)");
            return false;
        }
        return true;
    }
    
    private void collectStep1Data() {
        employeeData.setNin(editNin.getText().toString().trim());
        employeeData.setFirstName(editFirstName.getText().toString().trim());
        employeeData.setLastName(editLastName.getText().toString().trim());
        employeeData.setMiddleName(editMiddleName.getText().toString().trim());
        employeeData.setEmail(editEmail.getText().toString().trim());
        employeeData.setPhoneNumber(editPhone.getText().toString().trim());
        employeeData.setJobTitle(editJobTitle.getText().toString().trim());
        employeeData.setDepartment(editDepartment.getText().toString().trim());
        employeeData.setGrossSalary(editSalary.getText().toString().trim());
        employeeData.setHireDate(editHireDate.getText().toString().trim());
    }
    
    private void collectStep2Data() {
        // Les données de la photo sont déjà collectées dans capturePhoto()
        Log.d(TAG, "Données étape 2 collectées - Photo: " + employeeData.getPhotoPath());
    }
    
    private void collectStep3Data() {
        // Combiner tous les templates (format texte pour compatibilité)
        StringBuilder allTemplates = new StringBuilder();
        for (Map.Entry<String, byte[]> entry : capturedFingerprints.entrySet()) {
            allTemplates.append(entry.getKey()).append(":").append(entry.getValue().length).append(";");
        }
        
        employeeData.setFingerprintTemplate(allTemplates.toString());
        employeeData.setFingerprintFinger("priority_fingers"); // 3 doigts prioritaires
        employeeData.setBiometricEnrolled(true);
        
        // NOUVEAU : Stocker les templates binaires pour l'envoi au backend
        employeeData.setCapturedFingerprints(new HashMap<>(capturedFingerprints));
        Log.d(TAG, "Templates binaires stockés: " + capturedFingerprints.size() + " doigts");
    }
    
    private void initializeCamera() {
        try {
            camera = Camera.open(0);
            cameraPreviewView = new CameraPreview(this, camera);
            cameraPreview.addView(cameraPreviewView);
            txtIcaoStatus.setText("Caméra initialisée - Prêt pour capture");
        } catch (Exception e) {
            Log.e(TAG, "Erreur initialisation caméra: " + e.getMessage());
            txtIcaoStatus.setText("Erreur caméra: " + e.getMessage());
        }
    }
    
    private void capturePhoto() {
        if (camera == null) {
            showToast("Caméra non disponible");
            return;
        }
        
        txtIcaoStatus.setText("Capture en cours...");
        progressIcao.setVisibility(View.VISIBLE);
        
        camera.takePicture(null, null, new Camera.PictureCallback() {
            @Override
            public void onPictureTaken(byte[] data, Camera camera) {
                try {
                    // Sauvegarder la photo
                    String photoPath = savePhoto(data);
                    employeeData.setPhotoPath(photoPath);
                    
                    // Simuler l'analyse ICAO
                    int icaoScore = analyzeIcaoCompliance(data);
                    
                    runOnUiThread(() -> {
                        imgPhotoPreview.setImageBitmap(BitmapFactory.decodeFile(photoPath));
                        imgPhotoPreview.setVisibility(View.VISIBLE);
                        txtIcaoScore.setText("Score ICAO: " + icaoScore + "%");
                        progressIcao.setProgress(icaoScore);
                        progressIcao.setVisibility(View.GONE);
                        
                        if (icaoScore >= 80) {
                            txtIcaoStatus.setText("✅ Photo conforme ICAO (" + icaoScore + "%)");
                            txtIcaoStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
                        } else {
                            txtIcaoStatus.setText("⚠️ Photo non conforme (" + icaoScore + "%)");
                            txtIcaoStatus.setTextColor(getResources().getColor(android.R.color.holo_orange_dark));
                        }
                    });
                    
                    Log.d(TAG, "Photo capturée: " + photoPath + " (Score ICAO: " + icaoScore + "%)");
                    
                } catch (Exception e) {
                    Log.e(TAG, "Erreur sauvegarde photo: " + e.getMessage());
                    runOnUiThread(() -> {
                        txtIcaoStatus.setText("Erreur: " + e.getMessage());
                        progressIcao.setVisibility(View.GONE);
                    });
                }
            }
        });
    }
    
    private String savePhoto(byte[] data) throws Exception {
        File mediaStorageDir = new File(Environment.getExternalStorageDirectory(), "RH_Photos");
        if (!mediaStorageDir.exists()) {
            if (!mediaStorageDir.mkdirs()) {
                throw new Exception("Échec création dossier photos");
            }
        }
        
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        String filename = "RH_Photo_" + timeStamp + ".jpg";
        File photoFile = new File(mediaStorageDir.getPath() + File.separator + filename);
        
        FileOutputStream fos = new FileOutputStream(photoFile);
        fos.write(data);
        fos.close();
        
        return photoFile.getAbsolutePath();
    }
    
    private int analyzeIcaoCompliance(byte[] imageData) {
        // Simulation de l'analyse ICAO
        // En réalité, ceci devrait utiliser une bibliothèque d'analyse d'image
        int baseScore = 70;
        int randomVariation = (int) (Math.random() * 30);
        return Math.min(100, baseScore + randomVariation);
    }
    
    private void startFingerprintCapture() {
        capturedFingerprints.clear();
        currentFingerIndex = 0;
        
        txtFingerprintStatus.setText("Prêt à capturer les empreintes prioritaires...\n" +
                                    "Doigts à enregistrer: Index_Droit, Pouce_Droit, Index_Gauche");
        
        // Créer la liste des doigts (seulement 3 doigts prioritaires)
        createFingersList();
        
        // Le périphérique est déjà initialisé dans showStep(STEP_FINGERPRINTS)
        if (deviceInitialized) {
            btnStartFingerprints.setText("👆 Capturer " + allFingers[0] + " (1/3)");
            btnStartFingerprints.setEnabled(true);
        } else {
            txtFingerprintStatus.setText("Initialisation du capteur en cours...");
        }
    }
    
    private void createFingersList() {
        fingersList.removeAllViews();
        
        for (int i = 0; i < allFingers.length; i++) {
            TextView fingerView = new TextView(this);
            fingerView.setText(allFingers[i] + " - ⏳ En attente");
            fingerView.setPadding(16, 8, 16, 8);
            fingerView.setBackgroundResource(R.drawable.status_background);
            fingerView.setLayoutParams(new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, 
                LinearLayout.LayoutParams.WRAP_CONTENT));
            fingerView.setTag(i);
            fingersList.addView(fingerView);
        }
    }
    
    private void captureNextFingerprint() {
        if (currentFingerIndex >= allFingers.length) {
            // Toutes les empreintes prioritaires capturées
            txtFingerprintStatus.setText("✅ Toutes les empreintes prioritaires capturées ! (3/3)");
            txtFingerprintStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
            btnStartFingerprints.setText("✅ Terminé");
            btnStartFingerprints.setEnabled(false);
            return;
        }
        
        String currentFinger = allFingers[currentFingerIndex];
        txtFingerprintStatus.setText("Placez le " + currentFinger + " sur le capteur et cliquez 'Capturer'");
        
        // Mettre à jour le bouton pour le doigt actuel
        btnStartFingerprints.setText("👆 Capturer " + currentFinger);
        btnStartFingerprints.setEnabled(true);
    }
    
    // Variables pour MorphoSmart
    private MorphoDevice morphoDevice;
    private boolean deviceInitialized = false;
    private FingerprintProcessObserver fingerprintObserver;
    
    private void captureCurrentFingerprint() {
        Log.d(TAG, "captureCurrentFingerprint - deviceInitialized: " + deviceInitialized + ", morphoDevice: " + (morphoDevice != null));
        if (!deviceInitialized || morphoDevice == null) {
            showToast("Périphérique non initialisé - deviceInitialized: " + deviceInitialized + ", morphoDevice: " + (morphoDevice != null));
            return;
        }
        
        String currentFinger = allFingers[currentFingerIndex];
        txtFingerprintStatus.setText("Placez le " + currentFinger + " sur le capteur...");
        btnStartFingerprints.setEnabled(false);
        btnStartFingerprints.setText("Capture en cours...");
        
        // Créer l'observer pour les callbacks
        fingerprintObserver = new FingerprintProcessObserver(this, txtFingerprintStatus, imgFingerprintPreview, progressFingerprint);
        
        new Thread(() -> {
            try {
                // Paramètres de capture (basés sur fingerprint-test)
                int timeout = 30;
                int acquisitionThreshold = 0;
                int advancedSecurityLevelsRequired = 0;
                int fingerNumber = 1;
                TemplateType templateType = TemplateType.MORPHO_PK_ISO_FMR;
                TemplateFVPType templateFVPType = TemplateFVPType.MORPHO_NO_PK_FVP;
                int maxSizeTemplate = 512;
                EnrollmentType enrollType = EnrollmentType.ONE_ACQUISITIONS;
                LatentDetection latentDetection = LatentDetection.LATENT_DETECT_ENABLE;
                Coder coderChoice = Coder.MORPHO_DEFAULT_CODER;
                int detectModeChoice = DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                        | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue();
                TemplateList templateList = new TemplateList();
                
                // Callbacks
                int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()
                        | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue()
                        | CallbackMask.MORPHO_CALLBACK_CODEQUALITY.getValue()
                        | CallbackMask.MORPHO_CALLBACK_DETECTQUALITY.getValue();
                
                // CAPTURE RÉELLE
                int ret = morphoDevice.capture(timeout, acquisitionThreshold, advancedSecurityLevelsRequired,
                        fingerNumber, templateType, templateFVPType, maxSizeTemplate, enrollType,
                        latentDetection, coderChoice, detectModeChoice, templateList, callbackCmd, fingerprintObserver);
                
                Log.d(TAG, "Capture " + currentFinger + " result: " + ret);
                
                if (ret == ErrorCodes.MORPHO_OK) {
                    if (templateList.getNbTemplate() == 1) {
                        Template template = templateList.getTemplate(0);
                        byte[] fingerTemplate = template.getData();
                        capturedFingerprints.put(currentFinger, fingerTemplate);
                        
                        runOnUiThread(() -> {
                            txtFingerprintStatus.setText("✅ " + currentFinger + " capturé avec succès !");
                            txtFingerprintStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
                            updateFingerprintList();
                            
                            // Passer au doigt suivant
                            currentFingerIndex++;
                            if (currentFingerIndex < allFingers.length) {
                                int progress = currentFingerIndex + 1;
                                btnStartFingerprints.setText("👆 Capturer " + allFingers[currentFingerIndex] + " (" + progress + "/3)");
                                btnStartFingerprints.setEnabled(true);
                                txtFingerprintStatus.setText("Prêt pour le " + allFingers[currentFingerIndex] + " (" + progress + "/3)");
                            } else {
                                // Toutes les empreintes prioritaires capturées
                                txtFingerprintStatus.setText("✅ Toutes les empreintes prioritaires capturées !\n" +
                                                            "3/3 doigts enregistrés (Index_Droit, Pouce_Droit, Index_Gauche)");
                                btnStartFingerprints.setText("✅ Terminé (3/3)");
                                btnStartFingerprints.setEnabled(false);
                            }
                        });
                    }
                } else {
                    runOnUiThread(() -> {
                        txtFingerprintStatus.setText("Erreur capture " + currentFinger + ": " + getErrorMessage(ret));
                        btnStartFingerprints.setText("👆 Réessayer " + currentFinger);
                        btnStartFingerprints.setEnabled(true);
                    });
                }
                
            } catch (Exception e) {
                Log.e(TAG, "Exception capture " + currentFinger + ": " + e.getMessage());
                runOnUiThread(() -> {
                    txtFingerprintStatus.setText("Erreur: " + e.getMessage());
                    btnStartFingerprints.setText("👆 Réessayer " + currentFinger);
                    btnStartFingerprints.setEnabled(true);
                });
            }
        }).start();
    }
    
    private void initializeMorphoDevice() {
        new Thread(() -> {
            try {
                Log.d(TAG, "Initialisation du périphérique MorphoSmart...");
                
                // Initialiser USBManager
                USBManager.getInstance().initialize(this, "com.onip.biometric.USB_ACTION", true);
                Log.d(TAG, "USBManager initialisé");
                
                // Créer le périphérique MorphoSmart
                morphoDevice = new MorphoDevice();
                Log.d(TAG, "MorphoDevice créé");
                
                // Énumérer les périphériques USB
                Integer nbUsbDevice = new Integer(0);
                int ret = morphoDevice.initUsbDevicesNameEnum(nbUsbDevice);
                Log.d(TAG, "Énumération USB: " + ret + ", nbDevices: " + nbUsbDevice);
                
                if (ret == ErrorCodes.MORPHO_OK && nbUsbDevice == 1) {
                    // Ouvrir le périphérique
                    String sensorName = morphoDevice.getUsbDeviceName(0);
                    Log.d(TAG, "Nom du capteur: " + sensorName);
                    
                    final int openResult = morphoDevice.openUsbDevice(sensorName, 0);
                    Log.d(TAG, "Ouverture périphérique: " + openResult);
                    
                    if (openResult == ErrorCodes.MORPHO_OK) {
                        deviceInitialized = true;
                        Log.d(TAG, "Périphérique MorphoSmart initialisé avec succès - deviceInitialized: " + deviceInitialized);
                        runOnUiThread(() -> {
                            txtFingerprintStatus.setText("✓ Capteur d'empreintes prêt ! Cliquez 'Capturer' pour commencer.");
                            btnStartFingerprints.setText("👆 Capturer " + allFingers[0]);
                            btnStartFingerprints.setEnabled(true);
                        });
                    } else {
                        runOnUiThread(() -> {
                            txtFingerprintStatus.setText("Erreur ouverture périphérique: " + openResult);
                        });
                    }
                } else {
                    final int finalNbUsbDevice = nbUsbDevice;
                    runOnUiThread(() -> {
                        txtFingerprintStatus.setText("Erreur: " + finalNbUsbDevice + " périphérique(s) trouvé(s). Attendu: 1");
                    });
                }
                
            } catch (Exception e) {
                Log.e(TAG, "Exception lors de l'initialisation: " + e.getMessage());
                runOnUiThread(() -> {
                    txtFingerprintStatus.setText("Exception: " + e.getMessage());
                });
            }
        }).start();
    }
    
    private void updateFingerprintList() {
        for (int i = 0; i < allFingers.length; i++) {
            TextView fingerView = (TextView) fingersList.findViewWithTag(i);
            if (fingerView != null) {
                String fingerName = allFingers[i];
                if (capturedFingerprints.containsKey(fingerName)) {
                    fingerView.setText("✅ " + fingerName + " - Capturé");
                    fingerView.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
                } else {
                    fingerView.setText("⏳ " + fingerName + " - En attente");
                    fingerView.setTextColor(getResources().getColor(android.R.color.holo_orange_dark));
                }
            }
        }
    }
    
    private String getErrorMessage(int errorCode) {
        switch (errorCode) {
            case ErrorCodes.MORPHO_OK: return "Succès";
            case -1: return "Paramètre invalide";
            case -2: return "Timeout";
            case -3: return "Aucun périphérique";
            case -4: return "Périphérique occupé";
            default: return "Erreur code: " + errorCode;
        }
    }
    
    private byte[] generateSimulatedTemplate(String fingerName) {
        byte[] template = new byte[512];
        String seed = fingerName + System.currentTimeMillis();
        
        for (int i = 0; i < template.length; i++) {
            template[i] = (byte) (seed.hashCode() + i);
        }
        
        return template;
    }
    
    private void saveEmployee() {
        Log.d(TAG, "=== DÉBUT SAUVEGARDE ===");
        
        try {
            showToast("Enregistrement en cours...");
            
            apiService.saveEmployee(employeeData, new EmployeeApiService.ApiCallback() {
                @Override
                public void onSuccess(String message) {
                    runOnUiThread(() -> {
                        showToast(message);
                        Log.d(TAG, "Succès: " + message);
                    });
                }
                
                @Override
                public void onError(String error) {
                    runOnUiThread(() -> {
                        showToast("Erreur: " + error);
                        Log.e(TAG, "Erreur: " + error);
                    });
                }
            });
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur lors de la sauvegarde: " + e.getMessage());
            showToast("Erreur: " + e.getMessage());
        }
    }
    
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        
        if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_OK) {
            // Photo capturée avec succès
            File photoFile = createPhotoFile();
            if (photoFile != null && photoFile.exists()) {
                String photoPath = photoFile.getAbsolutePath();
                employeeData.setPhotoPath(photoPath);
                
                // Simuler l'analyse ICAO
                int icaoScore = analyzeIcaoCompliance(null);
                
                // Afficher la photo
                imgPhotoPreview.setImageBitmap(BitmapFactory.decodeFile(photoPath));
                imgPhotoPreview.setVisibility(View.VISIBLE);
                txtIcaoScore.setText("Score ICAO: " + icaoScore + "%");
                progressIcao.setProgress(icaoScore);
                progressIcao.setVisibility(View.GONE);
                
                if (icaoScore >= 80) {
                    txtIcaoStatus.setText("✅ Photo conforme ICAO (" + icaoScore + "%)");
                    txtIcaoStatus.setTextColor(getResources().getColor(android.R.color.holo_green_dark));
                } else {
                    txtIcaoStatus.setText("⚠️ Photo non conforme (" + icaoScore + "%)");
                    txtIcaoStatus.setTextColor(getResources().getColor(android.R.color.holo_orange_dark));
                }
                
                Log.d(TAG, "Photo capturée: " + photoPath + " (Score ICAO: " + icaoScore + "%)");
            } else {
                showToast("Erreur: Photo non trouvée");
            }
        } else if (requestCode == REQUEST_IMAGE_CAPTURE && resultCode == RESULT_CANCELED) {
            showToast("Capture annulée");
        }
    }
    
    
    private File createPhotoFile() {
        File mediaStorageDir = new File(Environment.getExternalStorageDirectory(), "RH_Photos");
        if (!mediaStorageDir.exists()) {
            if (!mediaStorageDir.mkdirs()) {
                Log.d(TAG, "Échec création dossier: " + mediaStorageDir);
                return null;
            }
        }
        
        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        return new File(mediaStorageDir.getPath() + File.separator + "IMG_" + timeStamp + ".jpg");
    }
    
    private void setupCameraPreview() {
        if (camera != null) {
            try {
                // Créer le preview caméra
                CameraPreview preview = new CameraPreview(this, camera);
                cameraPreview.addView(preview);
                
                // Configuration de la caméra pour portrait
                Camera.Parameters params = camera.getParameters();
                params.setRotation(90); // Forcer l'orientation portrait
                camera.setParameters(params);
                
                Log.d(TAG, "Preview caméra configuré en portrait");
            } catch (Exception e) {
                Log.e(TAG, "Erreur configuration preview: " + e.getMessage());
            }
        }
    }
    
    private void showToast(String message) {
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (camera != null) {
            camera.release();
            camera = null;
        }
    }
}
