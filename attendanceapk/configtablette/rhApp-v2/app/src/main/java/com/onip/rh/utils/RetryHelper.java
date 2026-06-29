package com.onip.rh.utils;

import android.util.Log;
import java.util.concurrent.Callable;

/**
 * Helper pour gérer les retry automatiques avec backoff exponentiel
 */
public class RetryHelper {
    
    private static final String TAG = "RetryHelper";
    
    /**
     * Exécute une opération avec retry automatique
     * @param operation L'opération à exécuter (retourne true si succès)
     * @param maxRetries Nombre maximum de tentatives
     * @param initialDelayMs Délai initial en millisecondes
     * @return true si succès, false si échec après toutes les tentatives
     */
    public static boolean executeWithRetry(Callable<Boolean> operation, int maxRetries, long initialDelayMs) {
        int attempt = 0;
        long delay = initialDelayMs;
        
        while (attempt < maxRetries) {
            try {
                Log.d(TAG, "Tentative " + (attempt + 1) + "/" + maxRetries);
                Boolean result = operation.call();
                
                if (result != null && result) {
                    Log.d(TAG, "✅ Succès à la tentative " + (attempt + 1));
                    return true;
                }
                
                // Échec - attendre avant de réessayer
                if (attempt < maxRetries - 1) {
                    Log.d(TAG, "⏳ Attente de " + delay + "ms avant retry...");
                    Thread.sleep(delay);
                    delay *= 2; // Backoff exponentiel
                }
                
                attempt++;
                
            } catch (Exception e) {
                Log.e(TAG, "❌ Erreur tentative " + (attempt + 1) + ": " + e.getMessage());
                
                if (attempt < maxRetries - 1) {
                    try {
                        Thread.sleep(delay);
                        delay *= 2;
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        return false;
                    }
                }
                attempt++;
            }
        }
        
        Log.e(TAG, "❌ Échec après " + maxRetries + " tentatives");
        return false;
    }
    
    /**
     * Version simplifiée avec paramètres par défaut
     */
    public static boolean executeWithRetry(Callable<Boolean> operation) {
        return executeWithRetry(operation, 3, 1000); // 3 tentatives, 1s initial
    }
}

