package com.onip.enroll.activities;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ListView;
import com.onip.enroll.EnrollApplication;
import com.onip.enroll.R;
import com.onip.enroll.models.Employee;
import com.onip.enroll.services.DeviceManager;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class EmployeeListActivity extends Activity {

    private List<Employee> allEmployees = new ArrayList<>();
    private List<Employee> filteredEmployees = new ArrayList<>();
    private ArrayAdapter<String> adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_employee_list);

        DeviceManager.rebindUsbHost(this);

        EnrollApplication app = (EnrollApplication) getApplication();
        allEmployees = new ArrayList<>(app.getGlobalEmployees());

        ListView listView = findViewById(R.id.list_employees);
        EditText search = findViewById(R.id.edit_search_employee);
        Button btnBack = findViewById(R.id.btn_back_employee_list);

        adapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, new ArrayList<>());
        listView.setAdapter(adapter);

        applyFilter("");

        search.addTextChangedListener(new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int before, int count) {
                applyFilter(s.toString());
            }
            @Override public void afterTextChanged(Editable s) {}
        });

        listView.setOnItemClickListener((parent, view, position, id) -> {
            if (position < 0 || position >= filteredEmployees.size()) {
                return;
            }
            Employee employee = filteredEmployees.get(position);
            if (employee.getNin() == null || employee.getNin().trim().isEmpty()) {
                new AlertDialog.Builder(this)
                        .setTitle("Matricule manquant")
                        .setMessage("Cet agent n'a pas de matricule RH. Complétez la fiche dans Register d'abord.")
                        .setPositiveButton("OK", null)
                        .show();
                return;
            }
            Intent intent = new Intent(this, FingerprintEnrollActivity.class);
            intent.putExtra("employee_id", employee.getId());
            intent.putExtra("employee_name", employee.getFullName());
            intent.putExtra("employee_nin", employee.getNin());
            startActivity(intent);
        });

        btnBack.setOnClickListener(v -> finish());

        com.onip.enroll.utils.SettingsLauncher.wire(this, R.id.btn_settings_employee_list);
    }

    private void applyFilter(String query) {
        filteredEmployees.clear();
        String q = query == null ? "" : query.trim().toLowerCase(Locale.getDefault());

        for (Employee employee : allEmployees) {
            String label = formatEmployee(employee).toLowerCase(Locale.getDefault());
            if (q.isEmpty() || label.contains(q)) {
                filteredEmployees.add(employee);
            }
        }

        List<String> labels = new ArrayList<>();
        for (Employee employee : filteredEmployees) {
            labels.add(formatEmployee(employee));
        }
        adapter.clear();
        adapter.addAll(labels);
        adapter.notifyDataSetChanged();
    }

    private String formatEmployee(Employee employee) {
        String matricule = employee.getNin() != null ? employee.getNin() : "—";
        String enrolled = employee.isBiometricEnrolled() ? " [empreintes]" : "";
        return employee.getFullName() + " · " + matricule + enrolled;
    }
}
