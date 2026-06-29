package com.onip.enroll.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import com.onip.enroll.models.Employee;
import com.onip.enroll.utils.ConfigManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/** Charge la liste des agents RH pour l'enrôlement. */
public class EmployeeDataService {

    private static final String TAG = "EmployeeDataService";

    public interface EmployeesCallback {
        void onSuccess(List<Employee> employees);
        void onError(String error);
    }

    private final ConfigManager configManager;

    public EmployeeDataService(Context context) {
        this.configManager = new ConfigManager(context);
    }

    public void loadEmployees(EmployeesCallback callback) {
        new LoadEmployeesTask(callback).execute();
    }

    private class LoadEmployeesTask extends AsyncTask<Void, Void, List<Employee>> {
        private final EmployeesCallback callback;
        private String errorMessage;

        LoadEmployeesTask(EmployeesCallback callback) {
            this.callback = callback;
        }

        @Override
        protected List<Employee> doInBackground(Void... voids) {
            try {
                String urlString = configManager.getBackendUrl("/api/data");
                HttpURLConnection connection = (HttpURLConnection) new URL(urlString).openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(15000);
                connection.setReadTimeout(15000);

                int responseCode = connection.getResponseCode();
                BufferedReader reader = new BufferedReader(new InputStreamReader(
                        responseCode >= 200 && responseCode < 300
                                ? connection.getInputStream()
                                : connection.getErrorStream()
                ));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                connection.disconnect();

                if (responseCode < 200 || responseCode >= 300) {
                    errorMessage = "HTTP " + responseCode;
                    return null;
                }

                JSONObject jsonObject = new JSONObject(response.toString());
                JSONArray dataArray = jsonObject.getJSONArray("data");
                List<Employee> employees = new ArrayList<>();
                for (int i = 0; i < dataArray.length(); i++) {
                    JSONObject empJson = dataArray.getJSONObject(i);
                    Employee employee = new Employee();
                    employee.setId(empJson.optInt("id", 0));
                    employee.setFirstName(empJson.optString("firstName", ""));
                    employee.setLastName(empJson.optString("lastName", ""));
                    employee.setMiddleName(empJson.optString("middleName", ""));
                    employee.setNin(empJson.optString("nin", ""));
                    employee.setBiometricEnrolled(empJson.optBoolean("biometricEnrolled", false));
                    employees.add(employee);
                }
                Log.d(TAG, employees.size() + " employé(s) chargé(s)");
                return employees;
            } catch (Exception e) {
                errorMessage = e.getMessage();
                return null;
            }
        }

        @Override
        protected void onPostExecute(List<Employee> employees) {
            if (callback == null) {
                return;
            }
            if (employees != null && !employees.isEmpty()) {
                callback.onSuccess(employees);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Liste agents vide");
            }
        }
    }
}
