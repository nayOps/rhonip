package com.onip.enroll.utils;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

/**
 * Gestionnaire de configuration pour l'application
 * Stocke l'IP et le port du backend dans SharedPreferences
 * Version améliorée avec gestion d'erreurs
 */
public class ConfigManager {
    
    private static final String TAG = "ConfigManager";
    private static final String PREFS_NAME = "rh_app_v2_config";
    
    // Clés pour SharedPreferences
    private static final String KEY_BACKEND_IP = "backend_ip";
    private static final String KEY_BACKEND_PORT = "backend_port";
    
    // Serveur RH production VPS
    private static final String DEFAULT_IP = "102.68.62.85";
    private static final String DEFAULT_PORT = "8100";
    
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
     * Construit l'URL de base du backend (sans endpoint)
     */
    public String getBackendBaseUrl() {
        String ip = getBackendIp();
        String port = getBackendPort();
        String url = "http://" + ip + ":" + port;
        Log.d(TAG, "URL backend base: " + url);
        return url;
    }
    
    /**
     * Construit l'URL complète pour un endpoint
     */
    public String getBackendUrl(String endpoint) {
        String baseUrl = getBackendBaseUrl();
        if (!endpoint.startsWith("/")) {
            baseUrl += "/";
        }
        return baseUrl + endpoint;
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

