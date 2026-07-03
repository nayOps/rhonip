package com.onip.attendance.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import com.onip.attendance.models.Employee;
import com.onip.attendance.storage.LocalTemplateStore;
import com.onip.attendance.utils.ConfigManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Chargement des données pointage via bundle RH + cache SQLite local.
 */
public class DataManager {

    private static final String TAG = "DataManager";
    private static final int MAX_RETRIES = 3;
    private static final int CONNECT_TIMEOUT_MS = 15000;
    private static final int READ_TIMEOUT_MS = 30000;

    private final Context context;
    private final ConfigManager configManager;
    private final LocalTemplateStore templateStore;

    public interface AllDataCallback {
        void onSuccess(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates, boolean fromCache);
        void onError(String error);
    }

    public DataManager(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
        this.templateStore = new LocalTemplateStore(context);
    }

    public LocalTemplateStore getTemplateStore() {
        return templateStore;
    }

    public void loadAllData(AllDataCallback callback) {
        loadAllData(false, callback);
    }

    public void loadAllData(boolean forceFullSync, AllDataCallback callback) {
        new LoadAllDataTask(forceFullSync, callback).execute();
    }

    public void loadFromCache(AllDataCallback callback) {
        new LoadCacheTask(callback).execute();
    }

    public interface ConnectionCallback {
        void onSuccess(int enrolledCount, int employeeCount);
        void onError(String error);
    }

    public void testServerConnection(ConnectionCallback callback) {
        new TestConnectionTask(callback).execute();
    }

    private class TestConnectionTask extends AsyncTask<Void, Void, BundleLoadResult> {
        private final ConnectionCallback callback;
        private String errorMessage;

        TestConnectionTask(ConnectionCallback callback) {
            this.callback = callback;
        }

        @Override
        protected BundleLoadResult doInBackground(Void... voids) {
            try {
                return fetchBundle();
            } catch (Exception e) {
                errorMessage = e.getMessage();
                return null;
            }
        }

        @Override
        protected void onPostExecute(BundleLoadResult result) {
            if (callback == null) {
                return;
            }
            if (result != null) {
                callback.onSuccess(result.templates.size(), result.employees.size());
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Connexion impossible");
            }
        }
    }

    private class LoadCacheTask extends AsyncTask<Void, Void, BundleLoadResult> {
        private final AllDataCallback callback;

        LoadCacheTask(AllDataCallback callback) {
            this.callback = callback;
        }

        @Override
        protected BundleLoadResult doInBackground(Void... voids) {
            if (!templateStore.hasData()) {
                return null;
            }
            return new BundleLoadResult(
                    templateStore.loadEmployees(),
                    templateStore.loadTemplates(),
                    true
            );
        }

        @Override
        protected void onPostExecute(BundleLoadResult result) {
            if (callback == null) {
                return;
            }
            if (result != null && !result.templates.isEmpty()) {
                callback.onSuccess(result.employees, result.templates, true);
            } else {
                callback.onError("Aucune donnée locale");
            }
        }
    }

    private class LoadAllDataTask extends AsyncTask<Void, Void, BundleLoadResult> {
        private final AllDataCallback callback;
        private final boolean forceFullSync;
        private String errorMessage;

        LoadAllDataTask(boolean forceFullSync, AllDataCallback callback) {
            this.forceFullSync = forceFullSync;
            this.callback = callback;
        }

        @Override
        protected BundleLoadResult doInBackground(Void... voids) {
            int retry = 0;
            while (retry < MAX_RETRIES) {
                try {
                    BundleLoadResult remote = fetchBundle();
                    if (remote != null && !remote.templates.isEmpty()) {
                        if (forceFullSync) {
                            templateStore.clearAll();
                        }
                        templateStore.replaceAll(remote.employees, remote.templates);
                        if (remote.version != null && !remote.version.isEmpty()) {
                            templateStore.setSyncVersion(remote.version);
                        }
                        return new BundleLoadResult(
                                templateStore.loadEmployees(),
                                templateStore.loadTemplates(),
                                false
                        );
                    }
                    if (remote != null && remote.templates.isEmpty()) {
                        errorMessage = "Aucune empreinte reçue du serveur";
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Erreur bundle tentative " + (retry + 1) + ": " + e.getMessage());
                    errorMessage = e.getMessage();
                }
                retry++;
            }

            if (!forceFullSync && templateStore.hasData()) {
                Log.w(TAG, "Utilisation du cache local (réseau indisponible)");
                return new BundleLoadResult(
                        templateStore.loadEmployees(),
                        templateStore.loadTemplates(),
                        true
                );
            }
            return null;
        }

        @Override
        protected void onPostExecute(BundleLoadResult result) {
            if (callback == null) {
                return;
            }
            if (result != null && !result.templates.isEmpty()) {
                callback.onSuccess(result.employees, result.templates, result.fromCache);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Impossible de charger les empreintes");
            }
        }
    }

    private BundleLoadResult fetchBundle() throws Exception {
        String urlString = configManager.getBackendUrl("/api/fingerprints/bundle");
        Log.d(TAG, "Chargement bundle complet: " + urlString);

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
            throw new Exception("HTTP " + responseCode + ": " + response);
        }

        JSONObject json = new JSONObject(response.toString());
        if (!"success".equals(json.optString("status"))) {
            throw new Exception(json.optString("message", "Bundle invalide"));
        }

        BundleLoadResult result = new BundleLoadResult();
        result.status = json.optString("status", "");
        result.version = json.optString("version", null);

        JSONArray employeesJson = json.optJSONArray("employees");
        if (employeesJson == null) {
            return result;
        }

        for (int i = 0; i < employeesJson.length(); i++) {
            JSONObject empJson = employeesJson.getJSONObject(i);
            int employeeId = empJson.optInt("employeeId", 0);
            if (employeeId <= 0) {
                continue;
            }

            Map<String, byte[]> fingers = new HashMap<>();
            JSONArray fingersJson = empJson.optJSONArray("fingers");
            if (fingersJson != null) {
                for (int j = 0; j < fingersJson.length(); j++) {
                    JSONObject fingerJson = fingersJson.getJSONObject(j);
                    String fingerName = fingerJson.optString("fingerName", "");
                    String templateB64 = fingerJson.optString("template_base64", "");
                    byte[] data = LocalTemplateStore.decodeTemplate(templateB64);
                    if (fingerName.isEmpty() || data == null) {
                        continue;
                    }
                    fingers.put(fingerName, data);
                }
            }
            Employee employee = new Employee();
            employee.setId(employeeId);
            employee.setFirstName(empJson.optString("firstName", ""));
            employee.setLastName(empJson.optString("lastName", ""));
            employee.setMiddleName(empJson.optString("middleName", ""));
            employee.setNin(empJson.optString("registrationNumber", ""));
            employee.setBiometricEnrolled(!fingers.isEmpty());
            result.employees.add(employee);
            if (!fingers.isEmpty()) {
                result.templates.put(employeeId, fingers);
            }
        }

        Log.d(TAG, "Bundle reçu: " + result.employees.size() + " agent(s), "
                + countTemplates(result.templates) + " template(s)");
        return result;
    }

    private static int countTemplates(Map<Integer, Map<String, byte[]>> templates) {
        int total = 0;
        for (Map<String, byte[]> fingers : templates.values()) {
            total += fingers.size();
        }
        return total;
    }

    private static class BundleLoadResult {
        List<Employee> employees = new ArrayList<>();
        Map<Integer, Map<String, byte[]>> templates = new HashMap<>();
        String version;
        String status;
        boolean fromCache;

        BundleLoadResult() {
        }

        BundleLoadResult(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates, boolean fromCache) {
            this.employees = employees;
            this.templates = templates;
            this.fromCache = fromCache;
        }
    }
}
