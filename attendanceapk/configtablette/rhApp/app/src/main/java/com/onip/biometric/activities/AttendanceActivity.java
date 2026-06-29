package com.onip.biometric.activities;

import android.app.Activity;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.biometric.ONIPApplication;
import com.onip.biometric.R;
import com.onip.biometric.fingerprint.FingerprintProcessObserver;
import com.onip.biometric.models.Employee;
import com.onip.biometric.services.AttendanceService;
import com.onip.biometric.services.EmployeeService;
import com.onip.biometric.services.FingerprintTemplateService;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// Imports MorphoSmart SDK
import com.morpho.android.usb.USBManager;
import com.morpho.morphosmart.sdk.CallbackMask;
import com.morpho.morphosmart.sdk.Coder;
import com.morpho.morphosmart.sdk.DetectionMode;
import com.morpho.morphosmart.sdk.EnrollmentType;
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

import java.util.ArrayList;
import java.util.List;

/**
 * Activité pour marquer la présence avec empreinte digitale
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
    private boolean deviceInitialized = false;
    private boolean capturing = false;
    
    // Gestion des employés et présences
    private List<Employee> employees = new ArrayList<>();
    private Employee matchedEmployee = null;
    private String lastAttendanceType = null;
    private long lastAttendanceTime = 0;
    
    // Services
    private AttendanceService attendanceService;
    
    // Application globale
    private ONIPApplication app;
    
    // Templates chargés pour le matching (depuis l'application globale)
    private Map<Integer, Map<String, byte[]>> allTemplates = new HashMap<>(); // employeeId -> templates
    
    // Gestion d'états pour stabilisation
    private enum AppState {
        READY,             // Prêt (bouton activable)
        CAPTURING,         // Capture en cours
        MATCHING,          // Matching en cours
        ERROR              // Erreur
    }
    private AppState appState = AppState.READY;
    
    // Handler pour UI
    private android.os.Handler progressHandler;
    
    // APPROCHE HYBRIDE : Ordre de priorité pour le matching (2-3 doigts prioritaires)
    // Ordre optimisé : Index_Droit (le plus utilisé) → Pouce_Droit (le plus facile) → Index_Gauche (backup)
    private static final String[] priorityFingers = {"Index_Droit", "Pouce_Droit", "Index_Gauche"};
    
    // Classe interne pour mapper index template -> employé/doigt
    private static class TemplateInfo {
        Employee employee;
        String fingerName;
        
        TemplateInfo(Employee employee, String fingerName) {
            this.employee = employee;
            this.fingerName = fingerName;
        }
    }
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_attendance);
        
        // Forcer l'orientation portrait
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        
        // Garder l'écran actif (pas de veille)
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        
        app = (ONIPApplication) getApplication();
        
        // Handler pour synchronisation barre de progression
        progressHandler = new android.os.Handler(android.os.Looper.getMainLooper());
        
        initializeViews();
        initializeServices();
        
        // Récupérer les données depuis l'application globale
        loadGlobalData();
    }
    
    private void loadGlobalData() {
        // Récupérer le MorphoDevice depuis l'application globale
        morphoDevice = app.getGlobalMorphoDevice();
        deviceInitialized = app.isDeviceInitialized();
        
        // Récupérer les employés depuis l'application globale
        employees = app.getGlobalEmployees();
        
        // Récupérer les templates depuis l'application globale
        allTemplates = app.getGlobalTemplates();
        
        Log.d(TAG, "✅ Données chargées depuis l'application globale:");
        Log.d(TAG, "   - Employés: " + employees.size());
        Log.d(TAG, "   - Templates: " + allTemplates.size() + " employé(s)");
        Log.d(TAG, "   - Device initialisé: " + deviceInitialized);
        
        if (employees.isEmpty()) {
            setAppState(AppState.ERROR);
            runOnUiThread(() -> {
                txtStatus.setText("❌ Aucun employé chargé\nVeuillez redémarrer l'application");
                btnCapture.setEnabled(false);
            });
            return;
        }
        
        if (!deviceInitialized || morphoDevice == null) {
            setAppState(AppState.ERROR);
            runOnUiThread(() -> {
                txtStatus.setText("❌ Capteur non disponible\nVeuillez redémarrer l'application");
                btnCapture.setEnabled(false);
            });
            return;
        }
        
        // Tout est prêt
        setAppState(AppState.READY);
        runOnUiThread(() -> {
            txtStatus.setText("Prêt - Placez votre doigt et cliquez 'Capturer'");
            btnCapture.setEnabled(true);
        });
    }
    
    private void setAppState(AppState newState) {
        appState = newState;
        updateButtonState();
        Log.d(TAG, "État changé: " + newState);
    }
    
    private void updateButtonState() {
        boolean canCapture = (appState == AppState.READY) && 
                            deviceInitialized && 
                            !employees.isEmpty() && 
                            !allTemplates.isEmpty() &&
                            !capturing;
        
        runOnUiThread(() -> {
            btnCapture.setEnabled(canCapture);
            if (canCapture) {
                btnCapture.setText("Capturer Empreinte");
            } else {
                switch (appState) {
                    case CAPTURING:
                    case MATCHING:
                        btnCapture.setText("En cours...");
                        break;
                    case ERROR:
                        btnCapture.setText("Erreur");
                        break;
                    default:
                        btnCapture.setText("Capturer Empreinte");
                }
            }
        });
    }
    
    @Override
    protected void onResume() {
        super.onResume();
        // Vérifier que les données sont toujours disponibles
        if (morphoDevice == null || !deviceInitialized) {
            morphoDevice = app.getGlobalMorphoDevice();
            deviceInitialized = app.isDeviceInitialized();
            updateButtonState();
        }
    }
    
    @Override
    protected void onPause() {
        super.onPause();
        // Libérer le capteur si nécessaire (optionnel)
        // Le capteur reste actif pour performance
    }
    
    private void initializeViews() {
        txtStatus = findViewById(R.id.txt_attendance_status);
        imgFingerprint = findViewById(R.id.img_fingerprint);
        progressBar = findViewById(R.id.progress_attendance);
        btnCapture = findViewById(R.id.btn_capture_attendance);
        btnBack = findViewById(R.id.btn_back_attendance);
        
        btnCapture.setOnClickListener(v -> captureFingerprint());
        btnBack.setOnClickListener(v -> finish());
        
        txtStatus.setText("Chargement...");
        btnCapture.setEnabled(false);
    }
    
    private void initializeServices() {
        attendanceService = new AttendanceService(this);
    }
    
    private void captureFingerprint() {
        // Vérifier que le device est toujours disponible
        if (morphoDevice == null || !deviceInitialized) {
            morphoDevice = app.getGlobalMorphoDevice();
            deviceInitialized = app.isDeviceInitialized();
        }
        
        if (!deviceInitialized || morphoDevice == null) {
            Log.e(TAG, "❌ Périphérique non initialisé - deviceInitialized: " + deviceInitialized + ", morphoDevice: " + (morphoDevice != null));
            Toast.makeText(this, "Périphérique non initialisé. Redémarrez l'application.", Toast.LENGTH_LONG).show();
            return;
        }
        
        if (employees.isEmpty()) {
            Log.e(TAG, "❌ Aucun employé chargé");
            Toast.makeText(this, "Aucun employé chargé. Redémarrez l'application.", Toast.LENGTH_LONG).show();
            return;
        }
        
        capturing = true;
        setAppState(AppState.CAPTURING);
        runOnUiThread(() -> {
            btnCapture.setEnabled(false);
            btnCapture.setText("Capture en cours...");
            progressBar.setVisibility(View.VISIBLE);
            progressBar.setProgress(0);
            txtStatus.setText("Placez votre doigt sur le capteur...");
        });
        
        Log.d(TAG, "=== DÉBUT CAPTURE EMPREINTE ===");
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
                
                Log.d(TAG, "Appel morphoDevice.capture()...");
                int ret = morphoDevice.capture(timeout, acquisitionThreshold, advancedSecurityLevelsRequired,
                        fingerNumber, templateType, templateFVPType, maxSizeTemplate, enrollType,
                        latentDetection, coderChoice, detectModeChoice, templateList, callbackCmd, processObserver);
                
                Log.d(TAG, "Capture result: " + ret + " (MORPHO_OK=" + ErrorCodes.MORPHO_OK + ")");
                
                if (ret == ErrorCodes.MORPHO_OK) {
                    if (templateList.getNbTemplate() == 1) {
                        Template template = templateList.getTemplate(0);
                        byte[] capturedTemplate = template.getData();
                        
                        setAppState(AppState.MATCHING);
                        runOnUiThread(() -> {
                            txtStatus.setText("Empreinte capturée\nRecherche de correspondance...");
                            progressBar.setVisibility(View.GONE);
                        });
                        
                        // Vérifier la présence avec SDK MorphoSmart
                        matchWithMorphoSDK(capturedTemplate);
                    }
                } else {
                    setAppState(AppState.READY);
                    runOnUiThread(() -> {
                        txtStatus.setText("Erreur capture: " + getErrorMessage(ret));
                        btnCapture.setText("Capturer Empreinte");
                        btnCapture.setEnabled(true);
                        Toast.makeText(AttendanceActivity.this, "Erreur: " + getErrorMessage(ret), Toast.LENGTH_LONG).show();
                    });
                }
                
            } catch (Exception e) {
                Log.e(TAG, "Exception capture: " + e.getMessage());
                setAppState(AppState.READY);
                runOnUiThread(() -> {
                    txtStatus.setText("Erreur: " + e.getMessage());
                    btnCapture.setText("Capturer Empreinte");
                    btnCapture.setEnabled(true);
                });
            } finally {
                capturing = false;
            }
        }).start();
    }
    
    /**
     * Compare le template capturé avec tous les templates stockés
     * OPTIMISATION : Utilise UNE SEULE vérification avec TemplateList contenant TOUS les templates
     * Beaucoup plus rapide que de vérifier template par template
     */
    private void matchWithMorphoSDK(byte[] capturedTemplate) {
        if (morphoDevice == null || !deviceInitialized) {
            Log.e(TAG, "Périphérique MorphoSmart non initialisé");
            setAppState(AppState.READY);
            runOnUiThread(() -> {
                txtStatus.setText("❌ Capteur non disponible");
                btnCapture.setText("Capturer Empreinte");
                btnCapture.setEnabled(true);
            });
            return;
        }
        
        if (employees.isEmpty() || allTemplates.isEmpty()) {
            Log.e(TAG, "Données non chargées - employees: " + employees.size() + ", templates: " + allTemplates.size());
            setAppState(AppState.ERROR);
            runOnUiThread(() -> {
                txtStatus.setText("❌ Données non chargées\nVeuillez redémarrer l'application");
                btnCapture.setText("Erreur");
                btnCapture.setEnabled(false);
            });
            return;
        }
        
        new Thread(() -> {
            try {
                Log.d(TAG, "=== MATCHING OPTIMISÉ AVEC SDK MORPHOSMART ===");
                Log.d(TAG, "Employés à vérifier: " + employees.size());
                Log.d(TAG, "Templates disponibles: " + allTemplates.size() + " employé(s)");
                
                runOnUiThread(() -> {
                    txtStatus.setText("Recherche de correspondance...");
                });
                
                long startTime = System.currentTimeMillis();
                
                // Paramètres pour morphoDevice.verify()
                int timeOut = 5; // Timeout augmenté pour meilleure reconnaissance
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
                int comparisonsDone = 0;
                
                // OPTIMISATION : Vérification séquentielle avec arrêt anticipé
                // Vérifier d'abord les doigts prioritaires, puis tous les autres si nécessaire
                for (Employee employee : employees) {
                    if (!allTemplates.containsKey(employee.getId())) {
                        continue;
                    }
                    
                    Map<String, byte[]> empTemplates = allTemplates.get(employee.getId());
                    
                    // Vérifier les doigts prioritaires en premier
                    for (String fingerName : priorityFingers) {
                        if (empTemplates.containsKey(fingerName)) {
                            byte[] storedTemplate = empTemplates.get(fingerName);
                            comparisonsDone++;
                            
                            Log.d(TAG, "Vérification " + employee.getFirstName() + " " + employee.getLastName() + " - " + fingerName);
                            
                            // Créer la TemplateList avec le template stocké
                            TemplateList templateList = new TemplateList();
                            Template storedTemplateObj = new Template();
                            storedTemplateObj.setData(storedTemplate);
                            storedTemplateObj.setTemplateType(TemplateType.MORPHO_PK_ISO_FMR);
                            templateList.putTemplate(storedTemplateObj);
                            
                            // Résultat de la correspondance
                            ResultMatching resultMatching = new ResultMatching();
                            
                            // VÉRIFICATION AVEC SDK MORPHOSMART
                            int ret = morphoDevice.verify(timeOut, far, coder, detectModeChoice, matchingStrategy,
                                    templateList, callbackCmd, null, resultMatching);
                            
                            Log.d(TAG, "Résultat verify pour " + fingerName + ": " + ret);
                            
                            if (ret == ErrorCodes.MORPHO_OK && resultMatching != null) {
                                int matchingScore = resultMatching.getMatchingScore();
                                Log.d(TAG, "Score pour " + fingerName + ": " + matchingScore);
                                
                                if (matchingScore > bestScore) {
                                    bestScore = matchingScore;
                                    bestMatch = employee;
                                    bestFinger = fingerName;
                                    Log.d(TAG, "✅ NOUVEAU MEILLEUR MATCH: " + employee.toString() + 
                                              " - " + fingerName + " (score: " + matchingScore + ")");
                                }
                                
                                // OPTIMISATION : Arrêt anticipé si score excellent
                                if (matchingScore >= 75) {
                                    Log.d(TAG, "✅ Score excellent trouvé (" + matchingScore + "), arrêt de la recherche");
                                    break;
                                }
                            } else if (ret == ErrorCodes.MORPHOERR_INVALID_FINGER || ret == ErrorCodes.MORPHOERR_NO_HIT) {
                                // Pas de correspondance - normal, continuer
                                Log.d(TAG, "Pas de correspondance pour " + fingerName);
                            } else {
                                Log.w(TAG, "Erreur verify pour " + fingerName + ": " + ret);
                            }
                        }
                    }
                    
                    // Si pas de match avec les doigts prioritaires, vérifier tous les autres doigts
                    if (bestScore < 50) {
                        for (String fingerName : empTemplates.keySet()) {
                            // Skip les doigts prioritaires déjà vérifiés
                            boolean isPriority = false;
                            for (String priority : priorityFingers) {
                                if (priority.equals(fingerName)) {
                                    isPriority = true;
                                    break;
                                }
                            }
                            if (isPriority) continue;
                            
                            if (empTemplates.containsKey(fingerName)) {
                                byte[] storedTemplate = empTemplates.get(fingerName);
                                comparisonsDone++;
                                
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
                                        Log.d(TAG, "✅ MATCH avec " + fingerName + " (score: " + matchingScore + ")");
                                    }
                                    if (matchingScore >= 75) {
                                        break;
                                    }
                                }
                            }
                        }
                    }
                    
                    // OPTIMISATION : Arrêt anticipé si score excellent
                    if (bestScore >= 75) {
                        Log.d(TAG, "✅ Score excellent, arrêt de la recherche");
                        break;
                    }
                }
                
                long elapsedTime = System.currentTimeMillis() - startTime;
                Log.d(TAG, "Matching terminé en " + elapsedTime + "ms (" + comparisonsDone + " comparaisons)");
                
                // Résultat final
                final Employee finalMatch = bestMatch;
                final String finalFinger = bestFinger;
                final int finalScore = bestScore;
                
                // Seuil MorphoSmart : généralement 50+ est un bon match
                if (finalMatch != null && finalScore >= 50) {
                    Log.d(TAG, "✅ CORRESPONDANCE VALIDÉE: " + finalMatch.toString() + 
                              " - " + finalFinger + " (score MorphoSmart: " + finalScore + ")");
                    matchedEmployee = finalMatch;
                    setAppState(AppState.READY);
                    // Afficher d'abord la reconnaissance
                    runOnUiThread(() -> {
                        txtStatus.setText("✅ Empreinte reconnue\n\n" +
                                        "👤 " + finalMatch.getFirstName() + " " + finalMatch.getLastName() + "\n" +
                                        "Vérification de la présence...");
                        btnCapture.setText("Capturer Empreinte");
                        btnCapture.setEnabled(true);
                    });
                    // Ensuite vérifier et enregistrer la présence
                    recordAttendanceForEmployee(finalMatch);
                } else {
                    Log.d(TAG, "❌ AUCUNE CORRESPONDANCE (meilleur score: " + finalScore + ")");
                    setAppState(AppState.READY);
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Empreinte non reconnue\n\nScore: " + finalScore);
                        btnCapture.setText("Capturer Empreinte");
                        btnCapture.setEnabled(true);
                        Toast.makeText(AttendanceActivity.this, "Empreinte non reconnue (score: " + finalScore + ")", Toast.LENGTH_LONG).show();
                    });
                }
                
            } catch (Exception e) {
                Log.e(TAG, "Exception lors du matching SDK: " + e.getMessage(), e);
                setAppState(AppState.READY);
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Erreur: " + e.getMessage());
                    btnCapture.setText("Capturer Empreinte");
                    btnCapture.setEnabled(true);
                    Toast.makeText(AttendanceActivity.this, "Erreur matching: " + e.getMessage(), Toast.LENGTH_LONG).show();
                });
            } finally {
                capturing = false;
            }
        }).start();
    }
    
    
    
    /**
     * Vérifie un template capturé avec un template stocké en utilisant morphoDevice.verify()
     * @return Score de correspondance (0-100), ou -1 en cas d'erreur
     */
    private int verifyTemplate(byte[] capturedTemplate, byte[] storedTemplate) {
        if (morphoDevice == null || capturedTemplate == null || storedTemplate == null) {
            return -1;
        }
        
        try {
            int timeout = 5; // Timeout court pour matching rapide
            int far = FalseAcceptanceRate.MORPHO_FAR_5; // Taux d'erreur 1/100000
            Coder coder = Coder.MORPHO_DEFAULT_CODER;
            int detectModeChoice = DetectionMode.MORPHO_ENROLL_DETECT_MODE.getValue()
                    | DetectionMode.MORPHO_FORCE_FINGER_ON_TOP_DETECT_MODE.getValue();
            int matchingStrategy = MatchingStrategy.MORPHO_STANDARD_MATCHING_STRATEGY.getValue();
            
            // Créer la TemplateList avec le template stocké
            TemplateList templateList = new TemplateList();
            Template storedTemplateObj = new Template();
            storedTemplateObj.setData(storedTemplate);
            storedTemplateObj.setTemplateType(TemplateType.MORPHO_PK_ISO_FMR);
            templateList.putTemplate(storedTemplateObj);
            
            // Créer un template pour le doigt capturé
            Template capturedTemplateObj = new Template();
            capturedTemplateObj.setData(capturedTemplate);
            capturedTemplateObj.setTemplateType(TemplateType.MORPHO_PK_ISO_FMR);
            
            // Callbacks minimaux pour performance
            int callbackCmd = CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue();
            
            // Résultat de la correspondance
            ResultMatching resultMatching = new ResultMatching();
            
            // VÉRIFICATION AVEC LA MÉTHODE SDK OFFICIELLE
            // Note: morphoDevice.verify() compare le doigt sur le capteur avec les templates fournis
            // Ici, on doit utiliser une méthode de comparaison directe entre templates
            // Pour l'instant, on utilise une comparaison simplifiée basée sur la similarité
            
            // ALTERNATIVE: Utiliser morphoDevice.match() si disponible, sinon comparaison manuelle
            // Pour cette implémentation, on utilise une comparaison par similarité de bytes
            
            int similarity = calculateTemplateSimilarity(capturedTemplate, storedTemplate);
            return similarity;
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur vérification template: " + e.getMessage());
            return -1;
        }
    }
    
    /**
     * Calcule la similarité entre deux templates MorphoSmart (0-100)
     * 
     * Les templates MorphoSmart (FMR) contiennent des minutiae (points caractéristiques).
     * Cette méthode compare les structures et patterns communs avec une tolérance accrue.
     * 
     * Note: Pour un matching de production, utiliser morphoDevice.verify() avec le doigt sur le capteur.
     * Cette méthode est une approximation pour matching hors-ligne.
     */
    private int calculateTemplateSimilarity(byte[] template1, byte[] template2) {
        if (template1 == null || template2 == null || template1.length == 0 || template2.length == 0) {
            Log.d(TAG, "Template null ou vide");
            return 0;
        }
        
        // Vérifier le header MorphoSmart (FMR format)
        if (template1.length < 20 || template2.length < 20) {
            Log.d(TAG, "Template trop court: " + template1.length + " vs " + template2.length);
            return 0;
        }
        
        // Vérifier le header FMR (commence généralement par "FMR" en ASCII ou 0x46 0x4D 0x52)
        boolean headerMatch = (template1[0] == template2[0] && template1[1] == template2[1] && template1[2] == template2[2]);
        if (!headerMatch) {
            Log.d(TAG, "Headers différents - pas de correspondance");
            return 0;
        }
        
        // Comparaison multi-niveaux avec pondération améliorée
        double similarity = 0.0;
        
        // 1. Comparaison de la structure (header + taille) - Plus tolérant
        int sizeSimilarity = calculateSizeSimilarity(template1.length, template2.length);
        similarity += sizeSimilarity * 0.15; // 15% du score
        
        // 2. Comparaison par blocs (structure des données) - Plus tolérant
        int blockSimilarity = calculateBlockSimilarity(template1, template2);
        similarity += blockSimilarity * 0.40; // 40% du score
        
        // 3. Comparaison des patterns (minutiae patterns) - Plus important
        int patternSimilarity = calculatePatternSimilarity(template1, template2);
        similarity += patternSimilarity * 0.45; // 45% du score
        
        // Bonus si les tailles sont très proches
        int sizeDiff = Math.abs(template1.length - template2.length);
        if (sizeDiff <= 10) {
            similarity += 10; // Bonus de 10 points
        }
        
        // Ajustement final
        int finalScore = (int) Math.min(100, Math.max(0, similarity));
        
        Log.d(TAG, String.format("Similarité: taille=%d, blocs=%d, patterns=%d, final=%d", 
                sizeSimilarity, blockSimilarity, patternSimilarity, finalScore));
        
        return finalScore;
    }
    
    private int calculateSizeSimilarity(int size1, int size2) {
        int diff = Math.abs(size1 - size2);
        int maxSize = Math.max(size1, size2);
        if (maxSize == 0) return 0;
        
        // Les templates MorphoSmart ont généralement des tailles similaires pour le même doigt
        // Pénalité si différence > 10%
        double ratio = 1.0 - (double) diff / maxSize;
        return (int) (ratio * 100);
    }
    
    private int calculateBlockSimilarity(byte[] template1, byte[] template2) {
        int minLength = Math.min(template1.length, template2.length);
        if (minLength < 8) return 0;
        
        int blockSize = 8; // Blocs de 8 bytes
        int matchingBlocks = 0;
        int totalBlocks = minLength / blockSize;
        
        if (totalBlocks == 0) return 0;
        
        for (int i = 0; i < totalBlocks; i++) {
            int start = i * blockSize;
            int differences = 0;
            
            // Compter les différences dans le bloc
            for (int j = 0; j < blockSize && (start + j) < minLength; j++) {
                if (template1[start + j] != template2[start + j]) {
                    differences++;
                }
            }
            
            // Bloc considéré comme similaire si moins de 3 bytes différents (tolérance accrue)
            if (differences <= 2) {
                matchingBlocks++;
            }
        }
        
        return (matchingBlocks * 100) / totalBlocks;
    }
    
    private int calculatePatternSimilarity(byte[] template1, byte[] template2) {
        int minLength = Math.min(template1.length, template2.length);
        if (minLength < 16) return 0;
        
        // Analyser les patterns de bits (minutiae) avec fenêtre glissante
        int similarPatterns = 0;
        int windowSize = 4; // Fenêtre de 4 bytes pour détecter les patterns
        int step = 2; // Pas de 2 bytes pour fenêtre glissante (plus de couverture)
        
        for (int i = 0; i < minLength - windowSize; i += step) {
            // Calculer un "hash" simple du pattern
            int hash1 = calculatePatternHash(template1, i, windowSize);
            int hash2 = calculatePatternHash(template2, i, windowSize);
            
            // Si les hashs sont proches, pattern similaire (seuil augmenté pour tolérance)
            int diff = Math.abs(hash1 - hash2);
            if (diff < 50) { // Seuil de similarité augmenté (était 10)
                similarPatterns++;
            }
        }
        
        int totalWindows = (minLength - windowSize) / step;
        if (totalWindows == 0) return 0;
        
        return (similarPatterns * 100) / totalWindows;
    }
    
    private int calculatePatternHash(byte[] template, int start, int size) {
        int hash = 0;
        for (int i = 0; i < size && (start + i) < template.length; i++) {
            hash = (hash * 31) + (template[start + i] & 0xFF);
        }
        return Math.abs(hash);
    }
    
    private void recordAttendanceForEmployee(Employee employee) {
        Log.d(TAG, "Enregistrement de présence pour: " + employee.toString());
        
        runOnUiThread(() -> {
            txtStatus.setText("👤 Employé reconnu: " + employee.getFirstName() + " " + employee.getLastName() + 
                            "\n\nVérification de l'historique...");
        });
        
        // Récupérer l'historique pour déterminer le type
        attendanceService.getTodayAttendance(employee.getId(), 
            new AttendanceService.AttendanceHistoryCallback() {
                @Override
                public void onSuccess(List<AttendanceService.AttendanceRecord> records) {
                    // NOUVELLE VÉRIFICATION : Refuser si déjà 2 présences
                    if (records != null && records.size() >= 2) {
                        Log.d(TAG, "✅ Empreinte reconnue - " + employee.getFirstName() + " " + employee.getLastName());
                        Log.d(TAG, "⚠️ Déjà " + records.size() + " présences aujourd'hui - Présence complète");
                        runOnUiThread(() -> {
                            txtStatus.setText("✅ Empreinte reconnue\n\n" +
                                            "👤 " + employee.getFirstName() + " " + employee.getLastName() + "\n\n" +
                                            "⚠️ Présence complète\n" +
                                            "Vous avez déjà marqué votre arrivée et départ aujourd'hui\n\n" +
                                            "📍 Arrivée: " + (records.size() > 0 ? records.get(0).time : "N/A") + "\n" +
                                            "📍 Départ: " + (records.size() > 1 ? records.get(1).time : "N/A"));
                            btnCapture.setText("Capturer Empreinte");
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                            Toast.makeText(AttendanceActivity.this, 
                                         "✅ " + employee.getFirstName() + " " + employee.getLastName() + " - Présence déjà complète", 
                                         Toast.LENGTH_LONG).show();
                        });
                        return; // Ne pas enregistrer
                    }
                    
                    // Déterminer le type
                    String attendanceType = determineAttendanceType(employee, records);
                    
                    // Vérifier si déjà complet (attendanceType == null)
                    if (attendanceType == null) {
                        Log.d(TAG, "❌ Présence déjà complète (attendanceType == null)");
                        runOnUiThread(() -> {
                            txtStatus.setText("⚠️ Présence complète\n\n" +
                                            "Arrivée et départ déjà enregistrés aujourd'hui");
                            btnCapture.setText("Capturer");
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                            Toast.makeText(AttendanceActivity.this, 
                                         "Présence déjà complète", 
                                         Toast.LENGTH_LONG).show();
                        });
                        return; // Ne pas enregistrer
                    }
                    
                    String fingerprintUsed = "fingerprint_capture";
                    
                    // Messages améliorés selon le type
                    String typeLabel = attendanceType.equals("checkin") ? "Arrivée" : "Départ";
                    runOnUiThread(() -> {
                        txtStatus.setText("👤 Employé reconnu: " + employee.getFirstName() + " " + employee.getLastName() + 
                                        "\n📍 Type: " + typeLabel +
                                        "\n\nEnregistrement en cours...");
                    });
                    
                    // Enregistrer la présence
                    recordAttendanceWithType(employee, attendanceType, fingerprintUsed);
                }
                
                @Override
                public void onError(String error) {
                    Log.w(TAG, "Erreur récupération historique, utilisation logique par défaut: " + error);
                    // En cas d'erreur, utiliser la logique par défaut (arrivée)
                    String attendanceType = determineAttendanceType(employee, null);
                    if (attendanceType != null) {
                        String fingerprintUsed = "fingerprint_capture";
                        recordAttendanceWithType(employee, attendanceType, fingerprintUsed);
                    } else {
                        runOnUiThread(() -> {
                            txtStatus.setText("❌ Erreur récupération historique\n\nImpossible de vérifier l'état");
                            btnCapture.setText("Capturer");
                            btnCapture.setEnabled(true);
                            progressBar.setVisibility(View.GONE);
                        });
                    }
                }
            });
    }
    
    private void recordAttendanceWithType(Employee employee, String attendanceType, String fingerprintUsed) {
        attendanceService.recordAttendance(employee.getId(), attendanceType, fingerprintUsed, 
            new AttendanceService.Callback() {
                @Override
                public void onSuccess(String message) {
                    // Messages améliorés avec heure
                    String currentTime = new java.text.SimpleDateFormat("HH:mm:ss", java.util.Locale.getDefault())
                            .format(new java.util.Date());
                    String typeLabel = attendanceType.equals("checkin") ? "Arrivée" : "Départ";
                    
                    runOnUiThread(() -> {
                        String displayMessage = "✅ " + typeLabel + " enregistrée !\n" +
                                              "👤 " + employee.getFirstName() + " " + employee.getLastName() + "\n" +
                                              "📍 " + typeLabel + " à " + currentTime;
                        txtStatus.setText(displayMessage);
                        btnCapture.setText("Capturer");
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        Toast.makeText(AttendanceActivity.this, 
                                     typeLabel + " enregistrée à " + currentTime, 
                                     Toast.LENGTH_LONG).show();
                        Log.d(TAG, "Présence enregistrée avec succès: " + typeLabel + " à " + currentTime);
                    });
                }
                
                @Override
                public void onError(String error) {
                    runOnUiThread(() -> {
                        txtStatus.setText("❌ Erreur enregistrement: " + error);
                        btnCapture.setText("Capturer");
                        btnCapture.setEnabled(true);
                        progressBar.setVisibility(View.GONE);
                        Toast.makeText(AttendanceActivity.this, "Erreur: " + error, Toast.LENGTH_LONG).show();
                        Log.e(TAG, "Erreur enregistrement présence: " + error);
                    });
                }
            });
        
        // Mettre à jour les variables de suivi
        matchedEmployee = employee;
        lastAttendanceType = attendanceType;
        lastAttendanceTime = System.currentTimeMillis();
    }
    
    private String determineAttendanceType(Employee employee, List<AttendanceService.AttendanceRecord> todayRecords) {
        long currentTime = System.currentTimeMillis();
        
        Log.d(TAG, "=== DÉTERMINATION DU TYPE DE PRÉSENCE ===");
        Log.d(TAG, "Employé: " + employee.toString());
        Log.d(TAG, "Historique aujourd'hui: " + (todayRecords != null ? todayRecords.size() : 0) + " enregistrement(s)");
        
        // Protection contre les doubles enregistrements (même employé, moins de 30 secondes)
        if (matchedEmployee != null && 
            matchedEmployee.getId() == employee.getId() && 
            (currentTime - lastAttendanceTime) < 30000) {
            Log.d(TAG, "❌ Présence déjà enregistrée il y a moins de 30 secondes");
            return lastAttendanceType != null ? lastAttendanceType : "checkin";
        }
        
        // NOUVELLE LOGIQUE : Vérifier le nombre de présences
        if (todayRecords == null || todayRecords.isEmpty()) {
            // Aucune présence aujourd'hui → Arrivée
            Log.d(TAG, "✅ Première présence de la journée = Arrivée");
            return "checkin";
        }
        
        // Si 1 présence
        if (todayRecords.size() == 1) {
            AttendanceService.AttendanceRecord firstRecord = todayRecords.get(0);
            Log.d(TAG, "Première présence: " + firstRecord.type + " à " + firstRecord.time);
            
            if ("checkin".equals(firstRecord.type)) {
                // Première = Arrivée → Deuxième = Départ
                Log.d(TAG, "✅ Dernière = Arrivée, nouvelle = Départ");
                return "checkout";
            } else {
                // Cas étrange : départ sans arrivée → Arrivée
                Log.d(TAG, "⚠️ Départ sans arrivée, nouvelle = Arrivée");
                return "checkin";
            }
        }
        
        // Si 2 présences ou plus → Déjà complet (retourner null)
        Log.d(TAG, "❌ Déjà 2 présences ou plus aujourd'hui - Présence complète");
        return null; // Indique que la présence est déjà complète
    }
    
    private String getErrorMessage(int errorCode) {
        switch (errorCode) {
            case ErrorCodes.MORPHO_OK: return "Succès";
            case ErrorCodes.MORPHOERR_TIMEOUT: return "Timeout - Placez votre doigt";
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

