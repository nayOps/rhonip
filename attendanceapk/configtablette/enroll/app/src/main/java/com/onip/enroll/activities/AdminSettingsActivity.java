package com.onip.enroll.activities;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import com.onip.enroll.R;
import com.onip.enroll.services.EmployeeDataService;
import com.onip.enroll.utils.ConfigManager;

/** Paramètres administrateur : serveur RH et rechargement des agents. */
public class AdminSettingsActivity extends Activity {

    private ConfigManager configManager;
    private EmployeeDataService employeeDataService;
    private EditText editBackendIp;
    private EditText editBackendPort;
    private TextView txtConnectionStatus;
    private Button btnSave;
    private Button btnReload;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_admin_settings);

        configManager = new ConfigManager(this);
        employeeDataService = new EmployeeDataService(this);
        editBackendIp = findViewById(R.id.edit_backend_ip_admin);
        editBackendPort = findViewById(R.id.edit_backend_port_admin);
        txtConnectionStatus = findViewById(R.id.txt_connection_status);
        btnSave = findViewById(R.id.btn_admin_save);
        btnReload = findViewById(R.id.btn_admin_reload);
        Button btnBack = findViewById(R.id.btn_admin_back);

        editBackendIp.setText(configManager.getBackendIp());
        editBackendPort.setText(configManager.getBackendPort());

        btnSave.setOnClickListener(v -> {
            if (saveConfig(true)) {
                testConnection(false);
            }
        });
        btnReload.setOnClickListener(v -> {
            if (saveConfig(true)) {
                testConnection(true);
            }
        });
        btnBack.setOnClickListener(v -> finish());
    }

    private boolean saveConfig(boolean silent) {
        String ip = editBackendIp.getText().toString().trim();
        String port = editBackendPort.getText().toString().trim();
        if (ip.isEmpty() || port.isEmpty()) {
            Toast.makeText(this, R.string.admin_fields_required, Toast.LENGTH_SHORT).show();
            return false;
        }
        configManager.setBackendConfig(ip, port);
        employeeDataService = new EmployeeDataService(this);
        if (!silent) {
            Toast.makeText(this, R.string.admin_saved, Toast.LENGTH_SHORT).show();
        }
        return true;
    }

    private void testConnection(boolean startReloadAfterSuccess) {
        setBusy(true);
        if (txtConnectionStatus != null) {
            txtConnectionStatus.setText(R.string.admin_testing_connection);
        }

        employeeDataService.testServerConnection(new EmployeeDataService.ConnectionCallback() {
            @Override
            public void onSuccess(int employeeCount, int enrolledCount) {
                runOnUiThread(() -> {
                    setBusy(false);
                    String message = getString(R.string.admin_connection_ok, enrolledCount, employeeCount);
                    if (txtConnectionStatus != null) {
                        txtConnectionStatus.setText(message);
                    }
                    Toast.makeText(AdminSettingsActivity.this, message, Toast.LENGTH_LONG).show();
                    if (startReloadAfterSuccess) {
                        startReload();
                    }
                });
            }

            @Override
            public void onError(String error) {
                runOnUiThread(() -> {
                    setBusy(false);
                    if (txtConnectionStatus != null) {
                        txtConnectionStatus.setText(R.string.admin_connection_failed);
                    }
                    Toast.makeText(
                            AdminSettingsActivity.this,
                            R.string.admin_connection_failed,
                            Toast.LENGTH_LONG
                    ).show();
                });
            }
        });
    }

    private void setBusy(boolean busy) {
        if (btnSave != null) {
            btnSave.setEnabled(!busy);
        }
        if (btnReload != null) {
            btnReload.setEnabled(!busy);
        }
    }

    private void startReload() {
        Toast.makeText(this, R.string.reload_started, Toast.LENGTH_SHORT).show();
        Intent intent = new Intent(this, LoadingActivity.class);
        intent.putExtra(LoadingActivity.EXTRA_FORCE_SYNC, true);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finish();
    }
}
