package com.onip.biometric.utils;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;

/**
 * Configuration backend RH (IP, port, clé guichet).
 */
public class ConfigManager {

    private static final String TAG = "ConfigManager";
    private static final String PREFS_NAME = "onip_biometric_config";

    private static final String KEY_BACKEND_IP = "backend_ip";
    private static final String KEY_BACKEND_PORT = "backend_port";
    private static final String KEY_GUICHET_KEY = "guichet_key";

    private static final String DEFAULT_IP = "102.68.62.85";
    private static final String DEFAULT_PORT = "8100";
    private static final String DEFAULT_GUICHET_KEY = "fgp_guichet_internal_dev";

    private final SharedPreferences prefs;

    public ConfigManager(Context context) {
        prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE);
    }

    public String getBackendIp() {
        return prefs.getString(KEY_BACKEND_IP, DEFAULT_IP);
    }

    public String getBackendPort() {
        return prefs.getString(KEY_BACKEND_PORT, DEFAULT_PORT);
    }

    public String getGuichetKey() {
        return prefs.getString(KEY_GUICHET_KEY, DEFAULT_GUICHET_KEY);
    }

    public String getBackendBaseUrl() {
        String url = "http://" + getBackendIp() + ":" + getBackendPort();
        Log.d(TAG, "URL backend: " + url);
        return url;
    }

    public String getGuichetUpsertUrl() {
        return getBackendBaseUrl() + "/api/guichet/employee/upsert/";
    }

    public void setBackendConfig(String ip, String port) {
        prefs.edit()
                .putString(KEY_BACKEND_IP, ip)
                .putString(KEY_BACKEND_PORT, port)
                .apply();
    }
}
