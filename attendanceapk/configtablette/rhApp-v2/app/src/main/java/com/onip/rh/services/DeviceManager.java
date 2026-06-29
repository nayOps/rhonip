package com.onip.rh.services;

import android.app.Activity;
import android.util.Log;
import com.morpho.android.usb.USBManager;
import com.morpho.morphosmart.sdk.ErrorCodes;
import com.morpho.morphosmart.sdk.MorphoDevice;
import com.onip.rh.utils.RetryHelper;
import java.util.concurrent.Callable;

/**
 * Gestionnaire du périphérique MorphoDevice
 * Version améliorée avec retry automatique et gestion d'erreurs robuste
 */
public class DeviceManager {
    
    private static final String TAG = "DeviceManager";
    private static final String USB_ACTION = "com.onip.rh.USB_ACTION";
    private static final int MAX_RETRIES = 3;
    private static final long INITIAL_DELAY_MS = 1000;
    
    private Activity activity;
    private MorphoDevice morphoDevice;
    private boolean initialized = false;
    
    public interface DeviceCallback {
        void onSuccess(MorphoDevice device);
        void onError(String error);
    }
    
    public DeviceManager(Activity activity) {
        this.activity = activity;
    }
    
    /**
     * Initialise le MorphoDevice avec retry automatique
     */
    public void initializeDevice(DeviceCallback callback) {
        new Thread(() -> {
            Log.d(TAG, "=== INITIALISATION MORPHODEVICE ===");
            
            boolean success = RetryHelper.executeWithRetry(new Callable<Boolean>() {
                @Override
                public Boolean call() throws Exception {
                    return initializeDeviceInternal();
                }
            }, MAX_RETRIES, INITIAL_DELAY_MS);
            
            if (success && morphoDevice != null) {
                initialized = true;
                activity.runOnUiThread(() -> {
                    callback.onSuccess(morphoDevice);
                });
            } else {
                initialized = false;
                activity.runOnUiThread(() -> {
                    callback.onError("Impossible d'initialiser le capteur après " + MAX_RETRIES + " tentatives");
                });
            }
        }).start();
    }
    
    /**
     * Initialisation interne (appelée par retry)
     */
    private boolean initializeDeviceInternal() {
        try {
            Log.d(TAG, "Tentative d'initialisation...");
            
            // ÉTAPE 1: Initialiser USBManager (OBLIGATOIRE)
            USBManager.getInstance().initialize(activity, USB_ACTION, true);
            Log.d(TAG, "✅ USBManager initialisé");
            
            // ÉTAPE 2: Créer MorphoDevice
            morphoDevice = new MorphoDevice();
            Log.d(TAG, "✅ MorphoDevice créé");
            
            // ÉTAPE 3: Énumérer les périphériques USB
            Integer nbUsbDevice = new Integer(0);
            int ret = morphoDevice.initUsbDevicesNameEnum(nbUsbDevice);
            Log.d(TAG, "Énumération USB: " + ret + ", nbDevices: " + nbUsbDevice);
            
            if (ret != ErrorCodes.MORPHO_OK) {
                Log.e(TAG, "❌ Erreur énumération USB: " + ret);
                return false;
            }
            
            if (nbUsbDevice != 1) {
                Log.w(TAG, "⚠️ Nombre de périphériques incorrect: " + nbUsbDevice + " (attendu: 1)");
                return false;
            }
            
            // ÉTAPE 4: Ouvrir le périphérique
            String sensorName = morphoDevice.getUsbDeviceName(0);
            Log.d(TAG, "Nom du capteur: " + sensorName);
            
            int openResult = morphoDevice.openUsbDevice(sensorName, 0);
            Log.d(TAG, "Résultat ouverture: " + openResult);
            
            if (openResult == ErrorCodes.MORPHO_OK) {
                Log.d(TAG, "✅ MorphoDevice initialisé avec succès");
                return true;
            } else {
                Log.e(TAG, "❌ Erreur ouverture périphérique: " + openResult);
                return false;
            }
            
        } catch (Exception e) {
            Log.e(TAG, "❌ Exception lors de l'initialisation: " + e.getMessage(), e);
            return false;
        }
    }
    
    /**
     * Vérifie si le device est initialisé
     */
    public boolean isInitialized() {
        return initialized && morphoDevice != null;
    }
    
    /**
     * Récupère le MorphoDevice (peut être null)
     */
    public MorphoDevice getDevice() {
        return morphoDevice;
    }
    
    /**
     * Ferme le périphérique
     */
    public void close() {
        if (morphoDevice != null) {
            try {
                // Le MorphoDevice se ferme automatiquement ou via USBManager
                // Pas de méthode closeUsbDevice() dans le SDK
                Log.d(TAG, "✅ MorphoDevice marqué comme fermé");
            } catch (Exception e) {
                Log.e(TAG, "❌ Erreur lors de la fermeture: " + e.getMessage());
            }
            morphoDevice = null;
            initialized = false;
        }
    }
    
    /**
     * Vérifie la connexion du périphérique
     */
    public boolean checkConnection() {
        if (morphoDevice == null) {
            return false;
        }
        
        try {
            Integer nbUsbDevice = new Integer(0);
            int ret = morphoDevice.initUsbDevicesNameEnum(nbUsbDevice);
            return ret == ErrorCodes.MORPHO_OK && nbUsbDevice == 1;
        } catch (Exception e) {
            Log.e(TAG, "Erreur vérification connexion: " + e.getMessage());
            return false;
        }
    }
}

