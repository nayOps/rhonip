package com.onip.enroll.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import com.onip.enroll.EnrollApplication;
import com.onip.enroll.R;
import com.onip.enroll.models.Employee;
import com.onip.enroll.services.DeviceManager;
import com.onip.enroll.services.EmployeeDataService;
import com.onip.enroll.utils.ConfigManager;
import com.morpho.morphosmart.sdk.MorphoDevice;
import java.util.List;

/** Démarrage enrôlement : capteur Morpho + liste agents RH. */
public class LoadingActivity extends Activity {

    private static final String TAG = "EnrollLoading";

    private TextView txtStatus;
    private ProgressBar progressBar;
    private LinearLayout configView;
    private EditText editBackendIp;
    private EditText editBackendPort;
    private Button btnRetry;

    private EnrollApplication app;
    private DeviceManager deviceManager;
    private EmployeeDataService employeeDataService;
    private ConfigManager configManager;
    private boolean hasConnectionError = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_loading);

        app = (EnrollApplication) getApplication();
        deviceManager = new DeviceManager(this);
        employeeDataService = new EmployeeDataService(this);
        configManager = new ConfigManager(this);

        txtStatus = findViewById(R.id.txt_loading_status);
        progressBar = findViewById(R.id.progress_loading);
        progressBar.setMax(100);
        configView = findViewById(R.id.layout_config_ip);
        editBackendIp = findViewById(R.id.edit_backend_ip_loading);
        editBackendPort = findViewById(R.id.edit_backend_port_loading);
        btnRetry = findViewById(R.id.btn_retry_loading);
        if (configView != null) {
            configView.setVisibility(android.view.View.GONE);
        }
        if (editBackendIp != null) {
            editBackendIp.setText(configManager.getBackendIp());
        }
        if (editBackendPort != null) {
            editBackendPort.setText(configManager.getBackendPort());
        }
        wireRetryButton();

        new Handler().postDelayed(this::initializeDevice, 400);
    }

    private void wireRetryButton() {
        if (btnRetry == null) {
            return;
        }
        btnRetry.setOnClickListener(v -> {
            String ip = editBackendIp != null ? editBackendIp.getText().toString().trim() : "";
            String port = editBackendPort != null ? editBackendPort.getText().toString().trim() : "";
            if (ip.isEmpty() || port.isEmpty()) {
                Toast.makeText(this, "IP et port requis", Toast.LENGTH_SHORT).show();
                return;
            }
            configManager.setBackendConfig(ip, port);
            if (configView != null) {
                configView.setVisibility(android.view.View.GONE);
            }
            progressBar.setVisibility(android.view.View.VISIBLE);
            hasConnectionError = false;
            loadEmployees();
        });
    }

    private void initializeDevice() {
        updateProgress(10, "Initialisation du capteur...");
        deviceManager.initializeDevice(new DeviceManager.DeviceCallback() {
            @Override
            public void onSuccess(MorphoDevice device) {
                app.setGlobalMorphoDevice(device);
                app.setDeviceInitialized(true);
                runOnUiThread(() -> {
                    updateProgress(40, "Chargement des agents...");
                    loadEmployees();
                });
            }

            @Override
            public void onError(String error) {
                Log.w(TAG, "Capteur indisponible: " + error);
                app.setDeviceInitialized(false);
                runOnUiThread(() -> {
                    updateProgress(40, "Capteur indisponible — chargement agents...");
                    loadEmployees();
                });
            }
        });
    }

    private void loadEmployees() {
        employeeDataService.loadEmployees(new EmployeeDataService.EmployeesCallback() {
            @Override
            public void onSuccess(List<Employee> employees) {
                app.setGlobalEmployees(employees);
                app.setDataLoaded(true);
                runOnUiThread(() -> {
                    updateProgress(100, "Prêt — " + employees.size() + " agent(s)");
                    new Handler().postDelayed(() -> {
                        try {
                            startActivity(new Intent(LoadingActivity.this, EmployeeListActivity.class));
                            overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
                            new Handler().postDelayed(LoadingActivity.this::finish, 400);
                        } catch (Exception e) {
                            Log.e(TAG, "Impossible d'ouvrir la liste agents", e);
                            updateProgress(100, "Erreur ouverture liste:\n" + e.getMessage());
                        }
                    }, 600);
                });
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, error);
                runOnUiThread(() -> {
                    if (!hasConnectionError) {
                        hasConnectionError = true;
                        if (configView != null) {
                            configView.setVisibility(android.view.View.VISIBLE);
                            progressBar.setVisibility(android.view.View.GONE);
                        }
                        txtStatus.setText("Erreur réseau: " + error);
                    } else if (!app.getGlobalEmployees().isEmpty()) {
                        startActivity(new Intent(LoadingActivity.this, EmployeeListActivity.class));
                        finish();
                    }
                });
            }
        });
    }

    private void updateProgress(int progress, String message) {
        progressBar.setProgress(progress);
        txtStatus.setText(message);
    }
}
