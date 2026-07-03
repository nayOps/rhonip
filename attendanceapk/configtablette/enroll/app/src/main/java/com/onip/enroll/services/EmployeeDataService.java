package com.onip.enroll.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import com.onip.enroll.models.Employee;
import com.onip.enroll.storage.LocalEmployeeStore;
import com.onip.enroll.utils.ConfigManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/** Charge la liste des agents RH (serveur + cache SQLite). */
public class EmployeeDataService {

    private static final String TAG = "EmployeeDataService";
    private static final int MAX_RETRIES = 3;
    private static final int CONNECT_TIMEOUT_MS = 15000;
    private static final int READ_TIMEOUT_MS = 30000;

    public interface EmployeesCallback {
        void onSuccess(List<Employee> employees, boolean fromCache);
        void onError(String error);
    }

    public interface ConnectionCallback {
        void onSuccess(int employeeCount, int enrolledCount);
        void onError(String error);
    }

    private final ConfigManager configManager;
    private final LocalEmployeeStore employeeStore;

    public EmployeeDataService(Context context) {
        this.configManager = new ConfigManager(context);
        this.employeeStore = new LocalEmployeeStore(context);
    }

    public LocalEmployeeStore getEmployeeStore() {
        return employeeStore;
    }

    public void loadEmployees(EmployeesCallback callback) {
        loadEmployees(false, callback);
    }

    public void loadEmployees(boolean forceFullSync, EmployeesCallback callback) {
        new LoadEmployeesTask(forceFullSync, callback).execute();
    }

    public void loadFromCache(EmployeesCallback callback) {
        new LoadCacheTask(callback).execute();
    }

    public void testServerConnection(ConnectionCallback callback) {
        new TestConnectionTask(callback).execute();
    }

    private class LoadCacheTask extends AsyncTask<Void, Void, List<Employee>> {
        private final EmployeesCallback callback;

        LoadCacheTask(EmployeesCallback callback) {
            this.callback = callback;
        }

        @Override
        protected List<Employee> doInBackground(Void... voids) {
            if (!employeeStore.hasData()) {
                return null;
            }
            return employeeStore.loadEmployees();
        }

        @Override
        protected void onPostExecute(List<Employee> employees) {
            if (callback == null) {
                return;
            }
            if (employees != null && !employees.isEmpty()) {
                callback.onSuccess(employees, true);
            } else {
                callback.onError("Aucune donnée locale");
            }
        }
    }

    private class TestConnectionTask extends AsyncTask<Void, Void, List<Employee>> {
        private final ConnectionCallback callback;
        private String errorMessage;

        TestConnectionTask(ConnectionCallback callback) {
            this.callback = callback;
        }

        @Override
        protected List<Employee> doInBackground(Void... voids) {
            try {
                return fetchEmployees();
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
                int enrolled = 0;
                for (Employee employee : employees) {
                    if (employee.isBiometricEnrolled()) {
                        enrolled++;
                    }
                }
                callback.onSuccess(employees.size(), enrolled);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Connexion impossible");
            }
        }
    }

    private class LoadEmployeesTask extends AsyncTask<Void, Void, LoadResult> {
        private final EmployeesCallback callback;
        private final boolean forceFullSync;
        private String errorMessage;

        LoadEmployeesTask(boolean forceFullSync, EmployeesCallback callback) {
            this.forceFullSync = forceFullSync;
            this.callback = callback;
        }

        @Override
        protected LoadResult doInBackground(Void... voids) {
            int retry = 0;
            while (retry < MAX_RETRIES) {
                try {
                    List<Employee> remote = fetchEmployees();
                    if (remote != null && !remote.isEmpty()) {
                        if (forceFullSync) {
                            employeeStore.clearAll();
                        }
                        employeeStore.replaceAll(remote);
                        return new LoadResult(employeeStore.loadEmployees(), false);
                    }
                    if (remote != null) {
                        errorMessage = "Liste agents vide";
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Erreur chargement tentative " + (retry + 1) + ": " + e.getMessage());
                    errorMessage = e.getMessage();
                }
                retry++;
            }

            if (!forceFullSync && employeeStore.hasData()) {
                Log.w(TAG, "Utilisation du cache local (réseau indisponible)");
                return new LoadResult(employeeStore.loadEmployees(), true);
            }
            return null;
        }

        @Override
        protected void onPostExecute(LoadResult result) {
            if (callback == null) {
                return;
            }
            if (result != null && result.employees != null && !result.employees.isEmpty()) {
                callback.onSuccess(result.employees, result.fromCache);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Impossible de charger les agents");
            }
        }
    }

    private List<Employee> fetchEmployees() throws Exception {
        String urlString = configManager.getBackendUrl("/api/data");
        Log.d(TAG, "Chargement agents: " + urlString);

        HttpURLConnection connection = (HttpURLConnection) new URL(urlString).openConnection();
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
        connection.setReadTimeout(READ_TIMEOUT_MS);

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
            throw new Exception("HTTP " + responseCode);
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
            if (employee.getId() > 0) {
                employees.add(employee);
            }
        }
        Log.d(TAG, employees.size() + " employé(s) reçu(s)");
        return employees;
    }

    private static class LoadResult {
        final List<Employee> employees;
        final boolean fromCache;

        LoadResult(List<Employee> employees, boolean fromCache) {
            this.employees = employees;
            this.fromCache = fromCache;
        }
    }
}
