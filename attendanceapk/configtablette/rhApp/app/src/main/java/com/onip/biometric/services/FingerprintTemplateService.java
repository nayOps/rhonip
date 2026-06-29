package com.onip.biometric.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Base64;
import android.util.Log;
import com.onip.biometric.models.Employee;
import com.onip.biometric.utils.ConfigManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;

/**
 * Service pour charger les templates d'empreintes depuis le backend
 */
public class FingerprintTemplateService {
    private static final String TAG = "FingerprintTemplateService";
    
    private Context context;
    private ConfigManager configManager;
    
    public interface Callback {
        void onSuccess(Map<String, byte[]> templates);
        void onError(String error);
    }
    
    public FingerprintTemplateService(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
    }
    
    /**
     * Charge les templates d'empreintes pour un employé
     */
    public void loadEmployeeTemplates(int employeeId, Callback callback) {
        new LoadTemplatesTask(employeeId, callback).execute();
    }
    
    /**
     * Charge les templates pour tous les employés (pour matching)
     */
    public void loadAllTemplatesForMatching(AllTemplatesCallback callback) {
        new LoadAllTemplatesTask(callback).execute();
    }
    
    public interface AllTemplatesCallback {
        void onSuccess(Map<Integer, Map<String, byte[]>> allTemplates); // employeeId -> templates
        void onError(String error);
    }
    
    private class LoadTemplatesTask extends AsyncTask<Void, Void, Map<String, byte[]>> {
        private int employeeId;
        private Callback callback;
        private String errorMessage = null;
        
        public LoadTemplatesTask(int employeeId, Callback callback) {
            this.employeeId = employeeId;
            this.callback = callback;
        }
        
        @Override
        protected Map<String, byte[]> doInBackground(Void... voids) {
            Map<String, byte[]> templates = new HashMap<>();
            
            try {
                String baseUrl = configManager.getBackendUrl().replace("/api/test", "");
                String urlString = baseUrl + "/api/fingerprints/" + employeeId;
                Log.d(TAG, "Chargement templates depuis: " + urlString);
                
                URL url = new URL(urlString);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                
                int responseCode = connection.getResponseCode();
                Log.d(TAG, "Response code: " + responseCode);
                
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
                    
                    // Charger chaque template
                    for (int i = 0; i < dataArray.length(); i++) {
                        JSONObject templateJson = dataArray.getJSONObject(i);
                        String fingerName = templateJson.getString("fingerName");
                        
                        // Récupérer le template binaire
                        String templateBase64 = loadTemplateBinary(employeeId, fingerName);
                        if (templateBase64 != null) {
                            byte[] templateData = Base64.decode(templateBase64, Base64.NO_WRAP);
                            templates.put(fingerName, templateData);
                            Log.d(TAG, "Template chargé: " + fingerName + " (" + templateData.length + " bytes)");
                        }
                    }
                    
                } else {
                    errorMessage = "Erreur HTTP: " + responseCode;
                }
                
                connection.disconnect();
                
            } catch (Exception e) {
                Log.e(TAG, "Erreur lors du chargement des templates", e);
                errorMessage = "Erreur: " + e.getMessage();
            }
            
            return templates;
        }
        
        @Override
        protected void onPostExecute(Map<String, byte[]> templates) {
            if (callback != null) {
                if (errorMessage != null) {
                    callback.onError(errorMessage);
                } else {
                    callback.onSuccess(templates);
                }
            }
        }
    }
    
    private String loadTemplateBinary(int employeeId, String fingerName) {
        try {
            String baseUrl = configManager.getBackendUrl().replace("/api/test", "");
            String urlString = baseUrl + "/api/fingerprints/" + employeeId + "/" + fingerName;
            
            URL url = new URL(urlString);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(10000);
            connection.setReadTimeout(10000);
            
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
    
    private class LoadAllTemplatesTask extends AsyncTask<Void, Void, Map<Integer, Map<String, byte[]>>> {
        private AllTemplatesCallback callback;
        private String errorMessage = null;
        
        public LoadAllTemplatesTask(AllTemplatesCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected Map<Integer, Map<String, byte[]>> doInBackground(Void... voids) {
            Map<Integer, Map<String, byte[]>> allTemplates = new HashMap<>();
            
            try {
                String baseUrl = configManager.getBackendUrl().replace("/api/test", "");
                String urlString = baseUrl + "/api/fingerprints/matching";
                Log.d(TAG, "Chargement tous les templates depuis: " + urlString);
                
                URL url = new URL(urlString);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(15000);
                connection.setReadTimeout(15000);
                
                int responseCode = connection.getResponseCode();
                Log.d(TAG, "Response code: " + responseCode);
                
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
                    
                } else {
                    errorMessage = "Erreur HTTP: " + responseCode;
                }
                
                connection.disconnect();
                
            } catch (Exception e) {
                Log.e(TAG, "Erreur lors du chargement de tous les templates", e);
                errorMessage = "Erreur: " + e.getMessage();
            }
            
            return allTemplates;
        }
        
        @Override
        protected void onPostExecute(Map<Integer, Map<String, byte[]>> allTemplates) {
            if (callback != null) {
                if (errorMessage != null) {
                    callback.onError(errorMessage);
                } else {
                    callback.onSuccess(allTemplates);
                }
            }
        }
    }
}


