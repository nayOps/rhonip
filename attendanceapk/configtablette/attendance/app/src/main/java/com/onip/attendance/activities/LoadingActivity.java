package com.onip.attendance.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;
import com.onip.attendance.AttendanceApplication;
import com.onip.attendance.R;
import com.onip.attendance.models.Employee;
import com.onip.attendance.services.AttendanceService;
import com.onip.attendance.services.DataManager;
import com.onip.attendance.services.DeviceManager;
import com.morpho.morphosmart.sdk.MorphoDevice;
import java.util.List;
import java.util.Map;

/**
 * Activité de chargement initiale
 * Initialise le MorphoDevice et charge toutes les données
 * Version améliorée avec retry automatique et gestion d'erreurs
 */
public class LoadingActivity extends Activity {
    
    private static final String TAG = "LoadingActivity";
    
    private TextView txtStatus;
    private ProgressBar progressBar;
    
    // Vue pour configuration IP en cas d'erreur
    private android.widget.LinearLayout configView;
    private android.widget.EditText editBackendIp;
    private android.widget.EditText editBackendPort;
    private android.widget.Button btnRetry;
    
    private AttendanceApplication app;
    private DeviceManager deviceManager;
    private DataManager dataManager;
    private com.onip.attendance.utils.ConfigManager configManager;
    
    private int currentStep = 0;
    private static final int TOTAL_STEPS = 3; // 1. Device, 2. Employés, 3. Templates
    private boolean hasConnectionError = false;
    private boolean navigationDone = false;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_loading);
        
        app = (AttendanceApplication) getApplication();
        deviceManager = new DeviceManager(this);
        dataManager = new DataManager(this);
        configManager = new com.onip.attendance.utils.ConfigManager(this);
        
        initializeViews();
        startLoading();
    }
    
    private void initializeViews() {
        txtStatus = findViewById(R.id.txt_loading_status);
        progressBar = findViewById(R.id.progress_loading);
        progressBar.setMax(100);
        progressBar.setProgress(0);
        
        // Vues pour configuration IP (initialement cachées)
        configView = findViewById(R.id.layout_config_ip);
        if (configView == null) {
            // Créer dynamiquement si pas dans le layout
            createConfigView();
        } else {
            editBackendIp = findViewById(R.id.edit_backend_ip_loading);
            editBackendPort = findViewById(R.id.edit_backend_port_loading);
            btnRetry = findViewById(R.id.btn_retry_loading);
            configView.setVisibility(android.view.View.GONE);
            if (editBackendIp != null) {
                editBackendIp.setText(configManager.getBackendIp());
            }
            if (editBackendPort != null) {
                editBackendPort.setText(configManager.getBackendPort());
            }
            wireRetryButton();
        }

        android.widget.Button btnOpenConfig = findViewById(R.id.btn_open_config_loading);
        if (btnOpenConfig != null) {
            btnOpenConfig.setOnClickListener(v -> showConfigPanel(
                    "Configurez l'adresse du serveur RH (port 8100 par défaut)."));
        }
    }

    private void showConfigPanel(String message) {
        progressBar.setVisibility(android.view.View.GONE);
        if (configView != null) {
            configView.setVisibility(android.view.View.VISIBLE);
            if (editBackendIp != null) {
                editBackendIp.setText(configManager.getBackendIp());
            }
            if (editBackendPort != null) {
                editBackendPort.setText(configManager.getBackendPort());
            }
            txtStatus.setText(message);
            wireRetryButton();
        }
    }

    private void wireRetryButton() {
        if (btnRetry == null) {
            return;
        }
        btnRetry.setOnClickListener(v -> {
            String ip = editBackendIp != null ? editBackendIp.getText().toString().trim() : "";
            String port = editBackendPort != null ? editBackendPort.getText().toString().trim() : "";

            if (ip.isEmpty() || port.isEmpty()) {
                android.widget.Toast.makeText(this, "Veuillez remplir tous les champs",
                        android.widget.Toast.LENGTH_SHORT).show();
                return;
            }

            configManager.setBackendConfig(ip, port);
            Log.d(TAG, "Configuration backend: " + ip + ":" + port);
            dataManager = new DataManager(this);

            configView.setVisibility(android.view.View.GONE);
            progressBar.setVisibility(android.view.View.VISIBLE);
            hasConnectionError = false;
            currentStep = 2;
            updateProgress(40, "Chargement des données...");
            loadAllData();
        });
    }
    
    private void createConfigView() {
        // Créer la vue de configuration dynamiquement si elle n'existe pas
        android.widget.LinearLayout mainLayout = findViewById(R.id.layout_loading_main);
        if (mainLayout != null) {
            configView = new android.widget.LinearLayout(this);
            configView.setOrientation(android.widget.LinearLayout.VERTICAL);
            configView.setPadding(32, 32, 32, 32);
            configView.setBackgroundResource(R.drawable.glassmorphic_card);
            configView.setVisibility(android.view.View.GONE);
            
            android.widget.LinearLayout.LayoutParams layoutParams = new android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT);
            layoutParams.setMargins(0, 32, 0, 0);
            configView.setLayoutParams(layoutParams);
            
            android.widget.TextView titleConfig = new android.widget.TextView(this);
            titleConfig.setText("Configuration Backend");
            titleConfig.setTextSize(18);
            titleConfig.setTextColor(getResources().getColor(R.color.text_primary));
            titleConfig.setPadding(0, 0, 0, 16);
            
            editBackendIp = new android.widget.EditText(this);
            editBackendIp.setHint("IP du backend (ex: 192.168.1.74)");
            editBackendIp.setInputType(android.text.InputType.TYPE_CLASS_TEXT);
            editBackendIp.setPadding(16, 16, 16, 16);
            editBackendIp.setBackgroundResource(R.drawable.input_flat);
            editBackendIp.setLayoutParams(new android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT));
            ((android.widget.LinearLayout.LayoutParams) editBackendIp.getLayoutParams()).setMargins(0, 0, 0, 16);
            
            editBackendPort = new android.widget.EditText(this);
            editBackendPort.setHint("Port (ex: 8100)");
            editBackendPort.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
            editBackendPort.setPadding(16, 16, 16, 16);
            editBackendPort.setBackgroundResource(R.drawable.input_flat);
            editBackendPort.setLayoutParams(new android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT));
            ((android.widget.LinearLayout.LayoutParams) editBackendPort.getLayoutParams()).setMargins(0, 0, 0, 16);
            
            btnRetry = new android.widget.Button(this);
            btnRetry.setText("Relancer le chargement");
            btnRetry.setBackgroundResource(R.drawable.button_primary_flat);
            btnRetry.setTextColor(getResources().getColor(R.color.white));
            btnRetry.setLayoutParams(new android.widget.LinearLayout.LayoutParams(
                android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
                android.widget.LinearLayout.LayoutParams.WRAP_CONTENT));
            
            configView.addView(titleConfig);
            configView.addView(editBackendIp);
            configView.addView(editBackendPort);
            configView.addView(btnRetry);

            if (editBackendIp != null) {
                editBackendIp.setText(configManager.getBackendIp());
            }
            if (editBackendPort != null) {
                editBackendPort.setText(configManager.getBackendPort());
            }

            mainLayout.addView(configView);
        }
    }
    
    private void startLoading() {
        Log.d(TAG, "=== DÉMARRAGE CHARGEMENT GLOBAL ===");
        updateProgress(0, "Initialisation de l'application...");
        
        // Étape 1: Initialisation du capteur
        new Handler().postDelayed(() -> {
            currentStep = 1;
            updateProgress(10, "Initialisation du capteur d'empreintes...");
            initializeDevice();
        }, 500);
    }
    
    private void initializeDevice() {
        deviceManager.initializeDevice(new DeviceManager.DeviceCallback() {
            @Override
            public void onSuccess(MorphoDevice device) {
                Log.d(TAG, "✅ Capteur initialisé avec succès");
                app.setGlobalMorphoDevice(device);
                app.setDeviceInitialized(true);
                
                runOnUiThread(() -> {
                    currentStep = 2;
                    updateProgress(40, "Chargement des données...");
                    loadAllData();
                });
            }
            
            @Override
            public void onError(String error) {
                Log.w(TAG, "⚠️ Capteur non disponible: " + error);
                app.setDeviceInitialized(false);
                
                runOnUiThread(() -> {
                    updateProgress(40, "Capteur non disponible - Chargement des données...");
                    loadAllData();
                });
            }
        });
    }
    
    private void loadAllData() {
        dataManager.loadAllData(new DataManager.AllDataCallback() {
            @Override
            public void onSuccess(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates, boolean fromCache) {
                Log.d(TAG, "✅ Données chargées: " + employees.size() + " employés, "
                        + templates.size() + " avec templates"
                        + (fromCache ? " (cache local)" : " (serveur)"));

                app.setGlobalEmployees(employees);
                app.setGlobalTemplates(templates);
                app.setDataLoaded(true);

                AttendanceService attendanceService = new AttendanceService(LoadingActivity.this);
                attendanceService.syncPendingPunches();

                runOnUiThread(() -> {
                    String cacheHint = fromCache ? "\n(cache local)" : "";
                    updateProgress(100, "✅ Application prête !" + cacheHint);
                    new Handler().postDelayed(() -> navigateToAttendance(), 800);
                });
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "❌ Erreur chargement données: " + error);
                
                runOnUiThread(() -> {
                    // Vérifier si c'est une erreur de connexion (IP/host)
                    boolean isConnectionError = error.contains("Connexion refusée") || 
                                               error.contains("Host inconnu") || 
                                               error.contains("Timeout") ||
                                               error.contains("UnknownHostException") ||
                                               error.contains("ConnectException") ||
                                               error.contains("SocketTimeoutException") ||
                                               error.toLowerCase().contains("connection") ||
                                               error.toLowerCase().contains("refused");
                    
                    if (isConnectionError && !hasConnectionError) {
                        hasConnectionError = true;
                        showConfigDialog(error);
                        return;
                    }
                    
                    // Autre type d'erreur
                    {
                        // Autre type d'erreur
                        String backendUrl = configManager.getBackendBaseUrl();
                        String errorMessage = "⚠️ Erreur de chargement\n\n" + 
                                            "Erreur: " + error + "\n\n" +
                                            "Backend: " + backendUrl;
                        
                        updateProgress(90, errorMessage);
                        
                        // Continuer quand même si on a des données en cache
                        new Handler().postDelayed(() -> {
                            if (app.getGlobalEmployees().isEmpty()) {
                                txtStatus.setText("❌ Impossible de charger les données\n\n" +
                                                "Backend: " + backendUrl + "\n" +
                                                "Veuillez vérifier la connexion et redémarrer");
                            } else {
                                // On a des données en cache, continuer
                                Log.d(TAG, "✅ Utilisation des données en cache");
                                navigateToAttendance();
                            }
                        }, 3000);
                    }
                });
            }
        });
    }
    
    private void navigateToAttendance() {
        if (navigationDone) {
            return;
        }
        navigationDone = true;
        try {
            Intent intent = new Intent(LoadingActivity.this, AttendanceActivity.class);
            startActivity(intent);
            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
            finish();
        } catch (Exception e) {
            navigationDone = false;
            Log.e(TAG, "Impossible d'ouvrir l'écran pointage", e);
            updateProgress(100, "Erreur ouverture écran pointage:\n" + e.getMessage());
        }
    }
    
    private void updateProgress(int progress, String message) {
        runOnUiThread(() -> {
            progressBar.setProgress(progress);
            txtStatus.setText(message);
            Log.d(TAG, "Progress: " + progress + "% - " + message);
        });
    }
    
    /**
     * Affiche le formulaire de configuration IP en cas d'erreur de connexion
     */
    private void showConfigDialog(String error) {
        runOnUiThread(() -> showConfigPanel(
                "❌ Erreur de connexion\n\n" + error + "\n\nVeuillez vérifier l'IP et le port du backend"));
    }
}

