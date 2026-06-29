package com.onip.cameratest;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.hardware.Camera;
import android.net.Uri;
import android.os.AsyncTask;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.View;
import android.widget.FrameLayout;
import android.widget.ImageButton;
import android.widget.TextView;
import android.widget.Toast;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;

/**
 * Application de test de caméra pour MorphoTablet
 * Basée sur l'exemple SDK officiel
 */
public class CameraTestActivity extends Activity implements View.OnClickListener {

    private static final String TAG = "CameraTestActivity";
    
    private int NB_CAM = 0;
    private int indexCam = 0;
    private FrameLayout frameLayout;
    private int frameWidth = 0;
    private int frameHeight = 0;
    private ImageButton btn_capture;
    private ImageButton btn_switch;
    private TextView txtStatus;

    private boolean isNotAvailable;
    private SurfaceHolder holder;
    private Camera cam = null;
    private CameraPreview preview = null;
    private Camera.PictureCallback pictureCb;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        if (savedInstanceState != null) {
            indexCam = savedInstanceState.getInt("indexCam");
        } else {
            indexCam = 0;
        }
        
        setContentView(R.layout.activity_camera_test);

        initializeViews();
        setupCamera();
    }

    private void initializeViews() {
        frameLayout = findViewById(R.id.cameraFrame);
        btn_capture = findViewById(R.id.btn_capture);
        btn_switch = findViewById(R.id.btn_switch);
        txtStatus = findViewById(R.id.txt_status);

        btn_capture.setOnClickListener(this);
        btn_switch.setOnClickListener(this);

        txtStatus.setText(getString(R.string.status_initializing));
    }

    private void setupCamera() {
        frameLayout.addOnLayoutChangeListener(new View.OnLayoutChangeListener() {
            @Override
            public void onLayoutChange(View v, int left, int top, int right, int bottom, 
                                     int oldLeft, int oldTop, int oldRight, int oldBottom) {
                Log.d(TAG, "Layout changed - w: " + frameLayout.getWidth() + " h: " + frameLayout.getHeight());
                frameWidth = frameLayout.getWidth();
                frameHeight = frameLayout.getHeight();

                if (cam != null) {
                    Camera.Parameters param = cam.getParameters();
                    List<Camera.Size> sizes = param.getSupportedPreviewSizes();
                    Camera.Size optSize = getOptimalPreviewSize(sizes, frameWidth, frameHeight);
                    param.setPreviewSize(optSize.width, optSize.height);
                    cam.setParameters(param);
                }
            }
        });

        isNotAvailable = false;
        NB_CAM = Camera.getNumberOfCameras();

        if (NB_CAM > 0 && indexCam < NB_CAM) {
            cam = getCamera();

            if (cam != null) {
                preview = new CameraPreview(this, cam);
                holder = preview.getHolder();
                frameLayout.addView(preview);

                setupPictureCallback();
                txtStatus.setText(getString(R.string.status_ready));
            } else {
                txtStatus.setText(getString(R.string.error_camera));
            }
        } else {
            txtStatus.setText("Aucune caméra détectée");
        }
    }

    private void setupPictureCallback() {
        pictureCb = new Camera.PictureCallback() {
            @Override
            public void onPictureTaken(byte[] data, Camera camera) {
                File pictureFile = getOutputMediaFile();
                if (pictureFile == null) {
                    Log.d(TAG, "Erreur création fichier média");
                    runOnUiThread(() -> {
                        txtStatus.setText("Erreur sauvegarde");
                        Toast.makeText(CameraTestActivity.this, "Erreur sauvegarde", Toast.LENGTH_SHORT).show();
                    });
                    return;
                }

                try {
                    FileOutputStream fos = new FileOutputStream(pictureFile);
                    fos.write(data);
                    fos.close();

                    camera.startPreview();

                    // Afficher la photo capturée
                    Intent intent = new Intent();
                    intent.setAction(Intent.ACTION_VIEW);
                    intent.setDataAndType(Uri.fromFile(pictureFile), "image/*");
                    startActivity(intent);

                    String msg = getString(R.string.photo_saved) + ": " + pictureFile.getName();
                    runOnUiThread(() -> {
                        txtStatus.setText(getString(R.string.status_ready));
                        Toast.makeText(CameraTestActivity.this, msg, Toast.LENGTH_LONG).show();
                    });

                } catch (FileNotFoundException e) {
                    Log.d(TAG, "Fichier non trouvé: " + e.getMessage());
                } catch (IOException e) {
                    Log.d(TAG, "Erreur accès fichier: " + e.getMessage());
                }
            }
        };
    }

    public Camera getCamera() {
        isNotAvailable = true;
        Camera c = null;

        if (indexCam == NB_CAM) {
            indexCam = 0;
        }

        try {
            c = Camera.open(indexCam);

            Camera.CameraInfo camInfo = new Camera.CameraInfo();
            c.getCameraInfo(indexCam, camInfo);

            Camera.Parameters params = c.getParameters();
            params.setPictureSize(1920, 1080);
            params.setJpegQuality(100);

            if (camInfo.facing == Camera.CameraInfo.CAMERA_FACING_FRONT) {
                c.setDisplayOrientation(180);
                params.setRotation(180);
                params.setPictureSize(1600, 1200);
            }

            c.setParameters(params);
            Log.d(TAG, "Caméra ouverte: " + indexCam + " (Facing: " + camInfo.facing + ")");
        } catch (Exception e) {
            Log.e(TAG, "Erreur ouverture caméra: " + e.getMessage());
        }

        isNotAvailable = false;
        return c;
    }

    public void closeCamera() {
        if (cam != null) {
            holder = preview.getHolder();
            cam.stopPreview();
            cam.release();
            cam = null;
            Log.d(TAG, "Caméra fermée");
        }
    }

    @Override
    public void onClick(View v) {
        int id = v.getId();
        if (id == R.id.btn_capture) {
            if (cam != null) {
                txtStatus.setText(getString(R.string.status_capturing));
                cam.takePicture(null, null, pictureCb);
            } else {
                Toast.makeText(this, "Caméra non disponible", Toast.LENGTH_SHORT).show();
            }
        } else if (id == R.id.btn_switch && !isNotAvailable) {
            new AsyncTask<Void, Void, Void>() {
                ProgressDialog progressDialog;

                @Override
                protected void onPreExecute() {
                    super.onPreExecute();
                    progressDialog = new ProgressDialog(CameraTestActivity.this);
                    progressDialog.setMessage("Changement de caméra...");
                    progressDialog.setCancelable(false);
                    progressDialog.show();

                    closeCamera();
                }

                @Override
                protected Void doInBackground(Void... voids) {
                    indexCam++;
                    cam = getCamera();
                    return null;
                }

                @Override
                protected void onPostExecute(Void aVoid) {
                    super.onPostExecute(aVoid);
                    progressDialog.dismiss();

                    try {
                        preview.setCamera(cam);
                        cam.setPreviewDisplay(holder);
                        cam.startPreview();
                        txtStatus.setText(getString(R.string.status_ready));
                    } catch (IOException e) {
                        Log.e(TAG, "Erreur preview: " + e.getMessage());
                        txtStatus.setText(getString(R.string.error_camera));
                    }
                }
            }.execute();
        }
    }

    private static File getOutputMediaFile() {
        File mediaStorageDir = new File(Environment.getExternalStorageDirectory(), "Camera_Test");

        if (!mediaStorageDir.exists()) {
            if (!mediaStorageDir.mkdirs()) {
                Log.d(TAG, "Échec création dossier");
                return null;
            }
        }

        String timeStamp = new SimpleDateFormat("yyyyMMdd_HHmmss").format(new Date());
        File mediaFile = new File(mediaStorageDir.getPath() + File.separator +
                "IMG_" + timeStamp + ".jpg");

        return mediaFile;
    }

    private Camera.Size getOptimalPreviewSize(List<Camera.Size> sizes, int w, int h) {
        final double ASPECT_TOLERANCE = 0.05;
        double targetRatio = (double) w / h;

        if (sizes == null) return null;

        Camera.Size optimalSize = null;
        double minDiff = Double.MAX_VALUE;
        int targetHeight = h;

        for (Camera.Size size : sizes) {
            double ratio = (double) size.width / size.height;
            if (Math.abs(ratio - targetRatio) > ASPECT_TOLERANCE) continue;
            if (Math.abs(size.height - targetHeight) < minDiff) {
                optimalSize = size;
                minDiff = Math.abs(size.height - targetHeight);
            }
        }

        if (optimalSize == null) {
            minDiff = Double.MAX_VALUE;
            for (Camera.Size size : sizes) {
                if (Math.abs(size.height - targetHeight) < minDiff) {
                    optimalSize = size;
                    minDiff = Math.abs(size.height - targetHeight);
                }
            }
        }
        return optimalSize;
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putInt("indexCam", indexCam);
    }

    @Override
    protected void onPause() {
        super.onPause();
        closeCamera();
        if (preview != null) {
            frameLayout.removeView(preview);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (cam == null) {
            cam = getCamera();
            if (cam != null) {
                preview = new CameraPreview(this, cam);
                frameLayout.addView(preview);
                setupPictureCallback();
            }
        }
    }
}
