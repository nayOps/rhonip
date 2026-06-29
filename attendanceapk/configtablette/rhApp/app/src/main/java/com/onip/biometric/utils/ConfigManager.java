package com.onip.biometric.utils;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

/**
 * Gestionnaire de configuration pour l'application
 * Stocke l'IP et le port du backend dans SharedPreferences
 */
public class ConfigManager {
    
    private static final String TAG = "ConfigManager";
    private static final String PREFS_NAME = "rh_app_config";
    
    // Clés pour SharedPreferences
    private static final String KEY_BACKEND_IP = "backend_ip";
    private static final String KEY_BACKEND_PORT = "backend_port";
    
    // Valeurs par défaut
    private static final String DEFAULT_IP = "192.168.1.73";
    private static final String DEFAULT_PORT = "8083";
    
    private SharedPreferences prefs;
    private Context context;
    
    public ConfigManager(Context context) {
        this.context = context;
        this.prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }
    
    /**
     * Récupère l'IP du backend
     */
    public String getBackendIp() {
        return prefs.getString(KEY_BACKEND_IP, DEFAULT_IP);
    }
    
    /**
     * Récupère le port du backend
     */
    public String getBackendPort() {
        return prefs.getString(KEY_BACKEND_PORT, DEFAULT_PORT);
    }
    
    /**
     * Construit l'URL complète du backend
     */
    public String getBackendUrl() {
        String ip = getBackendIp();
        String port = getBackendPort();
        String url = "http://" + ip + ":" + port + "/api/test";
        Log.d(TAG, "URL backend: " + url);
        return url;
    }
    
    /**
     * Sauvegarde l'IP du backend
     */
    public void setBackendIp(String ip) {
        prefs.edit().putString(KEY_BACKEND_IP, ip).apply();
        Log.d(TAG, "IP sauvegardée: " + ip);
    }
    
    /**
     * Sauvegarde le port du backend
     */
    public void setBackendPort(String port) {
        prefs.edit().putString(KEY_BACKEND_PORT, port).apply();
        Log.d(TAG, "Port sauvegardé: " + port);
    }
    
    /**
     * Sauvegarde l'IP et le port en une seule fois
     */
    public void setBackendConfig(String ip, String port) {
        prefs.edit()
            .putString(KEY_BACKEND_IP, ip)
            .putString(KEY_BACKEND_PORT, port)
            .apply();
        Log.d(TAG, "Configuration sauvegardée: " + ip + ":" + port);
    }
    
    /**
     * Réinitialise la configuration aux valeurs par défaut
     */
    public void resetToDefault() {
        setBackendConfig(DEFAULT_IP, DEFAULT_PORT);
    }
    
    /**
     * Vérifie si la configuration a été modifiée
     */
    public boolean isDefaultConfig() {
        return getBackendIp().equals(DEFAULT_IP) && getBackendPort().equals(DEFAULT_PORT);
    }
}

