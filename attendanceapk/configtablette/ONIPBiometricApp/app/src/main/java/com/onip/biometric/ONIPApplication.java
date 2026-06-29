package com.onip.biometric;

import android.app.Application;
import android.util.Log;

/**
 * Application class pour l'application ONIP RH
 */
public class ONIPApplication extends Application {
    
    private static final String TAG = "ONIPApplication";
    
    @Override
    public void onCreate() {
        super.onCreate();
        
        Log.d(TAG, "ONIPApplication onCreate() - Application ONIP RH démarrée");
    }
}
