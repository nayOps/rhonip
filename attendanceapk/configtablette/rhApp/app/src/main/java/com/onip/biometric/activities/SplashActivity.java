package com.onip.biometric.activities;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.onip.biometric.ONIPApplication;
import com.onip.biometric.R;
import com.onip.biometric.models.Employee;
import com.onip.biometric.services.EmployeeService;
import com.onip.biometric.services.FingerprintTemplateService;
import com.morpho.android.usb.USBManager;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.ErrorCodes;

import java.util.List;
import java.util.Map;

/**
 * Activité de chargement initiale
 * Charge tous les employés, templates et initialise le capteur
 */
public class SplashActivity extends Activity {
    
    private static final String TAG = "SplashActivity";
    private static final String PREFS_NAME = "ONIP_PREFS";
    private static final String KEY_FIRST_LAUNCH = "first_launch";
    
    private TextView txtStatus;
    private ProgressBar progressBar;
    
    private ONIPApplication app;
    private EmployeeService employeeService;
    private FingerprintTemplateService templateService;
    private MorphoDevice morphoDevice;
    
    private int currentStep = 0;
    private static final int TOTAL_STEPS = 4; // 1. Initialisation, 2. Capteur, 3. Employés, 4. Templates
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_loading);
        
        app = (ONIPApplication) getApplication();
        employeeService = new EmployeeService(this);
        templateService = new FingerprintTemplateService(this);
        
        initializeViews();
        startLoading();
    }
    
    private void initializeViews() {
        txtStatus = findViewById(R.id.txt_loading_status);
        progressBar = findViewById(R.id.progress_loading);
        progressBar.setMax(100);
        progressBar.setProgress(0);
    }
    
    private void startLoading() {
        Log.d(TAG, "=== DÉMARRAGE CHARGEMENT GLOBAL ===");
        updateProgress(0, "Initialisation de l'application...");
        
        // Étape 1: Initialisation (déjà fait)
        new Handler().postDelayed(() -> {
            currentStep = 1;
            updateProgress(25, "Initialisation du capteur d'empreintes...");
            initializeMorphoDevice();
        }, 500);
    }
    
    private void initializeMorphoDevice() {
        new Thread(() -> {
            try {
                Log.d(TAG, "Initialisation du périphérique MorphoSmart...");
                
                USBManager.getInstance().initialize(this, "com.onip.biometric.USB_ACTION", true);
                Log.d(TAG, "USBManager initialisé");
                
                morphoDevice = new MorphoDevice();
                Log.d(TAG, "MorphoDevice créé");
                
                Integer nbUsbDevice = new Integer(0);
                int ret = morphoDevice.initUsbDevicesNameEnum(nbUsbDevice);
                Log.d(TAG, "Énumération USB: " + ret + ", nbDevices: " + nbUsbDevice);
                
                if (ret == com.morpho.morphosmart.sdk.ErrorCodes.MORPHO_OK && nbUsbDevice == 1) {
                    String sensorName = morphoDevice.getUsbDeviceName(0);
                    Log.d(TAG, "Nom du capteur: " + sensorName);
                    
                    final int openResult = morphoDevice.openUsbDevice(sensorName, 0);
                    Log.d(TAG, "Ouverture périphérique: " + openResult);
                    
                    if (openResult == com.morpho.morphosmart.sdk.ErrorCodes.MORPHO_OK) {
                        app.setGlobalMorphoDevice(morphoDevice);
                        app.setDeviceInitialized(true);
                        Log.d(TAG, "✅ Capteur MorphoSmart initialisé");
                        
                        runOnUiThread(() -> {
                            currentStep = 2;
                            updateProgress(50, "Chargement des employés...");
                            loadEmployees();
                        });
                    } else {
                        Log.e(TAG, "❌ Erreur ouverture capteur: " + openResult);
                        runOnUiThread(() -> {
                            updateProgress(50, "Capteur non disponible - Chargement des employés...");
                            loadEmployees();
                        });
                    }
                } else {
                    Log.w(TAG, "⚠️ Aucun capteur MorphoSmart détecté (nbDevices: " + nbUsbDevice + ")");
                    runOnUiThread(() -> {
                        updateProgress(50, "Capteur non détecté - Chargement des employés...");
                        loadEmployees();
                    });
                }
            } catch (Exception e) {
                Log.e(TAG, "❌ Exception initialisation capteur: " + e.getMessage(), e);
                runOnUiThread(() -> {
                    updateProgress(50, "Erreur capteur - Chargement des employés...");
                    loadEmployees();
                });
            }
        }).start();
    }
    
    private void loadEmployees() {
        employeeService.loadEmployees(new EmployeeService.Callback() {
            @Override
            public void onSuccess(List<Employee> employees) {
                app.setGlobalEmployees(employees);
                Log.d(TAG, "✅ " + employees.size() + " employé(s) chargé(s)");
                
                currentStep = 3;
                updateProgress(75, "Chargement des templates d'empreintes...");
                loadTemplates();
            }
            
            @Override
            public void onError(String error) {
                Log.e(TAG, "❌ Erreur chargement employés: " + error);
                runOnUiThread(() -> {
                    updateProgress(75, "Erreur chargement employés - Tentative chargement templates...");
                    // Continuer quand même pour charger les templates
                    loadTemplates();
                });
            }
        });
    }
    
    private void loadTemplates() {
        templateService.loadAllTemplatesForMatching(new FingerprintTemplateService.AllTemplatesCallback() {
            @Override
            public void onSuccess(Map<Integer, Map<String, byte[]>> templates) {
                app.setGlobalTemplates(templates);
                
                int totalTemplates = 0;
                for (Map<String, byte[]> empTemplates : templates.values()) {
                    totalTemplates += empTemplates.size();
                }
                Log.d(TAG, "✅ " + totalTemplates + " template(s) chargé(s)");
                
                // Tout est chargé
                app.setDataLoaded(true);
                currentStep = 4;
                updateProgress(100, "Chargement terminé !");
                
                // Naviguer vers le menu principal après un court délai
                new Handler().postDelayed(() -> {
                    navigateToMainMenu();
                }, 1000);
            }
            
            @Override
            public void onError(String error) {
                Log.e(TAG, "❌ Erreur chargement templates: " + error);
                runOnUiThread(() -> {
                    updateProgress(100, "Chargement terminé (avec erreurs)");
                    // Naviguer quand même
                    new Handler().postDelayed(() -> {
                        navigateToMainMenu();
                    }, 1000);
                });
            }
        });
    }
    
    private void updateProgress(int progress, String message) {
        runOnUiThread(() -> {
            progressBar.setProgress(progress);
            txtStatus.setText(message);
            Log.d(TAG, "📊 " + progress + "% - " + message);
        });
    }
    
    private void navigateToMainMenu() {
        Intent intent = new Intent(this, MainMenuActivity.class);
        startActivity(intent);
        finish();
    }
    
    @Override
    protected void onDestroy() {
        super.onDestroy();
        // Ne pas fermer le device ici, il est utilisé globalement
    }
}

