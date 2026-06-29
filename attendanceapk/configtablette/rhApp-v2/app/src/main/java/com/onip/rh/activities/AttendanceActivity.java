package com.onip.rh.activities;

import android.app.Activity;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import com.onip.rh.RHApplication;
import com.onip.rh.R;
import com.onip.rh.fingerprint.FingerprintProcessObserver;
import com.onip.rh.models.Employee;
import com.onip.rh.services.AttendanceService;
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
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Activité pour marquer la présence avec empreinte digitale
 * Version fluide et optimisée
 */
public class AttendanceActivity extends Activity {
    
    private static final String TAG = "AttendanceActivity";
    
    // UI Components
    private TextView txtStatus;
    private ImageView imgFingerprint;
    private ProgressBar progressBar;
    private Button btnCapture;
    private Button btnBack;
    
    // MorphoSmart Components
    private MorphoDevice morphoDevice;
    private FingerprintProcessObserver processObserver;
    private boolean capturing = false;
    
    // Gestion des employés et présences
    private List<Employee> employees = new ArrayList<>();
    private Employee matchedEmployee = null;
    
    // Services
    private AttendanceService attendanceService;
    
    // Application globale
    private RHApplication app;
    
    // Templates chargés pour le matching
    private Map<Integer, Map<String, byte[]>> allTemplates = new HashMap<>();
    
    // Doigts prioritaires pour matching rapide
    private static final String[] priorityFingers = {"Index_Droit", "Pouce_Droit", "Index_Gauche"};
    
    // Handler pour retour automatique
    private Handler autoReturnHandler = new Handler(Looper.getMainLooper());
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_attendance);
        
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        
        app = (RHApplication) getApplication();
        attendanceService = new AttendanceService(this);
        
        initializeViews();
        loadGlobalData();
    }
    
    private void initializeViews() {
        txtStatus = findViewById(R.id.txt_attendance_status);
        imgFingerprint = findViewById(R.id.img_attendance_fingerprint);
        progressBar = findViewById(R.id.progress_attendance);
        btnCapture = findViewById(R.id.btn_capture_attendance);
        btnBack = findViewById(R.id.btn_back_attendance);
        
        txtStatus.setText("Placez votre doigt sur le capteur");
        btnCapture.setText("Capturer");
        btnCapture.setOnClickListener(v -> captureFingerprint());
        btnBack.setOnClickListener(v -> finish());
    }
    
    private void loadGlobalData() {
        morphoDevice = app.getGlobalMorphoDevice();
        employees = app.getGlobalEmployees();
        allTemplates = app.getGlobalTemplates();
        
        Log.d(TAG, "✅ Données chargées:");
        Log.d(TAG, "   - Employés: " + employees.size());
        Log.d(TAG, "   - Templates: " + allTemplates.size() + " employé(s)");
        Log.d(TAG, "   - Device: " + (morphoDevice != null ? "✅" : "❌"));
        
        if (morphoDevice == null) {
            txtStatus.setText("❌ Capteur non disponible\nVeuillez redémarrer l'application");
            btnCapture.setEnabled(false);
            return;
        }
        
        if (employees.isEmpty() || allTemplates.isEmpty()) {
            txtStatus.setText("❌ Données non chargées\nVeuillez redémarrer l'application");
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
                        | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue();
                
                Template capturedTemplate = new Template();
                
                int ret = morphoDevice.capture(timeout, acquisitionThreshold, advancedSecurityLevelsRequired,
                        fingerNumber, templateType, templateFVPType, maxSizeTemplate, enrollType,
                        latentDetection, coderChoice, detectModeChoice, templateList, callbackCmd, processObserver);
                
                if (ret == ErrorCodes.MORPHO_OK) {
                    if (templateList.getNbTemplate() == 1) {
                        Template template = templateList.getTemplate(0);
                        byte[] templateData = template.getData();
                        Log.d(TAG, "✅ Empreinte capturée");
                        if (templateData != null) {
                            matchFingerprint(templateData);
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
    
    private void matchFingerprint(byte[] capturedTemplate) {
        new Thread(() -> {
            Log.d(TAG, "=== MATCHING OPTIMISÉ ===");
            
            long startTime = System.currentTimeMillis();
            
            int timeOut = 5;
            int far = FalseAcceptanceRate.MORPHO_FAR_5;
            Coder coder = Coder.MORPHO_DEFAULT_CODER;
            int detectModeChoice = DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                    | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue();
            int matchingStrategy = MatchingStrategy.MORPHO_STANDARD_MATCHING_STRATEGY.getValue();
            int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()
                    | CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue();
            
            Employee bestMatch = null;
            int bestScore = 0;
            String bestFinger = null;
            
            // Vérification séquentielle avec arrêt anticipé
            for (Employee employee : employees) {
                if (!allTemplates.containsKey(employee.getId())) {
                    continue;
                }
                
                Map<String, byte[]> empTemplates = allTemplates.get(employee.getId());
                
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
                                templateList, callbackCmd, null, resultMatching);
                        
                        if (ret == ErrorCodes.MORPHO_OK && resultMatching != null) {
                            int matchingScore = resultMatching.getMatchingScore();
                            
                            if (matchingScore > bestScore) {
                                bestScore = matchingScore;
                                bestMatch = employee;
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
            
            long elapsedTime = System.currentTimeMillis() - startTime;
            Log.d(TAG, "Matching terminé en " + elapsedTime + "ms");
            
            final Employee finalMatch = bestMatch;
            final int finalScore = bestScore;
            
            if (finalMatch != null && finalScore >= 50) {
                Log.d(TAG, "✅ CORRESPONDANCE: " + finalMatch.toString() + " (score: " + finalScore + ")");
                matchedEmployee = finalMatch;
                
                runOnUiThread(() -> {
                    txtStatus.setText("✅ Empreinte reconnue\n\n" +
                                    "👤 " + finalMatch.getFirstName() + " " + finalMatch.getLastName() + "\n" +
                                    "Vérification de la présence...");
                });
                
                recordAttendanceForEmployee(finalMatch);
            } else {
                Log.d(TAG, "❌ AUCUNE CORRESPONDANCE (score: " + finalScore + ")");
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Empreinte non reconnue\n\nScore: " + finalScore);
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                    capturing = false;
                    
                    // Retry automatique après 2 secondes
                    autoReturnHandler.postDelayed(() -> {
                        if (!capturing) {
                            captureFingerprint();
                        }
                    }, 2000);
                });
            }
        }).start();
    }
    
    private void recordAttendanceForEmployee(Employee employee) {
        Log.d(TAG, "Enregistrement de présence pour: " + employee.toString());
        
        attendanceService.getTodayAttendance(employee.getId(), 
            new AttendanceService.AttendanceHistoryCallback() {
                @Override
                public void onSuccess(List<AttendanceService.AttendanceRecord> records) {
                    if (records != null && records.size() >= 2) {
                        Log.d(TAG, "✅ Empreinte reconnue - Présence complète");
                        runOnUiThread(() -> {
                            txtStatus.setText("✅ Empreinte reconnue\n\n" +
                                            "👤 " + employee.getFirstName() + " " + employee.getLastName() + "\n\n" +
                                            "⚠️ Présence complète\n" +
                                            "Vous avez déjà marqué votre arrivée et départ aujourd'hui\n\n" +
                                            "📍 Arrivée: " + (records.size() > 0 ? records.get(0).time : "N/A") + "\n" +
                                            "📍 Départ: " + (records.size() > 1 ? records.get(1).time : "N/A"));
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                            
                            // Retour automatique après 3 secondes
                            autoReturnHandler.postDelayed(() -> {
                                finish();
                            }, 3000);
                        });
                        return;
                    }
                    
                    String attendanceType = determineAttendanceType(employee, records);
                    
                    if (attendanceType == null) {
                        runOnUiThread(() -> {
                            txtStatus.setText("⚠️ Présence complète\n\nArrivée et départ déjà enregistrés");
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                            
                            autoReturnHandler.postDelayed(() -> {
                                finish();
                            }, 3000);
                        });
                        return;
                    }
                    
                    String typeLabel = attendanceType.equals("checkin") ? "Arrivée" : "Départ";
                    runOnUiThread(() -> {
                        txtStatus.setText("👤 Employé reconnu: " + employee.getFirstName() + " " + employee.getLastName() + 
                                        "\n📍 Type: " + typeLabel + "\n\nEnregistrement en cours...");
                    });
                    
                    recordAttendanceWithType(employee, attendanceType, "fingerprint_capture");
                }
                
                @Override
                public void onError(String error) {
                    Log.w(TAG, "Erreur récupération historique: " + error);
                    String attendanceType = determineAttendanceType(employee, null);
                    if (attendanceType != null) {
                        recordAttendanceWithType(employee, attendanceType, "fingerprint_capture");
                    } else {
                        runOnUiThread(() -> {
                            txtStatus.setText("❌ Erreur récupération historique");
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                            capturing = false;
                        });
                    }
                }
            });
    }
    
    private String determineAttendanceType(Employee employee, List<AttendanceService.AttendanceRecord> todayRecords) {
        if (todayRecords == null || todayRecords.isEmpty()) {
            return "checkin"; // Première présence = arrivée
        }
        
        if (todayRecords.size() >= 2) {
            return null; // Déjà complet
        }
        
        return "checkout"; // Deuxième présence = départ
    }
    
    private void recordAttendanceWithType(Employee employee, String attendanceType, String fingerprintUsed) {
        attendanceService.recordAttendance(employee.getId(), attendanceType, fingerprintUsed, 
            new AttendanceService.Callback() {
                @Override
                public void onSuccess(String message) {
                    String currentTime = new java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
                            .format(new java.util.Date());
                    String typeLabel = attendanceType.equals("checkin") ? "Arrivée" : "Départ";
                    
                    runOnUiThread(() -> {
                        String displayMessage = "✅ " + typeLabel + " enregistrée !\n" +
                                              "👤 " + employee.getFirstName() + " " + employee.getLastName() + "\n" +
                                              "📍 " + typeLabel + " à " + currentTime;
                        txtStatus.setText(displayMessage);
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        capturing = false;
                        
                        Toast.makeText(AttendanceActivity.this, 
                                     typeLabel + " enregistrée à " + currentTime, 
                                     Toast.LENGTH_LONG).show();
                        
                        // Retour automatique après 3 secondes
                        autoReturnHandler.postDelayed(() -> {
                            finish();
                        }, 3000);
                    });
                }
                
                @Override
                public void onError(String error) {
                    Log.e(TAG, "Erreur enregistrement présence: " + error);
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Erreur enregistrement\n" + error);
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        capturing = false;
                    });
                }
            });
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        autoReturnHandler.removeCallbacksAndMessages(null);
    }
}

