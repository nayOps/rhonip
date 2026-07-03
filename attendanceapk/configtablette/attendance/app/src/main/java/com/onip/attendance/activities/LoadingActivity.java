package com.onip.attendance.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;
import com.onip.attendance.AttendanceApplication;
import com.onip.attendance.R;
import com.onip.attendance.models.Employee;
import com.onip.attendance.services.AttendanceService;
import com.onip.attendance.services.DataManager;
import com.onip.attendance.services.DeviceManager;
import com.onip.attendance.storage.LocalTemplateStore;
import com.onip.attendance.utils.ConfigManager;
import com.onip.attendance.utils.SettingsLauncher;
import com.morpho.morphosmart.sdk.MorphoDevice;
import java.util.List;
import java.util.Map;

/**
 * Écran de démarrage : chargement rapide ou synchronisation serveur.
 */
public class LoadingActivity extends Activity {

    public static final String EXTRA_FORCE_SYNC = "force_sync";

    private static final String TAG = "LoadingActivity";

    private TextView txtStatus;
    private ProgressBar progressBar;

    private AttendanceApplication app;
    private DeviceManager deviceManager;
    private DataManager dataManager;
    private ConfigManager configManager;
    private LocalTemplateStore templateStore;

    private boolean forceSync;
    private boolean navigationDone;

    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_loading);

        app = (AttendanceApplication) getApplication();
        deviceManager = new DeviceManager(this);
        dataManager = new DataManager(this);
        configManager = new ConfigManager(this);
        templateStore = new LocalTemplateStore(this);
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

        boolean cacheUsable = templateStore.hasData() && templateStore.countTemplates() > 0;
        boolean needsServerSync = forceSync || !cacheUsable;

        if (needsServerSync) {
            syncFromServer();
        } else {
            loadFromLocalCache();
        }
    }

    private void loadFromLocalCache() {
        dataManager.loadFromCache(new DataManager.AllDataCallback() {
            @Override
            public void onSuccess(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates, boolean fromCache) {
                onDataReady(employees, templates);
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
        dataManager.loadAllData(forceSync, new DataManager.AllDataCallback() {
            @Override
            public void onSuccess(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates, boolean fromCache) {
                configManager.setInitialSyncDone(true);
                onDataReady(employees, templates);
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
                    if (templateStore.hasData()) {
                        loadFromLocalCache();
                        return;
                    }
                    updateProgress(100, getString(R.string.loading_sync_failed));
                });
            }
        });
    }

    private void onDataReady(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates) {
        if (employees == null || employees.isEmpty() || templates == null || templates.isEmpty()) {
            Log.e(TAG, "Données incomplètes après chargement");
            runOnUiThread(() -> updateProgress(100, getString(R.string.loading_sync_failed)));
            return;
        }

        Log.d(TAG, "Données prêtes: " + employees.size() + " agent(s), "
                + templates.size() + " avec empreinte");

        app.setGlobalEmployees(employees);
        app.setGlobalTemplates(templates);
        app.setDataLoaded(true);

        AttendanceService attendanceService = new AttendanceService(this);
        attendanceService.syncPendingPunches();

        runOnUiThread(() -> {
            updateProgress(100, getString(R.string.loading_ready_short));
            mainHandler.postDelayed(this::navigateToAttendance, 500);
        });
    }

    private void navigateToAttendance() {
        if (navigationDone || isFinishing()) {
            return;
        }
        navigationDone = true;
        Intent intent = new Intent(this, AttendanceActivity.class);
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
