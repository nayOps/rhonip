package com.onip.rh;

import android.app.Application;
import android.util.Log;
import com.onip.rh.models.Employee;
import com.morpho.morphosmart.sdk.MorphoDevice;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Application class pour l'application RH V2
 * Stocke les données globales chargées au démarrage
 * Version améliorée avec gestion d'état robuste
 */
public class RHApplication extends Application {
    
    private static final String TAG = "RHApplication";
    
    // Instance singleton
    private static RHApplication instance;
    
    // Données globales
    private List<Employee> globalEmployees = new ArrayList<>();
    private Map<Integer, Map<String, byte[]>> globalTemplates = new HashMap<>();
    private MorphoDevice globalMorphoDevice = null;
    
    // États
    private boolean dataLoaded = false;
    private boolean deviceInitialized = false;
    private boolean isLoading = false;
    
    // Timestamps pour cache
    private long lastDataLoadTime = 0;
    private static final long CACHE_VALIDITY_MS = 5 * 60 * 1000; // 5 minutes
    
    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        Log.d(TAG, "RHApplication onCreate() - Application RH V2 démarrée");
    }
    
    public static RHApplication getInstance() {
        return instance;
    }
    
    // ========== Getters et Setters pour les données globales ==========
    
    public List<Employee> getGlobalEmployees() {
        return globalEmployees;
    }
    
    public void setGlobalEmployees(List<Employee> employees) {
        this.globalEmployees = employees != null ? employees : new ArrayList<>();
        this.dataLoaded = true;
        this.lastDataLoadTime = System.currentTimeMillis();
        Log.d(TAG, "✅ " + this.globalEmployees.size() + " employé(s) stocké(s) globalement");
    }
    
    public Map<Integer, Map<String, byte[]>> getGlobalTemplates() {
        return globalTemplates;
    }
    
    public void setGlobalTemplates(Map<Integer, Map<String, byte[]>> templates) {
        this.globalTemplates = templates != null ? templates : new HashMap<>();
        int totalTemplates = 0;
        for (Map<String, byte[]> empTemplates : this.globalTemplates.values()) {
            totalTemplates += empTemplates.size();
        }
        Log.d(TAG, "✅ " + totalTemplates + " template(s) stocké(s) globalement");
    }
    
    public MorphoDevice getGlobalMorphoDevice() {
        return globalMorphoDevice;
    }
    
    public void setGlobalMorphoDevice(MorphoDevice device) {
        this.globalMorphoDevice = device;
        this.deviceInitialized = (device != null);
        Log.d(TAG, "✅ MorphoDevice " + (device != null ? "stocké" : "effacé") + " globalement");
    }
    
    // ========== Gestion des états ==========
    
    public boolean isDataLoaded() {
        return dataLoaded && !isDataExpired();
    }
    
    public void setDataLoaded(boolean loaded) {
        this.dataLoaded = loaded;
        if (loaded) {
            this.lastDataLoadTime = System.currentTimeMillis();
        }
        Log.d(TAG, "✅ Données chargées: " + loaded);
    }
    
    public boolean isDeviceInitialized() {
        return deviceInitialized && globalMorphoDevice != null;
    }
    
    public void setDeviceInitialized(boolean initialized) {
        this.deviceInitialized = initialized;
        Log.d(TAG, "✅ Device initialisé: " + initialized);
    }
    
    public boolean isLoading() {
        return isLoading;
    }
    
    public void setLoading(boolean loading) {
        this.isLoading = loading;
        Log.d(TAG, "⏳ Chargement: " + loading);
    }
    
    // ========== Vérification cache ==========
    
    private boolean isDataExpired() {
        if (lastDataLoadTime == 0) {
            return true;
        }
        long elapsed = System.currentTimeMillis() - lastDataLoadTime;
        return elapsed > CACHE_VALIDITY_MS;
    }
    
    public boolean needsDataRefresh() {
        return !dataLoaded || isDataExpired();
    }
    
    // ========== Utilitaires ==========
    
    public void clearGlobalData() {
        globalEmployees.clear();
        globalTemplates.clear();
        globalMorphoDevice = null;
        dataLoaded = false;
        deviceInitialized = false;
        lastDataLoadTime = 0;
        Log.d(TAG, "🗑️ Données globales effacées");
    }
    
    /**
     * Vérifie si l'application est prête (device + données)
     */
    public boolean isReady() {
        return isDeviceInitialized() && isDataLoaded();
    }
    
    /**
     * Obtient le statut de l'application
     */
    public String getStatus() {
        StringBuilder status = new StringBuilder();
        status.append("Device: ").append(isDeviceInitialized() ? "✅" : "❌");
        status.append(" | Data: ").append(isDataLoaded() ? "✅" : "❌");
        status.append(" | Employees: ").append(globalEmployees.size());
        return status.toString();
    }
}

