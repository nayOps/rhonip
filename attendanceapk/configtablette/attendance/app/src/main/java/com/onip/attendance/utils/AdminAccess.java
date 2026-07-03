package com.onip.attendance.utils;

import android.app.Activity;
import android.app.AlertDialog;
import android.text.InputType;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;
import com.onip.attendance.R;

/**
 * Vérifie le matricule administrateur avant l'accès aux paramètres.
 */
public final class AdminAccess {

    private AdminAccess() {
    }

    public static void prompt(Activity activity, Runnable onGranted) {
        if (activity == null || activity.isFinishing()) {
            return;
        }

        View view = LayoutInflater.from(activity).inflate(R.layout.dialog_admin_auth, null);
        EditText editCode = view.findViewById(R.id.edit_admin_code);

        AlertDialog dialog = new AlertDialog.Builder(activity)
                .setTitle(R.string.admin_auth_title)
                .setView(view)
                .setPositiveButton(R.string.admin_auth_confirm, null)
                .setNegativeButton(R.string.cancel, (d, w) -> d.dismiss())
                .create();

        dialog.setOnShowListener(d -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(v -> {
            String code = editCode.getText().toString().trim();
            if (ConfigManager.isAdminCode(code)) {
                dialog.dismiss();
                if (onGranted != null) {
                    onGranted.run();
                }
            } else {
                Toast.makeText(activity, R.string.admin_auth_denied, Toast.LENGTH_SHORT).show();
            }
        }));

        dialog.show();
        if (editCode != null) {
            editCode.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_CHARACTERS);
            editCode.requestFocus();
        }
    }
}
