package com.onip.biometric.services;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.hardware.Camera;
import android.util.Log;
import android.view.SurfaceHolder;
import android.view.SurfaceView;

import java.io.ByteArrayOutputStream;
import java.io.IOException;

/**
 * Service pour gérer la caméra native de la tablette
 */
public class CameraService implements Camera.PictureCallback, SurfaceHolder.Callback {
    
    private static final String TAG = "CameraService";
    
    private Context context;
    private Camera camera;
    private SurfaceView surfaceView;
    private boolean isOpen = false;
    
    // Interface pour les callbacks
    public interface PhotoCallback {
        void onPhotoTaken(byte[] photoData);
        void onError(String errorMessage);
    }
    
    private PhotoCallback photoCallback;
    
    public CameraService(Context context) {
        this.context = context;
    }
    
    /**
     * Ouvrir la caméra
     */
    public boolean openCamera(SurfaceView surfaceView) {
        try {
            Log.d(TAG, "Opening camera...");
            
            this.surfaceView = surfaceView;
            SurfaceHolder holder = surfaceView.getHolder();
            holder.addCallback(this);
            holder.setType(SurfaceHolder.SURFACE_TYPE_PUSH_BUFFERS);
            
            camera = Camera.open();
            if (camera != null) {
                isOpen = true;
                Log.d(TAG, "Camera opened successfully");
                return true;
            } else {
                Log.e(TAG, "Failed to open camera");
                return false;
            }
            
        } catch (Exception e) {
            Log.e(TAG, "Exception opening camera: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Prendre une photo
     */
    public void takePicture(PhotoCallback callback) {
        if (!isOpen || camera == null) {
            callback.onError("Caméra non ouverte");
            return;
        }
        
        this.photoCallback = callback;
        
        try {
            // Paramètres de la caméra
            Camera.Parameters params = camera.getParameters();
            
            // Définir la qualité JPEG
            params.setJpegQuality(90);
            
            // Définir la taille de l'image (si supportée)
            for (Camera.Size size : params.getSupportedPictureSizes()) {
                if (size.width <= 1920 && size.height <= 1080) {
                    params.setPictureSize(size.width, size.height);
                    break;
                }
            }
            
            camera.setParameters(params);
            
            // Prendre la photo
            camera.takePicture(null, null, this);
            
        } catch (Exception e) {
            Log.e(TAG, "Exception taking picture: " + e.getMessage());
            callback.onError("Erreur lors de la prise de photo: " + e.getMessage());
        }
    }
    
    @Override
    public void onPictureTaken(byte[] data, Camera camera) {
        Log.d(TAG, "Picture taken, size: " + data.length + " bytes");
        
        try {
            // Convertir en Bitmap pour traitement
            Bitmap bitmap = BitmapFactory.decodeByteArray(data, 0, data.length);
            
            // Rotation si nécessaire (caméra frontale)
            Matrix matrix = new Matrix();
            matrix.postRotate(90); // Rotation de 90 degrés
            Bitmap rotatedBitmap = Bitmap.createBitmap(bitmap, 0, 0, 
                bitmap.getWidth(), bitmap.getHeight(), matrix, true);
            
            // Convertir en JPEG
            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            rotatedBitmap.compress(Bitmap.CompressFormat.JPEG, 90, outputStream);
            byte[] finalData = outputStream.toByteArray();
            
            // Callback avec les données finales
            if (photoCallback != null) {
                photoCallback.onPhotoTaken(finalData);
            }
            
            // Redémarrer la prévisualisation
            camera.startPreview();
            
        } catch (Exception e) {
            Log.e(TAG, "Exception processing picture: " + e.getMessage());
            if (photoCallback != null) {
                photoCallback.onError("Erreur de traitement: " + e.getMessage());
            }
        }
    }
    
    @Override
    public void surfaceCreated(SurfaceHolder holder) {
        Log.d(TAG, "Surface created");
        if (camera != null) {
            try {
                camera.setPreviewDisplay(holder);
                camera.startPreview();
            } catch (IOException e) {
                Log.e(TAG, "Error setting camera preview: " + e.getMessage());
            }
        }
    }
    
    @Override
    public void surfaceChanged(SurfaceHolder holder, int format, int width, int height) {
        Log.d(TAG, "Surface changed: " + width + "x" + height);
        if (camera != null) {
            try {
                camera.stopPreview();
                camera.setPreviewDisplay(holder);
                camera.startPreview();
            } catch (Exception e) {
                Log.e(TAG, "Error restarting camera preview: " + e.getMessage());
            }
        }
    }
    
    @Override
    public void surfaceDestroyed(SurfaceHolder holder) {
        Log.d(TAG, "Surface destroyed");
    }
    
    /**
     * Fermer la caméra
     */
    public void close() {
        Log.d(TAG, "Closing camera...");
        
        if (camera != null) {
            camera.stopPreview();
            camera.release();
            camera = null;
        }
        
        isOpen = false;
        Log.d(TAG, "Camera closed");
    }
    
    /**
     * Vérifier si la caméra est ouverte
     */
    public boolean isOpen() {
        return isOpen && camera != null;
    }
}