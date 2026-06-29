package com.onip.enroll.activities;

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
import com.onip.enroll.EnrollApplication;
import com.onip.enroll.R;
import com.onip.enroll.fingerprint.FingerprintProcessObserver;
import com.onip.enroll.fingerprint.MorphoCaptureHelper;
import com.onip.enroll.services.DeviceManager;
import com.onip.enroll.services.EnrollService;
import com.onip.enroll.utils.FingerCatalog;
import com.onip.enroll.widgets.HandDiagramView;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.Template;
import com.morpho.morphosmart.sdk.TemplateList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;

public class FingerprintEnrollActivity extends Activity {

    private static final String TAG = "FingerprintEnroll";

    private TextView txtEmployee;
    private TextView txtProgress;
    private TextView txtCurrentFinger;
    private TextView txtStatus;
    private ProgressBar progressEnroll;
    private ProgressBar progressCaptureQuality;
    private ImageView imgFingerprint;
    private HandDiagramView handDiagram;
    private Button btnCapture;
    private Button btnReinit;
    private Button btnBack;

    private EnrollService enrollService;
    private DeviceManager deviceManager;
    private MorphoDevice morphoDevice;
    private boolean deviceReady = false;
    private final AtomicBoolean deviceInitializing = new AtomicBoolean(false);

    private int employeeId;
    private String employeeName;
    private String employeeNin;

    private int currentFingerIndex = 0;
    private volatile boolean capturing = false;
    private final Map<String, Boolean> savedFingers = new HashMap<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fingerprint_enroll);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

        employeeId = getIntent().getIntExtra("employee_id", 0);
        employeeName = getIntent().getStringExtra("employee_name");
        employeeNin = getIntent().getStringExtra("employee_nin");

        bindViews();
        enrollService = new EnrollService(this);
        deviceManager = new DeviceManager(this);

        progressEnroll.setMax(FingerCatalog.ALL_TEN.length);
        txtEmployee.setText(employeeName + "\nMatricule : " + employeeNin);

        btnCapture.setOnClickListener(v -> onCaptureClicked());
        btnReinit.setOnClickListener(v -> initializeSensor(true));
        btnBack.setOnClickListener(v -> finish());

        refreshUi();
        initializeSensor(false);
        loadEnrollmentStatus();
    }

    private void bindViews() {
        txtEmployee = findViewById(R.id.txt_enroll_employee);
        txtProgress = findViewById(R.id.txt_enroll_progress);
        txtCurrentFinger = findViewById(R.id.txt_current_finger);
        txtStatus = findViewById(R.id.txt_enroll_status);
        progressEnroll = findViewById(R.id.progress_enroll);
        progressCaptureQuality = findViewById(R.id.progress_capture_quality);
        imgFingerprint = findViewById(R.id.img_enroll_fingerprint);
        handDiagram = findViewById(R.id.hand_diagram);
        btnCapture = findViewById(R.id.btn_capture_finger);
        btnReinit = findViewById(R.id.btn_reinit_sensor);
        btnBack = findViewById(R.id.btn_back_enroll);
    }

    private void initializeSensor(boolean forceReinit) {
        if (!deviceInitializing.compareAndSet(false, true)) {
            Toast.makeText(this, "Initialisation déjà en cours...", Toast.LENGTH_SHORT).show();
            return;
        }

        EnrollApplication app = (EnrollApplication) getApplication();

        if (capturing) {
            MorphoCaptureHelper.cancelAcquisition(morphoDevice);
            capturing = false;
        }

        if (forceReinit) {
            MorphoCaptureHelper.closeDevice(app.getGlobalMorphoDevice());
            deviceManager.shutdownDevice();
            app.setGlobalMorphoDevice(null);
            app.setDeviceInitialized(false);
            morphoDevice = null;
            deviceReady = false;
        } else if (app.getGlobalMorphoDevice() != null
                && MorphoCaptureHelper.isDeviceResponsive(app.getGlobalMorphoDevice())) {
            morphoDevice = app.getGlobalMorphoDevice();
            deviceReady = true;
            deviceInitializing.set(false);
            txtStatus.setText("Capteur prêt. Placez le doigt indiqué puis appuyez sur Capturer.");
            refreshUi();
            return;
        }

        deviceReady = false;
        morphoDevice = null;
        btnCapture.setEnabled(false);
        txtStatus.setText("Initialisation du capteur Morpho...");

        deviceManager.initializeDevice(new DeviceManager.DeviceCallback() {
            @Override
            public void onSuccess(MorphoDevice device) {
                runOnUiThread(() -> {
                    deviceInitializing.set(false);
                    morphoDevice = device;
                    deviceReady = true;
                    app.setGlobalMorphoDevice(device);
                    app.setDeviceInitialized(true);
                    txtStatus.setText("Capteur prêt.\nPlacez le doigt sur le capteur puis Capturer.");
                    Toast.makeText(FingerprintEnrollActivity.this, "Capteur initialisé", Toast.LENGTH_SHORT).show();
                    refreshUi();
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() -> {
                    deviceInitializing.set(false);
                    deviceReady = false;
                    txtStatus.setText("Capteur indisponible.\n" + error + "\n\nRéessayez « Réinitialiser le capteur ».");
                    Toast.makeText(FingerprintEnrollActivity.this, error, Toast.LENGTH_LONG).show();
                    refreshUi();
                });
            }
        });
    }

    private void loadEnrollmentStatus() {
        enrollService.fetchEnrollmentStatus(employeeId, new EnrollService.StatusCallback() {
            @Override
            public void onSuccess(org.json.JSONObject response) {
                runOnUiThread(() -> {
                    try {
                        org.json.JSONArray fingers = response.optJSONArray("fingers");
                        if (fingers != null) {
                            for (int i = 0; i < fingers.length(); i++) {
                                org.json.JSONObject item = fingers.getJSONObject(i);
                                if (item.optBoolean("morphoReady", false)
                                        && "CAPTURED".equalsIgnoreCase(item.optString("status"))) {
                                    savedFingers.put(item.optString("fingerPosition"), true);
                                }
                            }
                        }
                    } catch (Exception e) {
                        Log.w(TAG, "Parse statut: " + e.getMessage());
                    }
                    skipCompletedFingers();
                    refreshUi();
                });
            }

            @Override
            public void onError(String error) {
                Log.w(TAG, "Statut enrôlement: " + error);
            }
        });
    }

    private void onCaptureClicked() {
        if (deviceInitializing.get()) {
            Toast.makeText(this, "Patientez, le capteur s'initialise...", Toast.LENGTH_SHORT).show();
            return;
        }
        if (capturing) {
            cancelCapture();
            return;
        }
        if (!deviceReady || morphoDevice == null) {
            Toast.makeText(this, "Capteur non prêt — réinitialisation...", Toast.LENGTH_LONG).show();
            initializeSensor(true);
            return;
        }
        if (!MorphoCaptureHelper.isDeviceResponsive(morphoDevice)) {
            Toast.makeText(this, "Capteur non réactif — réinitialisation...", Toast.LENGTH_LONG).show();
            initializeSensor(true);
            return;
        }
        if (currentFingerIndex >= FingerCatalog.ALL_TEN.length) {
            Toast.makeText(this, "Enrôlement déjà terminé", Toast.LENGTH_SHORT).show();
            return;
        }
        captureCurrentFinger();
    }

    private void cancelCapture() {
        new Thread(() -> {
            MorphoCaptureHelper.cancelAcquisition(morphoDevice);
            runOnUiThread(() -> {
                capturing = false;
                progressCaptureQuality.setProgress(0);
                txtStatus.setText("Capture annulée. Replacez le doigt et réessayez.");
                refreshUi();
            });
        }).start();
    }

    private Set<String> completedCodes() {
        Set<String> codes = new HashSet<>();
        for (FingerCatalog.FingerDef finger : FingerCatalog.ALL_TEN) {
            if (Boolean.TRUE.equals(savedFingers.get(finger.registerCode))) {
                codes.add(finger.registerCode);
            }
        }
        return codes;
    }

    private void skipCompletedFingers() {
        while (currentFingerIndex < FingerCatalog.ALL_TEN.length) {
            FingerCatalog.FingerDef finger = FingerCatalog.ALL_TEN[currentFingerIndex];
            if (!Boolean.TRUE.equals(savedFingers.get(finger.registerCode))) {
                break;
            }
            currentFingerIndex++;
        }
    }

    private void refreshUi() {
        int saved = 0;
        for (FingerCatalog.FingerDef finger : FingerCatalog.ALL_TEN) {
            if (Boolean.TRUE.equals(savedFingers.get(finger.registerCode))) {
                saved++;
            }
        }
        progressEnroll.setProgress(saved);
        txtProgress.setText("Empreintes Morpho : " + saved + " / " + FingerCatalog.ALL_TEN.length);
        handDiagram.updateState(currentFingerIndex, completedCodes());

        if (currentFingerIndex >= FingerCatalog.ALL_TEN.length) {
            txtCurrentFinger.setText("Enrôlement terminé");
            btnCapture.setText("Terminé");
            btnCapture.setEnabled(false);
            txtStatus.setText("Les 10 empreintes Morpho sont enregistrées.\nPhoto, iris et scans : guichet Register.");
            return;
        }

        FingerCatalog.FingerDef finger = FingerCatalog.ALL_TEN[currentFingerIndex];
        txtCurrentFinger.setText("Doigt " + (currentFingerIndex + 1) + "/10 — " + finger.label);
        btnCapture.setText(capturing ? "Annuler la capture" : ("Capturer : " + finger.label));
        btnCapture.setEnabled((deviceReady || capturing) && !deviceInitializing.get());

        if (!deviceReady && !deviceInitializing.get()) {
            txtStatus.setText("En attente du capteur. Utilisez « Réinitialiser le capteur » si besoin.");
        }
    }

    private void captureCurrentFinger() {
        capturing = true;
        btnCapture.setEnabled(true);
        btnReinit.setEnabled(false);
        progressCaptureQuality.setProgress(0);

        FingerCatalog.FingerDef finger = FingerCatalog.ALL_TEN[currentFingerIndex];
        txtStatus.setText("Capture — " + finger.label + "\nMaintenez le doigt sur le capteur...");

        FingerprintProcessObserver observer = new FingerprintProcessObserver(
                this, txtStatus, imgFingerprint, progressCaptureQuality);

        new Thread(() -> {
            try {
                TemplateList templateList = new TemplateList();
                int ret = MorphoCaptureHelper.captureOneTemplate(morphoDevice, templateList, observer);

                Log.d(TAG, "Capture " + finger.registerCode + " ret=" + ret + " templates=" + templateList.getNbTemplate());

                if (ret != ErrorCodes.MORPHO_OK || templateList.getNbTemplate() != 1) {
                    throw new Exception("Capture échouée (code " + ret + "). Gardez le doigt appuyé sur le capteur.");
                }

                Template template = templateList.getTemplate(0);
                byte[] templateData = template.getData();
                if (templateData == null || templateData.length == 0) {
                    throw new Exception("Template vide après capture.");
                }

                uploadTemplate(finger, templateData);
            } catch (Exception e) {
                Log.e(TAG, "Capture error", e);
                MorphoCaptureHelper.cancelAcquisition(morphoDevice);
                runOnUiThread(() -> finishCaptureWithError(e.getMessage()));
            }
        }).start();
    }

    private void finishCaptureWithError(String message) {
        capturing = false;
        btnReinit.setEnabled(true);
        txtStatus.setText("Erreur : " + message);
        Toast.makeText(this, message, Toast.LENGTH_LONG).show();
        refreshUi();
    }

    private void uploadTemplate(FingerCatalog.FingerDef finger, byte[] templateData) {
        enrollService.uploadFingerprint(employeeId, finger.registerCode, templateData, new EnrollService.EnrollCallback() {
            @Override
            public void onSuccess(org.json.JSONObject response) {
                runOnUiThread(() -> {
                    savedFingers.put(finger.registerCode, true);
                    currentFingerIndex++;
                    skipCompletedFingers();
                    capturing = false;
                    btnReinit.setEnabled(true);
                    progressCaptureQuality.setProgress(0);
                    refreshUi();
                    Toast.makeText(FingerprintEnrollActivity.this,
                            finger.label + " enregistré sur le serveur", Toast.LENGTH_SHORT).show();
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() -> finishCaptureWithError("Envoi serveur : " + error));
            }
        });
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (capturing) {
            MorphoCaptureHelper.cancelAcquisition(morphoDevice);
            capturing = false;
        }
    }

    @Override
    protected void onDestroy() {
        MorphoCaptureHelper.cancelAcquisition(morphoDevice);
        super.onDestroy();
        getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
}
