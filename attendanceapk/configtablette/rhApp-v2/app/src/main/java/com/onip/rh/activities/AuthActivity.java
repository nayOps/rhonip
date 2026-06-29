package com.onip.rh.activities;

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
import com.onip.rh.RHApplication;
import com.onip.rh.R;
import com.onip.rh.models.Employee;
import com.onip.rh.fingerprint.FingerprintProcessObserver;
import com.morpho.morphosmart.sdk.CallbackMask;
import com.morpho.morphosmart.sdk.Coder;
import com.morpho.morphosmart.sdk.DetectionMode;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.FalseAcceptanceRate;
import com.morpho.morphosmart.sdk.MatchingStrategy;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.ResultMatching;
import com.morpho.morphosmart.sdk.Template;
import com.morpho.morphosmart.sdk.TemplateList;
import com.morpho.morphosmart.sdk.TemplateType;
import com.morpho.morphosmart.sdk.TemplateFVPType;
import com.morpho.morphosmart.sdk.EnrollmentType;
import com.morpho.morphosmart.sdk.LatentDetection;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

/**
 * Activité d'authentification
 * Vérifie que l'utilisateur est super_admin avant d'autoriser l'enregistrement
 */
public class AuthActivity extends Activity {
    
    private static final String TAG = "AuthActivity";
    
    private TextView txtTitle;
    private TextView txtStatus;
    private ImageView imgFingerprint;
    private ProgressBar progressBar;
    private Button btnCapture;
    private Button btnBack;
    
    private MorphoDevice morphoDevice;
    private FingerprintProcessObserver processObserver;
    private boolean capturing = false;
    
    private RHApplication app;
    private List<Employee> allEmployeesWithFingerprints = new ArrayList<>();
    private Map<Integer, Map<String, byte[]>> allTemplatesForAuth;
    
    // Doigts prioritaires pour matching rapide
    private static final String[] priorityFingers = {"Index_Droit", "Pouce_Droit", "Index_Gauche"};
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_auth);
        
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        
        app = (RHApplication) getApplication();
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
        
        txtTitle.setText("Authentification");
        txtStatus.setText("Placez votre doigt pour vous authentifier");
        
        btnCapture.setText("Connexion");
        btnCapture.setOnClickListener(v -> captureFingerprint());
        btnBack.setOnClickListener(v -> finish());
    }
    
    private void loadGlobalData() {
        morphoDevice = app.getGlobalMorphoDevice();
        allEmployeesWithFingerprints = app.getGlobalEmployees();
        allTemplatesForAuth = app.getGlobalTemplates();
        
        Log.d(TAG, "✅ Données chargées:");
        Log.d(TAG, "   - Employés: " + allEmployeesWithFingerprints.size());
        Log.d(TAG, "   - Templates: " + allTemplatesForAuth.size() + " employé(s)");
        Log.d(TAG, "   - Device: " + (morphoDevice != null ? "✅" : "❌"));
        
        if (morphoDevice == null) {
            txtStatus.setText("❌ Capteur non disponible\nVeuillez redémarrer l'application");
            btnCapture.setEnabled(false);
            return;
        }
        
        if (allEmployeesWithFingerprints.isEmpty()) {
            txtStatus.setText("❌ Aucun employé chargé\nVeuillez redémarrer l'application");
            btnCapture.setEnabled(false);
            return;
        }
        
        btnCapture.setEnabled(true);
    }
    
    private void captureFingerprint() {
        if (capturing || morphoDevice == null) {
            return;
        }
        
        capturing = true;
        btnCapture.setEnabled(false);
        progressBar.setVisibility(View.VISIBLE);
        txtStatus.setText("Capture en cours... Placez votre doigt");
        
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
                        byte[] templateData = template.getData();
                        Log.d(TAG, "✅ Empreinte capturée");
                        if (templateData != null) {
                            verifyFingerprintAndRole(templateData);
                        } else {
                            throw new Exception("Template data is null");
                        }
                    } else {
                        throw new Exception("No template in list");
                    }
                } else {
                    Log.e(TAG, "❌ Erreur capture: " + ret);
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Erreur de capture\nCode: " + ret);
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        capturing = false;
                    });
                }
                
            } catch (Exception e) {
                Log.e(TAG, "❌ Exception capture: " + e.getMessage(), e);
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Erreur: " + e.getMessage());
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                    capturing = false;
                });
            }
        }).start();
    }
    
    private void verifyFingerprintAndRole(byte[] capturedTemplate) {
        new Thread(() -> {
            Log.d(TAG, "=== VÉRIFICATION EMPREINTE ET RÔLE ===");
            
            Employee matchedEmployee = null;
            int bestScore = 0;
            String bestFinger = null;
            
            // Vérifier tous les employés avec templates
            for (Employee emp : allEmployeesWithFingerprints) {
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
                        int ret = morphoDevice.verify(5, FalseAcceptanceRate.MORPHO_FAR_5, 
                                Coder.MORPHO_DEFAULT_CODER,
                                DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                                        | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue(),
                                MatchingStrategy.MORPHO_STANDARD_MATCHING_STRATEGY.getValue(),
                                templateList, CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()
                                        | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue(),
                                null, resultMatching);
                        
                        if (ret == ErrorCodes.MORPHO_OK && resultMatching != null) {
                            int matchingScore = resultMatching.getMatchingScore();
                            
                            if (matchingScore > bestScore) {
                                bestScore = matchingScore;
                                matchedEmployee = emp;
                                bestFinger = fingerName;
                            }
                            
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
            final Employee finalMatchedEmployee = matchedEmployee;
            final int finalBestScore = bestScore;
            
            if (finalMatchedEmployee != null && finalBestScore >= 50) {
                Log.d(TAG, "✅ Match trouvé: " + finalMatchedEmployee.toString() + 
                          " (score: " + finalBestScore + ", role: " + finalMatchedEmployee.getRole() + ")");
                
                if (finalMatchedEmployee.isSuperAdmin()) {
                    // Authentification réussie
                    runOnUiThread(() -> {
                        txtStatus.setText("✅ Authentification réussie\n" + 
                                        finalMatchedEmployee.getFirstName() + " " + 
                                        finalMatchedEmployee.getLastName());
                        Toast.makeText(this, "Authentification réussie", Toast.LENGTH_SHORT).show();
                        
                        // Naviguer vers le formulaire d'enregistrement
                        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {
                            Intent intent = new Intent(AuthActivity.this, EmployeeEnrollmentActivity.class);
                            startActivity(intent);
                            finish();
                        }, 1500);
                    });
                } else {
                    // Match mais pas super_admin
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Accès refusé\nVous n'êtes pas administrateur");
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        capturing = false;
                        Toast.makeText(this, "Accès refusé - Administrateur requis", Toast.LENGTH_LONG).show();
                    });
                }
            } else {
                // Pas de match
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Empreinte non reconnue\nVeuillez réessayer");
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                    capturing = false;
                });
            }
        }).start();
    }
}

