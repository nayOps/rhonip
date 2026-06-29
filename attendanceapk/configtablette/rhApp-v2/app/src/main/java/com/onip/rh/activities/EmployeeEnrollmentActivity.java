package com.onip.rh.activities;

import android.app.Activity;
import android.content.pm.ActivityInfo;
import android.os.Bundle;
import android.util.Log;
import com.onip.rh.R;

/**
 * Activité d'enregistrement d'employé (3 étapes)
 * TODO: Implémenter le formulaire complet
 */
public class EmployeeEnrollmentActivity extends Activity {
    
    private static final String TAG = "EmployeeEnrollmentActivity";
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_PORTRAIT);
        
        // TODO: Créer le layout et implémenter le formulaire
        Log.d(TAG, "EmployeeEnrollmentActivity - À implémenter");
        
        // Pour l'instant, juste finir l'activité
        finish();
    }
}


