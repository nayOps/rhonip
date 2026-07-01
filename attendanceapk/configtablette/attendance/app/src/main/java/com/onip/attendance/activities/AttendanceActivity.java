package com.onip.attendance.activities;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import com.onip.attendance.AttendanceApplication;
import com.onip.attendance.R;
import com.onip.attendance.fingerprint.FingerprintProcessObserver;
import com.onip.attendance.fingerprint.MorphoCaptureHelper;
import com.onip.attendance.models.Employee;
import com.onip.attendance.services.AttendanceService;
import com.onip.attendance.services.DeviceManager;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.FalseAcceptanceRate;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.morpho.morphosmart.sdk.Template;
import com.morpho.morphosmart.sdk.TemplateList;
import com.morpho.morphosmart.sdk.TemplateType;
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
    private LinearLayout layoutMatriculeSection;
    private LinearLayout layoutFingerprintSection;
    private EditText editMatricule;
    private Button btnValidateMatricule;
    private TextView txtStatus;
    private ImageView imgFingerprint;
    private ProgressBar progressBar;
    private Button btnCapture;
    private Button btnBack;
    
    // Employé sélectionné via matricule
    private Employee selectedEmployee = null;
    
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
    private AttendanceApplication app;
    
    // Templates chargés pour le matching
    private Map<Integer, Map<String, byte[]>> allTemplates = new HashMap<>();
    private Map<Integer, Employee> employeeById = new HashMap<>();
    private volatile boolean matchingInProgress = false;
    
    private static final int MATCH_FAR = FalseAcceptanceRate.MORPHO_FAR_5;
    private static final int MATCH_SCORE_EXCELLENT = 75;
    private static final int MATCH_SCORE_MINIMUM = 25;
    private static final String INDEX_DROIT = "Index_Droit";

    // Handler pour retour automatique
    private Handler autoReturnHandler = new Handler(Looper.getMainLooper());
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        try {
            setContentView(R.layout.activity_attendance);

            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

            app = (AttendanceApplication) getApplication();
            attendanceService = new AttendanceService(this);
            DeviceManager.rebindUsbHost(this);

            initializeViews();
            loadGlobalData();
        } catch (Exception e) {
            Log.e(TAG, "Crash initialisation écran pointage", e);
            Toast.makeText(this, "Erreur écran pointage: " + e.getMessage(), Toast.LENGTH_LONG).show();
            finish();
        }
    }
    
    private void initializeViews() {
        layoutMatriculeSection = findViewById(R.id.layout_matricule_section);
        layoutFingerprintSection = findViewById(R.id.layout_fingerprint_section);
        editMatricule = findViewById(R.id.edit_matricule);
        btnValidateMatricule = findViewById(R.id.btn_validate_matricule);
        txtStatus = findViewById(R.id.txt_attendance_status);
        imgFingerprint = findViewById(R.id.img_attendance_fingerprint);
        progressBar = findViewById(R.id.progress_attendance);
        btnCapture = findViewById(R.id.btn_capture_attendance);
        btnBack = findViewById(R.id.btn_back_attendance);

        btnValidateMatricule.setOnClickListener(v -> validateMatricule());
        btnCapture.setOnClickListener(v -> captureFingerprint());
        if (btnBack != null) {
            btnBack.setOnClickListener(v -> {
                Intent intent = new Intent(this, LoadingActivity.class);
                intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                startActivity(intent);
                finish();
            });
        }
    }

    private void validateMatricule() {
        String matricule = editMatricule.getText().toString().trim();
        if (matricule.isEmpty()) {
            Toast.makeText(this, R.string.attendance_matricule_empty, Toast.LENGTH_SHORT).show();
            return;
        }

        Employee found = findEmployeeByMatricule(matricule);
        if (found == null) {
            Toast.makeText(this, R.string.attendance_matricule_not_found, Toast.LENGTH_LONG).show();
            return;
        }

        Map<String, byte[]> templates = allTemplates.get(found.getId());
        if (templates == null || templates.isEmpty()) {
            Toast.makeText(this, R.string.attendance_no_fingerprint, Toast.LENGTH_LONG).show();
            return;
        }

        selectedEmployee = found;
        layoutMatriculeSection.setVisibility(View.GONE);
        layoutFingerprintSection.setVisibility(View.VISIBLE);
        btnCapture.setVisibility(View.VISIBLE);
        txtStatus.setText("👤 " + found.getFirstName() + " " + found.getLastName()
                + "\n\n" + getString(R.string.attendance_place_finger));
        btnCapture.setText(R.string.capture);
        btnCapture.setEnabled(true);
    }

    private Employee findEmployeeByMatricule(String matricule) {
        String normalized = matricule.trim().toUpperCase();
        for (Employee employee : employees) {
            if (employee.getNin() != null && employee.getNin().trim().toUpperCase().equals(normalized)) {
                return employee;
            }
        }
        return null;
    }

    private void resetToMatriculeScreen() {
        selectedEmployee = null;
        matchedEmployee = null;
        capturing = false;
        matchingInProgress = false;

        if (editMatricule != null) {
            editMatricule.setText("");
            editMatricule.requestFocus();
        }
        if (imgFingerprint != null) {
            imgFingerprint.setImageResource(R.drawable.ic_fingerprint);
        }
        if (progressBar != null) {
            progressBar.setProgress(0);
            progressBar.setVisibility(View.GONE);
        }
        if (layoutMatriculeSection != null) {
            layoutMatriculeSection.setVisibility(View.VISIBLE);
        }
        if (layoutFingerprintSection != null) {
            layoutFingerprintSection.setVisibility(View.GONE);
        }
        if (btnCapture != null) {
            btnCapture.setVisibility(View.GONE);
            btnCapture.setText(R.string.capture);
            btnCapture.setEnabled(true);
        }
        if (btnValidateMatricule != null) {
            btnValidateMatricule.setEnabled(true);
        }
    }

    private void loadGlobalData() {
        morphoDevice = app.getGlobalMorphoDevice();
        employees = app.getGlobalEmployees();
        allTemplates = app.getGlobalTemplates();
        employeeById.clear();
        for (Employee employee : employees) {
            employeeById.put(employee.getId(), employee);
        }
        
        Log.d(TAG, "✅ Données chargées:");
        Log.d(TAG, "   - Employés: " + employees.size());
        Log.d(TAG, "   - Templates: " + allTemplates.size() + " employé(s)");
        Log.d(TAG, "   - Device: " + (morphoDevice != null ? "✅" : "❌"));
        
        if (morphoDevice == null) {
            Toast.makeText(this, "Capteur non disponible — redémarrez l'application", Toast.LENGTH_LONG).show();
            btnValidateMatricule.setEnabled(false);
            return;
        }
        
        if (employees.isEmpty() || allTemplates.isEmpty()) {
            Toast.makeText(this, "Données non chargées — redémarrez l'application", Toast.LENGTH_LONG).show();
            btnValidateMatricule.setEnabled(false);
            return;
        }
        
        btnValidateMatricule.setEnabled(true);
    }
    
    private void captureFingerprint() {
        if (capturing || morphoDevice == null || selectedEmployee == null) {
            if (capturing) {
                cancelCapture();
            }
            return;
        }

        if (!MorphoCaptureHelper.isDeviceResponsive(morphoDevice)) {
            txtStatus.setText("Capteur bloqué — retournez à l'accueil et relancez l'application.");
            return;
        }

        capturing = true;
        btnCapture.setEnabled(true);
        btnCapture.setText("Annuler");
        progressBar.setVisibility(View.VISIBLE);
        txtStatus.setText("Capture en cours... Placez votre doigt");
        
        processObserver = new FingerprintProcessObserver(this, txtStatus, imgFingerprint, progressBar);
        
        new Thread(() -> {
            try {
                TemplateList templateList = new TemplateList();
                
                int ret = MorphoCaptureHelper.captureOneTemplate(morphoDevice, templateList, processObserver);
                
                if (ret == ErrorCodes.MORPHO_OK) {
                    if (templateList.getNbTemplate() == 1) {
                        Template template = templateList.getTemplate(0);
                        byte[] templateData = template.getData();
                        Log.d(TAG, "✅ Empreinte capturée");
                        if (templateData != null) {
                            matchFingerprint(templateData);
                            return;
                        } else {
                            throw new Exception("Template data is null");
                        }
                    } else {
                        throw new Exception("No template in list");
                    }
                } else {
                    throw new Exception("Erreur capture code " + ret);
                }
                
            } catch (Exception e) {
                Log.e(TAG, "❌ Exception capture: " + e.getMessage(), e);
                MorphoCaptureHelper.cancelAcquisition(morphoDevice);
                runOnUiThread(() -> resetCaptureUi("❌ Erreur: " + e.getMessage()));
            }
        }).start();
    }

    private void cancelCapture() {
        new Thread(() -> {
            MorphoCaptureHelper.cancelAcquisition(morphoDevice);
            runOnUiThread(() -> resetCaptureUi("Capture annulée."));
        }).start();
    }

    private void resetCaptureUi(String message) {
        if (message != null && !message.isEmpty()) {
            txtStatus.setText(message);
        } else if (txtStatus != null) {
            txtStatus.setText(R.string.attendance_place_finger);
        }
        btnCapture.setText(R.string.capture);
        btnCapture.setEnabled(true);
        progressBar.setVisibility(View.GONE);
        capturing = false;
    }
    
    private void matchFingerprint(byte[] capturedTemplate) {
        if (selectedEmployee == null) {
            runOnUiThreadSafe(() -> resetCaptureUi("❌ Matricule non validé"));
            return;
        }
        if (matchingInProgress) {
            return;
        }
        matchingInProgress = true;

        Map<Integer, Map<String, byte[]>> scopedTemplates = new HashMap<>();
        Map<String, byte[]> employeeTemplates = allTemplates.get(selectedEmployee.getId());
        if (employeeTemplates != null) {
            scopedTemplates.put(selectedEmployee.getId(), employeeTemplates);
        }

        new Thread(() -> {
            Log.d(TAG, "=== MATCHING matricule " + selectedEmployee.getNin() + " ===");
            long startTime = System.currentTimeMillis();

            Employee bestMatch = null;
            int bestScore = -1;
            String bestFinger = null;
            int comparisonsDone = 0;

            runOnUiThreadSafe(() ->
                    txtStatus.setText("Vérification empreinte...\n" + selectedEmployee.getFirstName()
                            + " " + selectedEmployee.getLastName()));

            try {
                MatchPassResult pass1 = runMatchPass(
                        capturedTemplate, scopedTemplates, new String[]{INDEX_DROIT},
                        bestMatch, bestScore, bestFinger, comparisonsDone, false);
                bestMatch = pass1.bestMatch;
                bestScore = pass1.bestScore;
                bestFinger = pass1.bestFinger;
                comparisonsDone = pass1.comparisonsDone;

                if (bestScore < MATCH_SCORE_EXCELLENT) {
                    MatchPassResult pass2 = runMatchPass(
                            capturedTemplate,
                            scopedTemplates,
                            new String[]{"Pouce_Droit", "Index_Gauche"},
                            bestMatch,
                            bestScore,
                            bestFinger,
                            comparisonsDone,
                            false
                    );
                    bestMatch = pass2.bestMatch;
                    bestScore = pass2.bestScore;
                    bestFinger = pass2.bestFinger;
                    comparisonsDone = pass2.comparisonsDone;
                }
            } catch (Exception e) {
                Log.e(TAG, "Erreur matching", e);
                runOnUiThreadSafe(() -> resetCaptureUi("❌ Erreur matching: " + e.getMessage()));
                matchingInProgress = false;
                return;
            }

            long elapsedTime = System.currentTimeMillis() - startTime;
            Log.d(TAG, "Matching terminé en " + elapsedTime + "ms, comparaisons=" + comparisonsDone + ", score=" + bestScore);

            final Employee finalMatch = bestMatch;
            final int finalScore = bestScore;
            final String finalBestFinger = bestFinger;
            final int finalComparisonsDone = comparisonsDone;
            matchingInProgress = false;

            if (finalMatch != null && finalScore >= MATCH_SCORE_MINIMUM) {
                matchedEmployee = finalMatch;
                runOnUiThreadSafe(() -> {
                    txtStatus.setText("✅ Empreinte reconnue\n\n" +
                            "👤 " + finalMatch.getFirstName() + " " + finalMatch.getLastName() + "\n" +
                            "Score: " + finalScore + "\n" +
                            "Doigt: " + finalBestFinger + "\n\n" +
                            "Enregistrement du pointage...");
                    recordAttendanceForEmployee(finalMatch);
                });
            } else {
                runOnUiThreadSafe(() -> {
                    txtStatus.setText("❌ Empreinte non reconnue\n\n" +
                            "Comparaisons: " + finalComparisonsDone + "\n" +
                            "Temps: " + elapsedTime + " ms");
                    btnCapture.setText(R.string.capture);
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                    capturing = false;
                });
            }
        }).start();
    }

    private static class MatchPassResult {
        Employee bestMatch;
        int bestScore;
        String bestFinger;
        int comparisonsDone;
    }

    private MatchPassResult runMatchPass(byte[] capturedTemplate,
                                       Map<Integer, Map<String, byte[]>> templatesSource,
                                       String[] fingerNames,
                                       Employee currentBest, int currentScore, String currentFinger,
                                       int comparisonsDone, boolean updateProgress) {
        MatchPassResult result = new MatchPassResult();
        result.bestMatch = currentBest;
        result.bestScore = currentScore;
        result.bestFinger = currentFinger;
        result.comparisonsDone = comparisonsDone;

        int checked = 0;
        int total = templatesSource.size();

        for (Map.Entry<Integer, Map<String, byte[]>> entry : templatesSource.entrySet()) {
            Employee employee = employeeById.get(entry.getKey());
            if (employee == null) {
                continue;
            }

            Map<String, byte[]> empTemplates = entry.getValue();
            for (String fingerName : fingerNames) {
                byte[] storedTemplate = empTemplates.get(fingerName);
                if (storedTemplate == null || storedTemplate.length == 0) {
                    continue;
                }

                result.comparisonsDone++;
                int matchingScore = MorphoCaptureHelper.verifyMatchScore(
                        morphoDevice, capturedTemplate, storedTemplate, MATCH_FAR);

                if (matchingScore > result.bestScore) {
                    result.bestScore = matchingScore;
                    result.bestMatch = employee;
                    result.bestFinger = fingerName;
                }
                if (matchingScore >= MATCH_SCORE_EXCELLENT) {
                    return result;
                }
            }

            checked++;
            if (updateProgress && checked % 10 == 0) {
                final int progress = checked;
                runOnUiThreadSafe(() ->
                        txtStatus.setText("Recherche de correspondance...\n" + progress + "/" + total + " agent(s)"));
            }

            if (result.bestScore >= MATCH_SCORE_EXCELLENT) {
                break;
            }
        }
        return result;
    }

    private boolean isActivityAlive() {
        return !isFinishing() && !isDestroyed();
    }

    private void runOnUiThreadSafe(Runnable action) {
        runOnUiThread(() -> {
            if (isActivityAlive() && action != null) {
                action.run();
            }
        });
    }
    
    private void recordAttendanceForEmployee(Employee employee) {
        Log.d(TAG, "Enregistrement pointage pour: " + employee);

        runOnUiThread(() -> txtStatus.setText(
                "👤 " + employee.getFirstName() + " " + employee.getLastName() + "\n\nEnregistrement en cours..."));

        attendanceService.recordPunch(employee.getId(), new AttendanceService.PunchCallback() {
            @Override
            public void onSuccess(AttendanceService.PunchResult result) {
                runOnUiThread(() -> showPunchResult(employee, result));
            }

            @Override
            public void onError(String error) {
                Log.e(TAG, "Erreur enregistrement pointage: " + error);
                runOnUiThread(() -> {
                    txtStatus.setText("❌ Erreur enregistrement\n" + error);
                    btnCapture.setEnabled(true);
                    progressBar.setVisibility(View.GONE);
                    capturing = false;
                });
            }
        });
    }

    private void showPunchResult(Employee employee, AttendanceService.PunchResult result) {
        String slotLabel = "";
        String punchTime = "";
        if (result.assignedSlot != null) {
            slotLabel = result.assignedSlot.optString("label", "");
            punchTime = result.assignedSlot.optString("punchTime", "");
        }

        int validated = 0;
        int total = 4;
        String dayStatusLabel = "";
        if (result.dayEvaluation != null) {
            validated = result.dayEvaluation.optInt("validatedSlots", 0);
            total = result.dayEvaluation.optInt("totalSlots", 4);
            dayStatusLabel = result.dayEvaluation.optString("dayStatusLabel", "");
        }

        StringBuilder message = new StringBuilder();
        message.append("✅ ").append(result.message).append("\n\n");
        message.append("👤 ").append(employee.getFirstName()).append(" ").append(employee.getLastName()).append("\n");
        if (!slotLabel.isEmpty()) {
            message.append("📍 ").append(slotLabel);
            if (!punchTime.isEmpty() && !"—".equals(punchTime)) {
                message.append(" — ").append(punchTime);
            }
            message.append("\n");
        }
        message.append("📊 ").append(validated).append("/").append(total).append(" plages\n");
        if (!dayStatusLabel.isEmpty()) {
            message.append("📋 ").append(dayStatusLabel);
        }
        if (result.queuedOffline) {
            message.append("\n⏳ Sync RH en attente");
        }

        txtStatus.setText(message.toString());
        btnCapture.setText("Capturer");
        btnCapture.setEnabled(true);
        progressBar.setVisibility(View.GONE);
        capturing = false;

        Toast.makeText(this, result.message, Toast.LENGTH_LONG).show();

        autoReturnHandler.postDelayed(() -> {
            if (isActivityAlive()) {
                resetToMatriculeScreen();
            }
        }, 3000);
    }

    @Override
    protected void onDestroy() {
        matchingInProgress = false;
        MorphoCaptureHelper.cancelAcquisition(morphoDevice);
        super.onDestroy();
        autoReturnHandler.removeCallbacksAndMessages(null);
    }
}

