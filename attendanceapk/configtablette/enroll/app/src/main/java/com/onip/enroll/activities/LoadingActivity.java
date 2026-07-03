package com.onip.enroll.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;
import com.onip.enroll.EnrollApplication;
import com.onip.enroll.R;
import com.onip.enroll.models.Employee;
import com.onip.enroll.services.DeviceManager;
import com.onip.enroll.services.EmployeeDataService;
import com.onip.enroll.storage.LocalEmployeeStore;
import com.onip.enroll.utils.ConfigManager;
import com.onip.enroll.utils.SettingsLauncher;
import com.morpho.morphosmart.sdk.MorphoDevice;
import java.util.List;

/** Écran de démarrage : chargement rapide ou synchronisation serveur. */
public class LoadingActivity extends Activity {

    public static final String EXTRA_FORCE_SYNC = "force_sync";

    private static final String TAG = "EnrollLoading";

    private TextView txtStatus;
    private ProgressBar progressBar;

    private EnrollApplication app;
    private DeviceManager deviceManager;
    private EmployeeDataService employeeDataService;
    private ConfigManager configManager;
    private LocalEmployeeStore employeeStore;

    private boolean forceSync;
    private boolean navigationDone;

    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_loading);

        app = (EnrollApplication) getApplication();
        deviceManager = new DeviceManager(this);
        employeeDataService = new EmployeeDataService(this);
        configManager = new ConfigManager(this);
        employeeStore = employeeDataService.getEmployeeStore();
        forceSync = getIntent().getBooleanExtra(EXTRA_FORCE_SYNC, false);

        txtStatus = findViewById(R.id.txt_loading_status);
        progressBar = findViewById(R.id.progress_loading);
        progressBar.setMax(100);
        progressBar.setProgress(0);

        SettingsLauncher.wire(this, R.id.btn_settings_loading);
        startLoading();
    }

    private void startLoading() {
        updateProgress(5, getString(R.string.loading_simple));
        mainHandler.postDelayed(this::initializeDevice, 300);
    }

    private void initializeDevice() {
        deviceManager.initializeDevice(new DeviceManager.DeviceCallback() {
            @Override
            public void onSuccess(MorphoDevice device) {
                app.setGlobalMorphoDevice(device);
                app.setDeviceInitialized(true);
                runOnUiThread(() -> loadData());
            }

            @Override
            public void onError(String error) {
                Log.w(TAG, "Capteur indisponible: " + error);
                app.setDeviceInitialized(false);
                runOnUiThread(() -> loadData());
            }
        });
    }

    private void loadData() {
        updateProgress(35, getString(R.string.loading_simple));

        boolean cacheUsable = employeeStore.hasData() && employeeStore.countEmployees() > 0;
        boolean needsServerSync = forceSync || !cacheUsable;

        if (needsServerSync) {
            syncFromServer();
        } else {
            loadFromLocalCache();
        }
    }

    private void loadFromLocalCache() {
        employeeDataService.loadFromCache(new EmployeeDataService.EmployeesCallback() {
            @Override
            public void onSuccess(List<Employee> employees, boolean fromCache) {
                onDataReady(employees);
            }

            @Override
            public void onError(String error) {
                Log.w(TAG, "Cache locale indisponible: " + error);
                syncFromServer();
            }
        });
    }

    private void syncFromServer() {
        updateProgress(50, getString(R.string.loading_sync));
        employeeDataService.loadEmployees(forceSync, new EmployeeDataService.EmployeesCallback() {
            @Override
            public void onSuccess(List<Employee> employees, boolean fromCache) {
                configManager.setInitialSyncDone(true);
                onDataReady(employees);
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "Erreur synchronisation: " + error);
                runOnUiThread(() -> {
                    if (forceSync) {
                        updateProgress(100, getString(R.string.loading_sync_failed));
                        android.widget.Toast.makeText(
                                LoadingActivity.this,
                                R.string.reload_failed,
                                android.widget.Toast.LENGTH_LONG
                        ).show();
                        return;
                    }
                    if (employeeStore.hasData()) {
                        loadFromLocalCache();
                        return;
                    }
                    updateProgress(100, getString(R.string.loading_sync_failed));
                });
            }
        });
    }

    private void onDataReady(List<Employee> employees) {
        if (employees == null || employees.isEmpty()) {
            Log.e(TAG, "Liste agents vide après chargement");
            runOnUiThread(() -> updateProgress(100, getString(R.string.loading_sync_failed)));
            return;
        }

        Log.d(TAG, "Agents prêts: " + employees.size());
        app.setGlobalEmployees(employees);
        app.setDataLoaded(true);

        runOnUiThread(() -> {
            updateProgress(100, getString(R.string.loading_ready_short));
            mainHandler.postDelayed(this::navigateToEmployeeList, 500);
        });
    }

    private void navigateToEmployeeList() {
        if (navigationDone || isFinishing()) {
            return;
        }
        navigationDone = true;
        Intent intent = new Intent(this, EmployeeListActivity.class);
        startActivity(intent);
        overridePendingTransition(android.R.anim.fade_in, android.R.anim.fade_out);
        finish();
    }

    private void updateProgress(int progress, String message) {
        runOnUiThread(() -> {
            progressBar.setProgress(progress);
            txtStatus.setText(message);
        });
    }
}
