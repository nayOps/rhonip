package com.onip.iristest;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.ColorMatrix;
import android.graphics.ColorMatrixColorFilter;
import android.graphics.Paint;
import android.os.Bundle;
import android.util.Log;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import java.nio.ByteBuffer;

/**
 * Version basée sur l'exemple SDK officiel avec vraies méthodes natives
 */
public class RealIrisActivity extends Activity {

    private static final String TAG = "RealIris";
    
    // Interface native réelle
    private IrisInterface irisInterface;
    
    // Variables de capture
    private byte[] leftTemplate = null;
    private byte[] rightTemplate = null;
    private Bitmap leftImage = null;
    private Bitmap rightImage = null;
    private int matchScore = 0;
    private int acquisitionQuality = 0;
    private int leftAcquisitionQuality = 0;
    private int rightAcquisitionQuality = 0;
    
    // UI Components
    private ImageView imageView;
    private TextView distanceIndicator;
    
    // Paramètres
    private int acquisitionTimeout = 25000;
    private int matchingThreshold = 4000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        try {
            Log.d(TAG, "=== DÉBUT REAL IRIS ONCREATE ===");
            setContentView(R.layout.activity_sdk_iris);
            Log.d(TAG, "Layout chargé");
            
            initializeViews();
            initializeIrisInterface();
            
            Log.d(TAG, "=== FIN REAL IRIS ONCREATE ===");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR CRITIQUE: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur critique: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void initializeViews() {
        try {
            Log.d(TAG, "Initialisation views...");
            
            imageView = findViewById(R.id.imageView);
            distanceIndicator = findViewById(R.id.distanceIndicator);
            
            Log.d(TAG, "Views trouvées");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR views: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur views: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void initializeIrisInterface() {
        try {
            Log.d(TAG, "Initialisation interface native...");
            
            irisInterface = new IrisInterface();
            
            // Initialisation native
            int ret = irisInterface.initialize();
            Log.d(TAG, "Initialize result: " + ret);
            
            if (ret == 0) {
                // Configuration du filtre couleur comme dans l'exemple
                float mx[] = {
                        -1.0f, 0.0f, 0.0f, 0.0f, 255.0f,
                        0.0f, -1.0f, 0.0f, 0.0f, 255.0f,
                        0.0f, 0.0f, -1.0f, 0.0f, 255.0f,
                        0.0f, 0.0f, 0.0f, 1.0f, 0.0f
                };
                ColorMatrix cm = new ColorMatrix(mx);
                imageView.setColorFilter(new ColorMatrixColorFilter(cm));
                
                // Nettoyage des templates
                irisInterface.clearTemplates();
                
                // Obtenir les informations du device
                String deviceId = IrisInterface.getDeviceId();
                String cameraModel = IrisInterface.getCameraModelId();
                String version = IrisInterface.getMobIrisVersion();
                
                distanceIndicator.setText("✓ Interface native initialisée\nDevice: " + deviceId + "\nCamera: " + cameraModel + "\nVersion: " + version);
                Toast.makeText(this, "Interface native prête !", Toast.LENGTH_SHORT).show();
                
                Log.d(TAG, "Interface native initialisée - Device: " + deviceId + ", Camera: " + cameraModel);
                
            } else {
                distanceIndicator.setText("✗ Erreur d'initialisation native: " + ret);
                Toast.makeText(this, "Erreur d'initialisation: " + ret, Toast.LENGTH_LONG).show();
                Log.e(TAG, "Erreur d'initialisation native: " + ret);
            }
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR interface native: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur interface: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    /**
     * Conversion d'image comme dans l'exemple SDK
     */
    public Bitmap rt_imageToBitmap(int width, int height, byte[] data) {
        float mx[] = {
                -1.0f, 0.0f, 0.0f, 0.0f, 255.0f,
                0.0f, -1.0f, 0.0f, 0.0f, 255.0f,
                0.0f, 0.0f, -1.0f, 0.0f, 255.0f,
                0.0f, 0.0f, 0.0f, 1.0f, 0.0f
        };

        Bitmap img = Bitmap.createBitmap(width, height, Bitmap.Config.ALPHA_8);
        img.copyPixelsFromBuffer(ByteBuffer.wrap(data));
        ColorMatrix cm = new ColorMatrix(mx);
        Bitmap var2 = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
        Canvas c = new Canvas(var2);
        Paint paint = new Paint();
        paint.setColorFilter(new ColorMatrixColorFilter(cm));
        c.drawBitmap(img, 0, 0, paint);
        return var2;
    }

    @Override
    protected void onResume() {
        super.onResume();
        Log.d(TAG, "onResume - Démarrage capture native");
        
        // Démarrer la capture native
        startNativeCapture();
    }

    private void startNativeCapture() {
        try {
            Log.d(TAG, "Démarrage capture native...");
            
            // Capture native comme dans l'exemple SDK
            Object[] objs = irisInterface.capture(acquisitionTimeout, matchingThreshold);
            
            if (objs != null && objs.length > 0) {
                Log.d(TAG, "Capture native réussie - " + objs.length + " objets");
                
                // Vérifier le statut de retour
                if (((Integer) objs[0]).intValue() == 0) {
                    Log.d(TAG, "Status: Succès");
                    
                    // Traitement des résultats comme dans l'exemple
                    int cnt = 1;
                    while (cnt < objs.length) {
                        Log.d(TAG, "Traitement objet " + cnt + " de type " + objs[cnt].getClass().getSimpleName());
                        
                        if (((Integer) objs[cnt]).intValue() == 0) {
                            cnt++;
                            leftTemplate = ((byte[]) objs[cnt++]);
                            int width = ((Integer) objs[cnt++]).intValue();
                            int height = ((Integer) objs[cnt++]).intValue();
                            byte imgbytes[] = ((byte[]) objs[cnt++]);
                            leftImage = rt_imageToBitmap(width, height, imgbytes);
                            
                            Log.d(TAG, "Iris gauche capturé - " + width + "x" + height);
                            
                        } else if (((Integer) objs[cnt]).intValue() == 1) {
                            cnt++;
                            rightTemplate = ((byte[]) objs[cnt++]);
                            int width = ((Integer) objs[cnt++]).intValue();
                            int height = ((Integer) objs[cnt++]).intValue();
                            byte imgbytes[] = ((byte[]) objs[cnt++]);
                            rightImage = rt_imageToBitmap(width, height, imgbytes);
                            
                            Log.d(TAG, "Iris droit capturé - " + width + "x" + height);
                        } else {
                            cnt++; // Passer au suivant si type inconnu
                        }
                    }
                } else {
                    Log.e(TAG, "Status d'erreur: " + objs[0]);
                    distanceIndicator.setText("✗ Erreur de capture: " + objs[0]);
                    return;
                }
                
                // Obtenir les métriques natives
                matchScore = IrisInterface.getMatchScore();
                acquisitionQuality = IrisInterface.getAcquitisionQuality();
                leftAcquisitionQuality = IrisInterface.getLeftTemplateQuality();
                rightAcquisitionQuality = IrisInterface.getRightTemplateQuality();
                
                // Afficher les résultats
                displayResults();
                
            } else {
                Log.e(TAG, "Capture native échouée");
                distanceIndicator.setText("✗ Échec de la capture native");
                Toast.makeText(this, "Échec de la capture native", Toast.LENGTH_SHORT).show();
            }
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR capture native: " + e.getMessage(), e);
            Toast.makeText(this, "Erreur capture: " + e.getMessage(), Toast.LENGTH_LONG).show();
        }
    }

    private void displayResults() {
        try {
            String result = "✓ Capture native réussie\n";
            result += "Score: " + matchScore + "\n";
            result += "Qualité: " + acquisitionQuality + "\n";
            result += "Gauche: " + leftAcquisitionQuality + "\n";
            result += "Droite: " + rightAcquisitionQuality;
            
            distanceIndicator.setText(result);
            Toast.makeText(this, "Capture d'iris native réussie !", Toast.LENGTH_SHORT).show();
            
            Log.d(TAG, "Résultats affichés");
            
        } catch (Exception e) {
            Log.e(TAG, "ERREUR affichage: " + e.getMessage(), e);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        Log.d(TAG, "onPause - Annulation capture native");
        if (irisInterface != null) {
            irisInterface.cancel();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        Log.d(TAG, "onDestroy - Nettoyage");
        if (irisInterface != null) {
            irisInterface.cancel();
        }
    }
}
