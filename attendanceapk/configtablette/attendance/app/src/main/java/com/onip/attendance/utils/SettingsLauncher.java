package com.onip.attendance.utils;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageButton;
import com.onip.attendance.R;
import com.onip.attendance.activities.AdminSettingsActivity;
import com.onip.attendance.utils.AdminAccess;

/**
 * Ouvre les paramètres après vérification du matricule administrateur.
 */
public final class SettingsLauncher {

    private SettingsLauncher() {
    }

    public static void wire(Activity activity, int buttonId) {
        ImageButton button = activity.findViewById(buttonId);
        if (button == null) {
            return;
        }
        button.setOnClickListener(v -> openAdmin(activity));
    }

    public static void openAdmin(Activity activity) {
        AdminAccess.prompt(activity, () -> {
            Intent intent = new Intent(activity, AdminSettingsActivity.class);
            activity.startActivity(intent);
        });
    }
}
