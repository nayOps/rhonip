package com.onip.biometric.services;

import android.util.Log;

import com.morpho.morphosmart.sdk.CallbackMask;

/**
 * Observer pour les callbacks du processus biométrique
 */
public class BiometricProcessObserver {
    
    private static final String TAG = "BiometricProcessObserver";
    private BiometricCaptureService.BiometricCallback callback;
    
    public BiometricProcessObserver(BiometricCaptureService.BiometricCallback callback) {
        this.callback = callback;
    }
    
    public void onImageAcquired(byte[] imageData) {
        Log.d(TAG, "Image acquise: " + (imageData != null ? imageData.length : 0) + " bytes");
        // Optionnel: traiter l'image acquise
    }
    
    public void onCommand(int command) {
        Log.d(TAG, "Commande reçue: " + command);
        
        if (command == CallbackMask.MORPHO_CALLBACK_COMMAND_CMD.getValue()) {
            Log.d(TAG, "Commande de capture");
        } else if (command == CallbackMask.MORPHO_CALLBACK_IMAGE_CMD.getValue()) {
            Log.d(TAG, "Commande d'image");
        } else if (command == CallbackMask.MORPHO_CALLBACK_CODEQUALITY.getValue()) {
            Log.d(TAG, "Commande qualité code");
        } else if (command == CallbackMask.MORPHO_CALLBACK_DETECTQUALITY.getValue()) {
            Log.d(TAG, "Commande qualité détection");
        } else {
            Log.d(TAG, "Commande inconnue: " + command);
        }
    }
    
    public void onQuality(int quality) {
        Log.d(TAG, "Qualité: " + quality);
        
        if (quality < 50) {
            Log.w(TAG, "Qualité faible: " + quality);
        } else if (quality >= 80) {
            Log.d(TAG, "Qualité excellente: " + quality);
        } else {
            Log.d(TAG, "Qualité acceptable: " + quality);
        }
    }
    
    public void onDetectQuality(int detectQuality) {
        Log.d(TAG, "Qualité de détection: " + detectQuality);
        
        if (detectQuality < 30) {
            Log.w(TAG, "Détection faible: " + detectQuality);
        } else if (detectQuality >= 70) {
            Log.d(TAG, "Détection excellente: " + detectQuality);
        } else {
            Log.d(TAG, "Détection acceptable: " + detectQuality);
        }
    }
}
