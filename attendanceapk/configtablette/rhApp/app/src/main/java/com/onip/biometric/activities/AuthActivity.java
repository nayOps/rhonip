package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.biometric.ONIPApplication;
import com.onip.biometric.R;
import com.onip.biometric.fingerprint.FingerprintProcessObserver;
import com.onip.biometric.services.EmployeeService;
import com.onip.biometric.services.FingerprintTemplateService;

import com.morpho.android.usb.USBManager;
import com.morpho.morphosmart.sdk.CallbackMask;
import com.morpho.morphosmart.sdk.Coder;
import com.morpho.morphosmart.sdk.DetectionMode;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.FalseAcceptanceRate;
import com.morpho.morphosmart.sdk.LatentDetection;
import com.morpho.morphosmart.sdk.MatchingStrategy;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.ResultMatching;
import com.morpho.morphosmart.sdk.Template;
import com.morpho.morphosmart.sdk.TemplateFVPType;
import com.morpho.morphosmart.sdk.TemplateList;
import com.morpho.morphosmart.sdk.TemplateType;
import com.morpho.morphosmart.sdk.EnrollmentType;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AuthActivity extends Activity {
    
    private static final String TAG = "AuthActivity";
    private static final String SUPER_ADMIN_FIRSTNAME = "nathan";
    private static final String SUPER_ADMIN_LASTNAME = "nathan";
    
    private TextView txtTitle;
    private TextView txtStatus;
    private ImageView imgFingerprint;
    private ProgressBar progressBar;
    private Button btnCapture;
    private Button btnBack;
    
    private MorphoDevice morphoDevice;
    private FingerprintProcessObserver processObserver;
    private boolean deviceInitialized = false;
    private boolean capturing = false;
    
    // Application globale
    private ONIPApplication app;
    
    // Pour l'authentification : utiliser les données globales
    private List<com.onip.biometric.models.Employee> allEmployeesWithFingerprints = new ArrayList<>();
    private Map<Integer, Map<String, byte[]>> allTemplatesForAuth = new HashMap<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_auth);
        
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        
        app = (ONIPApplication) getApplication();
        initializeViews();
        loadGlobalData();
    }
    
    private void initializeViews() {
        txtTitle = findViewById(R.id.txt_auth_title);
        txtStatus = findViewById(R.id.txt_auth_status);
        imgFingerprint = findViewById(R.id.img_auth_fingerprint);
        progressBar = findViewById(R.id.progress_auth);
        btnCapture = findViewById(R.id.btn_capture_auth);
        btnBack = findViewById(R.id.btn_back_auth);
        
        txtTitle.setText("Connexion");
        txtStatus.setText("Chargement du template d'authentification...");
        
        btnCapture.setText("Connexion");
        btnCapture.setOnClickListener(v -> captureFingerprint());
        btnBack.setOnClickListener(v -> finish());
        
        btnCapture.setEnabled(false);
    }
    
    private void loadGlobalData() {
        // Récupérer le MorphoDevice depuis l'application globale
        morphoDevice = app.getGlobalMorphoDevice();
        deviceInitialized = app.isDeviceInitialized();
        
        // Récupérer les employés depuis l'application globale
        allEmployeesWithFingerprints = app.getGlobalEmployees();
        
        // Récupérer les templates depuis l'application globale
        allTemplatesForAuth = app.getGlobalTemplates();
        
        Log.d(TAG, "✅ Données chargées depuis l'application globale:");
        Log.d(TAG, "   - Employés: " + allEmployeesWithFingerprints.size());
        Log.d(TAG, "   - Templates: " + allTemplatesForAuth.size() + " employé(s)");
        Log.d(TAG, "   - Device initialisé: " + deviceInitialized);
        
        if (allEmployeesWithFingerprints.isEmpty()) {
            runOnUiThread(() -> {
                txtStatus.setText("❌ Aucun employé chargé\nVeuillez redémarrer l'application");
                btnCapture.setEnabled(false);
            });
            return;
        }
        
        if (!deviceInitialized || morphoDevice == null) {
            runOnUiThread(() -> {
                txtStatus.setText("❌ Capteur non disponible\nVeuillez redémarrer l'application");
                btnCapture.setEnabled(false);
            });
            return;
        }
        
        // Filtrer les employés qui ont des templates
        int employeesWithTemplates = 0;
        for (com.onip.biometric.models.Employee emp : allEmployeesWithFingerprints) {
            if (allTemplatesForAuth.containsKey(emp.getId())) {
                employeesWithTemplates++;
            }
        }
        
        final int finalEmployeesWithTemplates = employeesWithTemplates;
        Log.d(TAG, "✅ " + finalEmployeesWithTemplates + " employé(s) avec templates chargés");
        runOnUiThread(() -> {
            txtStatus.setText("✓ " + finalEmployeesWithTemplates + " employé(s) prêt(s)\nPlacez votre doigt pour connexion");
            btnCapture.setEnabled(deviceInitialized);
        });
    }
    
    private void captureFingerprint() {
        if (!deviceInitialized || morphoDevice == null) {
            Toast.makeText(this, "Périphérique non initialisé", Toast.LENGTH_SHORT).show();
            return;
        }
        
        if (allTemplatesForAuth.isEmpty()) {
            Toast.makeText(this, "Aucun template chargé", Toast.LENGTH_SHORT).show();
            return;
        }

        capturing = true;
        btnCapture.setEnabled(false);
        btnCapture.setText("Capture en cours...");
        progressBar.setVisibility(View.VISIBLE);
        txtStatus.setText("Placez votre doigt sur le capteur...");

        processObserver = new FingerprintProcessObserver(this, txtStatus, imgFingerprint, progressBar);

        new Thread(() -> {
            try {
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

                int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()
                        | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue()
                        | CallbackMask.MORPHO_CALLBACK_CODEQUALITY.getValue()
                        | CallbackMask.MORPHO_CALLBACK_DETECTQUALITY.getValue();

                int ret = morphoDevice.capture(timeout, acquisitionThreshold, advancedSecurityLevelsRequired,
                        fingerNumber, templateType, templateFVPType, maxSizeTemplate, enrollType,
                        latentDetection, coderChoice, detectModeChoice, templateList, callbackCmd, processObserver);

                if (ret == ErrorCodes.MORPHO_OK) {
                    if (templateList.getNbTemplate() == 1) {
                        Template template = templateList.getTemplate(0);
                        byte[] capturedTemplate = template.getData();

                        runOnUiThread(() -> {
                            txtStatus.setText("Empreinte capturée\nVérification en cours...");
                        });

                        // Vérifier l'empreinte et le rôle super_admin
                        verifyFingerprintAndRole(capturedTemplate);
                    }
                } else {
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Erreur capture: " + getErrorMessage(ret));
                        btnCapture.setText("Capturer");
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                    });
                }
            } catch (Exception e) {
                Log.e(TAG, "Exception capture: " + e.getMessage());
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Erreur: " + e.getMessage());
                    btnCapture.setText("Capturer");
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                });
            } finally {
                capturing = false;
            }
        }).start();
    }
    
    private void verifyFingerprintAndRole(byte[] capturedTemplate) {
        new Thread(() -> {
            try {
                com.onip.biometric.models.Employee matchedEmployee = null;
                int bestScore = 0;
                String bestFinger = null;
                
                int timeOut = 5;
                int far = FalseAcceptanceRate.MORPHO_FAR_5;
                Coder coder = Coder.MORPHO_DEFAULT_CODER;
                int detectModeChoice = DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                        | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue();
                int matchingStrategy = MatchingStrategy.MORPHO_STANDARD_MATCHING_STRATEGY.getValue();
                int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue();
                
                String[] priorityFingers = {"Index_Droit", "Pouce_Droit", "Index_Gauche"};
                
                Log.d(TAG, "=== VÉRIFICATION EMPREINTE ET RÔLE ===");
                Log.d(TAG, "Employés à vérifier: " + allEmployeesWithFingerprints.size());
                Log.d(TAG, "Templates disponibles: " + allTemplatesForAuth.size() + " employés");
                
                // Vérifier tous les employés avec templates
                for (com.onip.biometric.models.Employee emp : allEmployeesWithFingerprints) {
                    if (!allTemplatesForAuth.containsKey(emp.getId())) {
                        continue;
                    }
                    
                    Map<String, byte[]> empTemplates = allTemplatesForAuth.get(emp.getId());
                    
                    // Vérifier les doigts prioritaires
                    for (String fingerName : priorityFingers) {
                        if (empTemplates.containsKey(fingerName)) {
                            byte[] storedTemplate = empTemplates.get(fingerName);
                            
                            TemplateList templateList = new TemplateList();
                            Template storedTemplateObj = new Template();
                            storedTemplateObj.setData(storedTemplate);
                            storedTemplateObj.setTemplateType(TemplateType.MORPHO_PK_ISO_FMR);
                            templateList.putTemplate(storedTemplateObj);
                            
                            ResultMatching resultMatching = new ResultMatching();
                            int ret = morphoDevice.verify(timeOut, far, coder, detectModeChoice, matchingStrategy,
                                    templateList, callbackCmd, processObserver, resultMatching);
                            
                            if (ret == ErrorCodes.MORPHO_OK && resultMatching != null) {
                                int matchingScore = resultMatching.getMatchingScore();
                                Log.d(TAG, "  - " + emp.getFirstName() + " " + emp.getLastName() + 
                                          " (" + fingerName + "): score=" + matchingScore + ", role=" + emp.getRole());
                                
                                if (matchingScore > bestScore) {
                                    bestScore = matchingScore;
                                    matchedEmployee = emp;
                                    bestFinger = fingerName;
                                }
                                
                                // Arrêt anticipé si score excellent
                                if (matchingScore >= 75) {
                                    break;
                                }
                            }
                        }
                    }
                    
                    if (bestScore >= 75) {
                        break;
                    }
                }
                
                // Vérifier si match trouvé ET si l'employé est super_admin
                final com.onip.biometric.models.Employee finalMatchedEmployee = matchedEmployee;
                final int finalBestScore = bestScore;
                
                if (finalMatchedEmployee != null && finalBestScore >= 50) {
                    Log.d(TAG, "✅ Match trouvé: " + finalMatchedEmployee.toString() + 
                              " (score: " + finalBestScore + ", role: " + finalMatchedEmployee.getRole() + ")");
                    
                    if (finalMatchedEmployee.isSuperAdmin()) {
                        // Authentification réussie - Super Admin
                        Log.d(TAG, "✅ Authentification réussie: Super Admin");
                        runOnUiThread(() -> {
                            txtStatus.setText("✅ Connexion réussie\n" + finalMatchedEmployee.getFirstName() + " " + finalMatchedEmployee.getLastName());
                            Toast.makeText(AuthActivity.this, "Connexion réussie", Toast.LENGTH_SHORT).show();
                            
                            // Naviguer immédiatement vers ThreeStepEmployeeActivity (formulaire d'enregistrement)
                            Intent intent = new Intent(AuthActivity.this, com.onip.biometric.activities.ThreeStepEmployeeActivity.class);
                            startActivity(intent);
                            finish();
                        });
                    } else {
                        // Match trouvé mais pas super_admin
                        Log.d(TAG, "❌ Empreinte reconnue mais pas super_admin: " + finalMatchedEmployee.getRole());
                        runOnUiThread(() -> {
                            txtStatus.setText("❌ Accès refusé\nVous n'êtes pas administrateur");
                            btnCapture.setText("Réessayer");
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                            Toast.makeText(AuthActivity.this, "Accès refusé - Administrateur requis", Toast.LENGTH_LONG).show();
                        });
                    }
                } else {
                    // Pas de correspondance
                    Log.d(TAG, "❌ Aucune correspondance trouvée (meilleur score: " + finalBestScore + ")");
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Empreinte non reconnue");
                        btnCapture.setText("Réessayer");
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        Toast.makeText(AuthActivity.this, "Empreinte non reconnue", Toast.LENGTH_LONG).show();
                    });
                }
            } catch (Exception e) {
                Log.e(TAG, "Exception vérification: " + e.getMessage(), e);
                runOnUiThread(() -> {
                    txtStatus.setText("Erreur: " + e.getMessage());
                    btnCapture.setText("Réessayer");
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                });
            } finally {
                capturing = false;
            }
        }).start();
    }
    
    private String getErrorMessage(int errorCode) {
        switch (errorCode) {
            case ErrorCodes.MORPHO_OK: return "Succès";
            case ErrorCodes.MORPHOERR_TIMEOUT: return "Timeout";
            case ErrorCodes.MORPHOERR_CMDE_ABORTED: return "Capture interrompue";
            case ErrorCodes.MORPHOERR_UNAVAILABLE: return "Périphérique non disponible";
            case ErrorCodes.MORPHOERR_INVALID_FINGER: return "Empreinte invalide";
            default: return "Erreur code: " + errorCode;
        }
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (morphoDevice != null) {
            try {
                morphoDevice.closeDevice();
            } catch (Exception e) {
                Log.e(TAG, "Erreur fermeture périphérique: " + e.getMessage());
            }
        }
    }
}

