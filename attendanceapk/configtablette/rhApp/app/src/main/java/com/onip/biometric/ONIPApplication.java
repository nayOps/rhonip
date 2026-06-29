package com.onip.biometric;

import android.app.Application;
import android.util.Log;
import com.onip.biometric.models.Employee;
import com.morpho.morphosmart.sdk.MorphoDevice;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Application class pour l'application ONIP RH
 * Stocke les données globales chargées au démarrage
 */
public class ONIPApplication extends Application {
    
    private static final String TAG = "ONIPApplication";
    
    // Instance singleton
    private static ONIPApplication instance;
    
    // Données globales
    private List<Employee> globalEmployees = new ArrayList<>();
    private Map<Integer, Map<String, byte[]>> globalTemplates = new HashMap<>();
    private MorphoDevice globalMorphoDevice = null;
    private boolean dataLoaded = false;
    private boolean deviceInitialized = false;
    
    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;
        Log.d(TAG, "ONIPApplication onCreate() - Application ONIP RH démarrée");
    }
    
    public static ONIPApplication getInstance() {
        return instance;
    }
    
    // Getters et Setters pour les données globales
    public List<Employee> getGlobalEmployees() {
        return globalEmployees;
    }
    
    public void setGlobalEmployees(List<Employee> employees) {
        this.globalEmployees = employees;
        Log.d(TAG, "✅ " + employees.size() + " employé(s) stocké(s) globalement");
    }
    
    public Map<Integer, Map<String, byte[]>> getGlobalTemplates() {
        return globalTemplates;
    }
    
    public void setGlobalTemplates(Map<Integer, Map<String, byte[]>> templates) {
        this.globalTemplates = templates;
        int totalTemplates = 0;
        for (Map<String, byte[]> empTemplates : templates.values()) {
            totalTemplates += empTemplates.size();
        }
        Log.d(TAG, "✅ " + totalTemplates + " template(s) stocké(s) globalement");
    }
    
    public MorphoDevice getGlobalMorphoDevice() {
        return globalMorphoDevice;
    }
    
    public void setGlobalMorphoDevice(MorphoDevice device) {
        this.globalMorphoDevice = device;
        Log.d(TAG, "✅ MorphoDevice stocké globalement");
    }
    
    public boolean isDataLoaded() {
        return dataLoaded;
    }
    
    public void setDataLoaded(boolean loaded) {
        this.dataLoaded = loaded;
        Log.d(TAG, "✅ Données chargées: " + loaded);
    }
    
    public boolean isDeviceInitialized() {
        return deviceInitialized;
    }
    
    public void setDeviceInitialized(boolean initialized) {
        this.deviceInitialized = initialized;
        Log.d(TAG, "✅ Device initialisé: " + initialized);
    }
    
    public void clearGlobalData() {
        globalEmployees.clear();
        globalTemplates.clear();
        globalMorphoDevice = null;
        dataLoaded = false;
        deviceInitialized = false;
        Log.d(TAG, "🗑️ Données globales effacées");
    }
}
