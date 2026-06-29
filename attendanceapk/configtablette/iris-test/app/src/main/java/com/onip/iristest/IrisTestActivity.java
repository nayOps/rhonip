package com.onip.iristest;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Bitmap;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.onip.iristest.IrisInterface;
import com.onip.iristest.NativePreviewResultListener;
import com.onip.iristest.PreviewResultListener;

import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;

/**
 * Application de test d'iris pour MorphoTablet
 * Basée sur l'exemple SDK officiel IrisSensor_Demo
 */
public class IrisTestActivity extends Activity implements PreviewResultListener {

    private static final String TAG = "IrisTestActivity";
    
    // Modes de fonctionnement
    private static final int ENROLL_MODE = 0;
    private static final int IDENT_MODE = 1;
    private static final int AUTHENT_MODE = 2;
    
    // Résultats
    private static final int CAPTURE_RESULT_OK = 0;
    private static final int CAPTURE_RESULT_KO = 1;
    
    // Paramètres
    private static final int CAPTURE_TIMEOUT = 25000; // 25 secondes
    private static final int MATCH_THRESHOLD = 4000; // Score minimum pour correspondance
    private static final int CAPTURE_QUALITY_THRESHOLD = 100; // Qualité minimum
    
    public static final String WORKING_DIR = "/sdcard/IrisTest";
    
    // Interface native
    private IrisInterface irisInterface;
    
    // Données de capture
    private byte[] leftTemplate = null;
    private byte[] rightTemplate = null;
    private Bitmap leftImage = null;
    private Bitmap rightImage = null;
    private int matchScore = 0;
    private int captureQuality = 0;
    private int leftCaptureQuality = 0;
    private int rightCaptureQuality = 0;
    private String matchId = "";
    private int captureResult = CAPTURE_RESULT_KO;
    private int currentMode = -1;
    
    // UI Components
    private EditText editFirstName;
    private EditText editLastName;
    private Button btnEnroll;
    private Button btnIdentify;
    private Button btnAuthenticate;
    private Button btnVerify;
    private TextView txtStatus;
    private TextView txtQuality;
    private TextView txtScore;
    private ProgressBar progressBar;
    private ImageView imgLeftIris;
    private ImageView imgRightIris;
    
    // Variables de contrôle
    private boolean capturing = false;
    private String storedFirstName = "";
    private String storedLastName = "";
    private byte[] storedLeftTemplate = null;
    private byte[] storedRightTemplate = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        try {
            Log.d(TAG, "=== DÉBUT ONCREATE ===");
            setContentView(R.layout.activity_iris_test);
            Log.d(TAG, "Layout chargé avec succès");
            
            initializeViews();
            Log.d(TAG, "Views initialisées");
            
            initializeIrisInterface();
            Log.d(TAG, "Interface iris initialisée");
            Log.d(TAG, "=== FIN ONCREATE ===");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR CRITIQUE dans onCreate: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur critique: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void initializeViews() {
        try {
            Log.d(TAG, "Initialisation des views...");
            
            editFirstName = findViewById(R.id.edit_first_name);
            editLastName = findViewById(R.id.edit_last_name);
            btnEnroll = findViewById(R.id.btn_enroll);
            btnIdentify = findViewById(R.id.btn_identify);
            btnAuthenticate = findViewById(R.id.btn_authenticate);
            btnVerify = findViewById(R.id.btn_verify);
            txtStatus = findViewById(R.id.txt_status);
            txtQuality = findViewById(R.id.txt_quality);
            txtScore = findViewById(R.id.txt_score);
            progressBar = findViewById(R.id.progress_bar);
            imgLeftIris = findViewById(R.id.img_left_iris);
            imgRightIris = findViewById(R.id.img_right_iris);

            Log.d(TAG, "Views trouvées avec succès");

            // Event listeners
            btnEnroll.setOnClickListener(this::onEnroll);
            btnIdentify.setOnClickListener(this::onIdentify);
            btnAuthenticate.setOnClickListener(this::onAuthenticate);
            btnVerify.setOnClickListener(this::onVerify);

            Log.d(TAG, "Listeners configurés");

            // Créer le dossier de travail
            File workingDir = new File(WORKING_DIR);
            if (!workingDir.exists()) {
                boolean created = workingDir.mkdirs();
                Log.d(TAG, "Dossier créé: " + created);
            }

            txtStatus.setText("Interface iris initialisée");
            Log.d(TAG, "Initialisation views terminée");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR dans initializeViews: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur views: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void initializeIrisInterface() {
        try {
            irisInterface = new IrisInterface();
            
            // Initialiser l'interface native
            new AsyncTask<Void, Void, Integer>() {
                @Override
                protected Integer doInBackground(Void... voids) {
                    try {
                        return irisInterface.initialize();
                    } catch (Exception e) {
                        Log.e(TAG, "Erreur dans initialize(): " + e.getMessage());
                        return -1;
                    }
                }

                @Override
                protected void onPostExecute(Integer result) {
                    if (result == 0) {
                        txtStatus.setText("✓ Interface iris initialisée avec succès");
                        enableButtons(true);
                        Toast.makeText(IrisTestActivity.this, "Interface iris prête !", Toast.LENGTH_SHORT).show();
                    } else {
                        txtStatus.setText("✗ Erreur d'initialisation: " + result);
                        enableButtons(false);
                        Toast.makeText(IrisTestActivity.this, "Erreur d'initialisation iris", Toast.LENGTH_LONG).show();
                    }
                }
            }.execute();
            
        } catch (Exception e) {
            Log.e(TAG, "Erreur initialisation interface iris: " + e.getMessage());
            txtStatus.setText("✗ Erreur d'initialisation: " + e.getMessage());
            enableButtons(false);
            Toast.makeText(this, "Erreur critique: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void enableButtons(boolean enabled) {
        btnEnroll.setEnabled(enabled);
        btnIdentify.setEnabled(enabled);
        btnAuthenticate.setEnabled(enabled);
        btnVerify.setEnabled(enabled);
    }

    private void onEnroll(View view) {
        String firstName = editFirstName.getText().toString().trim();
        String lastName = editLastName.getText().toString().trim();

        if (firstName.isEmpty() || lastName.isEmpty()) {
            Toast.makeText(this, "Veuillez saisir le prénom et le nom", Toast.LENGTH_SHORT).show();
            return;
        }

        currentMode = ENROLL_MODE;
        captureIris(firstName, lastName);
    }

    private void onIdentify(View view) {
        currentMode = IDENT_MODE;
        captureIris("", "");
    }

    private void onAuthenticate(View view) {
        if (storedLeftTemplate == null || storedRightTemplate == null) {
            Toast.makeText(this, "Aucun iris enregistré pour l'authentification", Toast.LENGTH_SHORT).show();
            return;
        }

        currentMode = AUTHENT_MODE;
        captureIris("", "");
    }

    private void onVerify(View view) {
        if (storedLeftTemplate == null || storedRightTemplate == null) {
            Toast.makeText(this, "Aucun iris enregistré pour la vérification", Toast.LENGTH_SHORT).show();
            return;
        }

        currentMode = AUTHENT_MODE;
        captureIris("", "");
    }

    private void captureIris(String firstName, String lastName) {
        if (capturing) {
            return;
        }

        capturing = true;
        enableButtons(false);
        progressBar.setVisibility(View.VISIBLE);
        txtStatus.setText("Capture d'iris en cours...");

        new AsyncTask<Void, Void, Object[]>() {
            @Override
            protected Object[] doInBackground(Void... voids) {
                try {
                    // Capturer les iris
                    Object[] result = irisInterface.capture(CAPTURE_TIMEOUT, MATCH_THRESHOLD);
                    return result;
                } catch (Exception e) {
                    Log.e(TAG, "Erreur capture iris: " + e.getMessage());
                    return null;
                }
            }

            @Override
            protected void onPostExecute(Object[] result) {
                capturing = false;
                enableButtons(true);
                progressBar.setVisibility(View.GONE);

                if (result != null && result.length >= 2) {
                    leftTemplate = (byte[]) result[0];
                    rightTemplate = (byte[]) result[1];
                    
                    // Obtenir les scores et qualités
                    matchScore = irisInterface.getMatchScore();
                    captureQuality = irisInterface.getAcquitisionQuality();
                    leftCaptureQuality = irisInterface.getLeftTemplateQuality();
                    rightCaptureQuality = irisInterface.getRightTemplateQuality();
                    matchId = irisInterface.getMatchIndex() + "";

                    processCaptureResult(firstName, lastName);
                } else {
                    txtStatus.setText("✗ Échec de la capture d'iris");
                    Toast.makeText(IrisTestActivity.this, "Échec de la capture d'iris", Toast.LENGTH_SHORT).show();
                }
            }
        }.execute();
    }

    private void processCaptureResult(String firstName, String lastName) {
        switch (currentMode) {
            case ENROLL_MODE:
                processEnrollment(firstName, lastName);
                break;
            case IDENT_MODE:
                processIdentification();
                break;
            case AUTHENT_MODE:
                processAuthentication();
                break;
        }
    }

    private void processEnrollment(String firstName, String lastName) {
        if (captureQuality >= CAPTURE_QUALITY_THRESHOLD) {
            // Sauvegarder les templates
            storedFirstName = firstName;
            storedLastName = lastName;
            storedLeftTemplate = leftTemplate.clone();
            storedRightTemplate = rightTemplate.clone();

            // Sauvegarder les images
            saveImages(firstName, lastName);

            txtStatus.setText("✓ Enregistrement réussi");
            txtQuality.setText("Qualité: " + captureQuality);
            txtScore.setText("Score: " + matchScore);
            
            Toast.makeText(this, "Iris enregistré avec succès !", Toast.LENGTH_SHORT).show();
            captureResult = CAPTURE_RESULT_OK;
        } else {
            txtStatus.setText("✗ Qualité insuffisante (" + captureQuality + "/" + CAPTURE_QUALITY_THRESHOLD + ")");
            txtQuality.setText("Qualité: " + captureQuality + " (minimum: " + CAPTURE_QUALITY_THRESHOLD + ")");
            txtScore.setText("Score: " + matchScore);
            
            Toast.makeText(this, "Qualité d'iris insuffisante", Toast.LENGTH_SHORT).show();
            captureResult = CAPTURE_RESULT_KO;
        }
    }

    private void processIdentification() {
        if (matchScore >= MATCH_THRESHOLD) {
            txtStatus.setText("✓ Identification réussie");
            txtQuality.setText("Qualité: " + captureQuality);
            txtScore.setText("Score: " + matchScore + " (ID: " + matchId + ")");
            
            Toast.makeText(this, "Iris identifié avec succès !", Toast.LENGTH_SHORT).show();
            captureResult = CAPTURE_RESULT_OK;
        } else {
            txtStatus.setText("✗ Identification échouée");
            txtQuality.setText("Qualité: " + captureQuality);
            txtScore.setText("Score: " + matchScore + " (minimum: " + MATCH_THRESHOLD + ")");
            
            Toast.makeText(this, "Iris non identifié", Toast.LENGTH_SHORT).show();
            captureResult = CAPTURE_RESULT_KO;
        }
    }

    private void processAuthentication() {
        if (storedLeftTemplate != null && storedRightTemplate != null) {
            // Comparer avec les templates stockés
            boolean leftMatch = compareTemplates(leftTemplate, storedLeftTemplate);
            boolean rightMatch = compareTemplates(rightTemplate, storedRightTemplate);

            if (leftMatch || rightMatch) {
                txtStatus.setText("✓ Authentification réussie");
                txtQuality.setText("Qualité: " + captureQuality);
                txtScore.setText("Score: " + matchScore + " (" + storedFirstName + " " + storedLastName + ")");
                
                Toast.makeText(this, "Authentification réussie !", Toast.LENGTH_SHORT).show();
                captureResult = CAPTURE_RESULT_OK;
            } else {
                txtStatus.setText("✗ Authentification échouée");
                txtQuality.setText("Qualité: " + captureQuality);
                txtScore.setText("Score: " + matchScore);
                
                Toast.makeText(this, "Authentification échouée", Toast.LENGTH_SHORT).show();
                captureResult = CAPTURE_RESULT_KO;
            }
        } else {
            txtStatus.setText("✗ Aucun iris enregistré");
            Toast.makeText(this, "Aucun iris enregistré pour l'authentification", Toast.LENGTH_SHORT).show();
            captureResult = CAPTURE_RESULT_KO;
        }
    }

    private boolean compareTemplates(byte[] template1, byte[] template2) {
        if (template1 == null || template2 == null) {
            return false;
        }

        if (template1.length != template2.length) {
            return false;
        }

        // Comparaison simple byte par byte
        int differences = 0;
        for (int i = 0; i < template1.length; i++) {
            if (template1[i] != template2[i]) {
                differences++;
            }
        }

        // Tolérance de 10% de différences
        double tolerance = template1.length * 0.1;
        return differences <= tolerance;
    }

    private void saveImages(String firstName, String lastName) {
        try {
            String timestamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
            String leftImagePath = WORKING_DIR + "/" + firstName + "_" + lastName + "_left_" + timestamp + ".jpg";
            String rightImagePath = WORKING_DIR + "/" + firstName + "_" + lastName + "_right_" + timestamp + ".jpg";

            // Sauvegarder les images (simulation - les vraies images viendraient du SDK)
            // Ici on créerait des Bitmap à partir des données du SDK
            
            Log.d(TAG, "Images sauvegardées: " + leftImagePath + ", " + rightImagePath);
        } catch (Exception e) {
            Log.e(TAG, "Erreur sauvegarde images: " + e.getMessage());
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (irisInterface != null) {
            try {
                irisInterface.cancel();
            } catch (Exception e) {
                Log.e(TAG, "Erreur fermeture interface iris: " + e.getMessage());
            }
        }
    }

    @Override
    public void onPreviewResult(Bitmap leftImage, Bitmap rightImage) {
        runOnUiThread(() -> {
            if (leftImage != null) {
                imgLeftIris.setImageBitmap(leftImage);
            }
            if (rightImage != null) {
                imgRightIris.setImageBitmap(rightImage);
            }
        });
    }
}
