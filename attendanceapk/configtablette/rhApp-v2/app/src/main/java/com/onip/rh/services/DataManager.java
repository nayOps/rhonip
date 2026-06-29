package com.onip.rh.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Base64;
import android.util.Log;
import com.onip.rh.models.Employee;
import com.onip.rh.utils.ConfigManager;
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
 * Gestionnaire de données (employés et templates)
 * Version améliorée avec retry automatique et gestion d'erreurs
 */
public class DataManager {
    
    private static final String TAG = "DataManager";
    private static final int MAX_RETRIES = 3;
    private static final int CONNECT_TIMEOUT_MS = 10000;
    private static final int READ_TIMEOUT_MS = 15000;
    
    private Context context;
    private ConfigManager configManager;
    
    public interface EmployeesCallback {
        void onSuccess(List<Employee> employees);
        void onError(String error);
    }
    
    public interface TemplatesCallback {
        void onSuccess(Map<Integer, Map<String, byte[]>> allTemplates);
        void onError(String error);
    }
    
    public interface AllDataCallback {
        void onSuccess(List<Employee> employees, Map<Integer, Map<String, byte[]>> templates);
        void onError(String error);
    }
    
    public DataManager(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
    }
    
    /**
     * Charge tous les employés depuis le backend
     */
    public void loadEmployees(EmployeesCallback callback) {
        new LoadEmployeesTask(callback).execute();
    }
    
    /**
     * Charge tous les templates pour le matching
     */
    public void loadAllTemplates(TemplatesCallback callback) {
        new LoadAllTemplatesTask(callback).execute();
    }
    
    /**
     * Charge employés et templates en parallèle
     */
    public void loadAllData(AllDataCallback callback) {
        final boolean[] employeesLoaded = {false};
        final boolean[] templatesLoaded = {false};
        final List<Employee>[] employeesRef = new List[]{null};
        final Map<Integer, Map<String, byte[]>>[] templatesRef = new Map[]{null};
        final String[] errorRef = new String[]{null};
        
        loadEmployees(new EmployeesCallback() {
            @Override
            public void onSuccess(List<Employee> employees) {
                employeesRef[0] = employees;
                employeesLoaded[0] = true;
                checkAndNotify(callback, employeesRef[0], templatesRef[0], employeesLoaded[0], templatesLoaded[0], errorRef);
            }
            
            @Override
            public void onError(String error) {
                errorRef[0] = "Erreur chargement employés: " + error;
                employeesLoaded[0] = true;
                checkAndNotify(callback, employeesRef[0], templatesRef[0], employeesLoaded[0], templatesLoaded[0], errorRef);
            }
        });
        
        loadAllTemplates(new TemplatesCallback() {
            @Override
            public void onSuccess(Map<Integer, Map<String, byte[]>> templates) {
                templatesRef[0] = templates;
                templatesLoaded[0] = true;
                checkAndNotify(callback, employeesRef[0], templatesRef[0], employeesLoaded[0], templatesLoaded[0], errorRef);
            }
            
            @Override
            public void onError(String error) {
                errorRef[0] = "Erreur chargement templates: " + error;
                templatesLoaded[0] = true;
                checkAndNotify(callback, employeesRef[0], templatesRef[0], employeesLoaded[0], templatesLoaded[0], errorRef);
            }
        });
    }
    
    private void checkAndNotify(AllDataCallback callback, List<Employee> employees, 
                                Map<Integer, Map<String, byte[]>> templates,
                                boolean employeesDone, boolean templatesDone, String[] error) {
        if (employeesDone && templatesDone) {
            if (error[0] != null) {
                callback.onError(error[0]);
            } else {
                callback.onSuccess(employees, templates);
            }
        }
    }
    
    // ========== TASK: Chargement des employés ==========
    
    private class LoadEmployeesTask extends AsyncTask<Void, Void, List<Employee>> {
        private EmployeesCallback callback;
        private String errorMessage = null;
        private int retryCount = 0;
        
        public LoadEmployeesTask(EmployeesCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected List<Employee> doInBackground(Void... voids) {
            List<Employee> employees = new ArrayList<>();
            
            while (retryCount < MAX_RETRIES) {
                try {
                    String urlString = configManager.getBackendUrl("/api/data");
                    Log.d(TAG, "Chargement employés depuis: " + urlString + " (tentative " + (retryCount + 1) + ")");
                    
                    URL url = new URL(urlString);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
                    connection.setReadTimeout(READ_TIMEOUT_MS);
                    
                    int responseCode = connection.getResponseCode();
                    Log.d(TAG, "Response code: " + responseCode + " pour " + urlString);
                    
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String line;
                        
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        reader.close();
                        
                        String jsonResponse = response.toString();
                        Log.d(TAG, "Response reçue (" + jsonResponse.length() + " chars)");
                        
                        // Parser la réponse JSON
                        JSONObject jsonObject = new JSONObject(jsonResponse);
                        JSONArray dataArray = jsonObject.getJSONArray("data");
                        
                        for (int i = 0; i < dataArray.length(); i++) {
                            JSONObject empJson = dataArray.getJSONObject(i);
                            
                            Employee employee = new Employee();
                            employee.setId(empJson.optInt("id", 0));
                            employee.setFirstName(empJson.optString("firstName", ""));
                            employee.setLastName(empJson.optString("lastName", ""));
                            employee.setNin(empJson.optString("nin", ""));
                            employee.setEmail(empJson.optString("email", ""));
                            employee.setPhoneNumber(empJson.optString("phoneNumber", ""));
                            employee.setFingerprintTemplate(empJson.optString("fingerprintTemplate", ""));
                            employee.setBiometricEnrolled(empJson.optBoolean("biometricEnrolled", false));
                            employee.setRole(empJson.optString("role", "employee"));
                            
                            employees.add(employee);
                        }
                        
                        Log.d(TAG, "✅ " + employees.size() + " employé(s) chargé(s)");
                        connection.disconnect();
                        return employees;
                        
                    } else {
                        errorMessage = "Erreur HTTP: " + responseCode;
                        connection.disconnect();
                    }
                    
                } catch (Exception e) {
                    Log.e(TAG, "Erreur tentative " + (retryCount + 1) + ": " + e.getMessage());
                    errorMessage = "Erreur: " + e.getMessage();
                }
                
                retryCount++;
                if (retryCount < MAX_RETRIES) {
                    try {
                        Thread.sleep(1000 * retryCount); // Backoff exponentiel
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
            
            return employees;
        }
        
        @Override
        protected void onPostExecute(List<Employee> employees) {
            if (callback != null) {
                if (errorMessage != null && employees.isEmpty()) {
                    callback.onError(errorMessage);
                } else {
                    callback.onSuccess(employees);
                }
            }
        }
    }
    
    // ========== TASK: Chargement de tous les templates ==========
    
    private class LoadAllTemplatesTask extends AsyncTask<Void, Void, Map<Integer, Map<String, byte[]>>> {
        private TemplatesCallback callback;
        private String errorMessage = null;
        private int retryCount = 0;
        
        public LoadAllTemplatesTask(TemplatesCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected Map<Integer, Map<String, byte[]>> doInBackground(Void... voids) {
            Map<Integer, Map<String, byte[]>> allTemplates = new HashMap<>();
            
            while (retryCount < MAX_RETRIES) {
                try {
                    String urlString = configManager.getBackendUrl("/api/fingerprints/matching");
                    Log.d(TAG, "Chargement templates depuis: " + urlString + " (tentative " + (retryCount + 1) + ")");
                    
                    URL url = new URL(urlString);
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    connection.setRequestMethod("GET");
                    connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
                    connection.setReadTimeout(READ_TIMEOUT_MS);
                    
                    int responseCode = connection.getResponseCode();
                    Log.d(TAG, "Response code: " + responseCode + " pour " + urlString);
                    
                    if (responseCode == HttpURLConnection.HTTP_OK) {
                        BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                        StringBuilder response = new StringBuilder();
                        String line;
                        
                        while ((line = reader.readLine()) != null) {
                            response.append(line);
                        }
                        reader.close();
                        
                        JSONObject jsonObject = new JSONObject(response.toString());
                        JSONArray dataArray = jsonObject.getJSONArray("data");
                        
                        // Grouper par employee_id
                        for (int i = 0; i < dataArray.length(); i++) {
                            JSONObject templateJson = dataArray.getJSONObject(i);
                            int empId = templateJson.getInt("employeeId");
                            String fingerName = templateJson.getString("fingerName");
                            
                            // Charger le template binaire
                            String templateBase64 = loadTemplateBinary(empId, fingerName);
                            if (templateBase64 != null) {
                                byte[] templateData = Base64.decode(templateBase64, Base64.NO_WRAP);
                                
                                if (!allTemplates.containsKey(empId)) {
                                    allTemplates.put(empId, new HashMap<String, byte[]>());
                                }
                                allTemplates.get(empId).put(fingerName, templateData);
                            }
                        }
                        
                        Log.d(TAG, "✅ " + allTemplates.size() + " employé(s) avec templates chargés");
                        connection.disconnect();
                        return allTemplates;
                        
                    } else {
                        // Lire le message d'erreur du serveur
                        String errorResponse = "";
                        try {
                            BufferedReader errorReader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
                            StringBuilder errorResponseBuilder = new StringBuilder();
                            String errorLine;
                            while ((errorLine = errorReader.readLine()) != null) {
                                errorResponseBuilder.append(errorLine);
                            }
                            errorReader.close();
                            errorResponse = errorResponseBuilder.toString();
                        } catch (Exception ex) {
                            // Ignorer si on ne peut pas lire l'erreur
                        }
                        errorMessage = "Erreur HTTP " + responseCode + (errorResponse.isEmpty() ? "" : ": " + errorResponse);
                        connection.disconnect();
                    }
                    
                } catch (java.net.ConnectException e) {
                    Log.e(TAG, "❌ Connexion refusée tentative " + (retryCount + 1) + ": " + e.getMessage());
                    errorMessage = "Connexion refusée - Vérifiez que le backend est démarré sur " + configManager.getBackendBaseUrl();
                } catch (java.net.UnknownHostException e) {
                    Log.e(TAG, "❌ Host inconnu tentative " + (retryCount + 1) + ": " + e.getMessage());
                    errorMessage = "Host inconnu - Vérifiez l'IP du backend: " + configManager.getBackendIp();
                } catch (java.net.SocketTimeoutException e) {
                    Log.e(TAG, "❌ Timeout tentative " + (retryCount + 1) + ": " + e.getMessage());
                    errorMessage = "Timeout - Le backend ne répond pas sur " + configManager.getBackendBaseUrl();
                } catch (Exception e) {
                    Log.e(TAG, "❌ Erreur tentative " + (retryCount + 1) + ": " + e.getMessage(), e);
                    errorMessage = "Erreur: " + e.getClass().getSimpleName() + " - " + e.getMessage();
                }
                
                retryCount++;
                if (retryCount < MAX_RETRIES) {
                    try {
                        Thread.sleep(1000 * retryCount);
                    } catch (InterruptedException ie) {
                        Thread.currentThread().interrupt();
                        break;
                    }
                }
            }
            
            return allTemplates;
        }
        
        @Override
        protected void onPostExecute(Map<Integer, Map<String, byte[]>> allTemplates) {
            if (callback != null) {
                if (errorMessage != null && allTemplates.isEmpty()) {
                    callback.onError(errorMessage);
                } else {
                    callback.onSuccess(allTemplates);
                }
            }
        }
    }
    
    /**
     * Charge le template binaire pour un employé et un doigt spécifique
     */
    private String loadTemplateBinary(int employeeId, String fingerName) {
        try {
            String urlString = configManager.getBackendUrl("/api/fingerprints/" + employeeId + "/" + fingerName);
            
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
            connection.setReadTimeout(READ_TIMEOUT_MS);
            
            if (connection.getResponseCode() == HttpURLConnection.HTTP_OK) {
                BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                StringBuilder response = new StringBuilder();
                String line;
                
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                
                JSONObject jsonObject = new JSONObject(response.toString());
                return jsonObject.getString("template_base64");
            }
            
            connection.disconnect();
        } catch (Exception e) {
            Log.e(TAG, "Erreur chargement template binaire: " + e.getMessage());
        }
        return null;
    }
}

