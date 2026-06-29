package com.onip.biometric.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import com.onip.biometric.models.Employee;
import com.onip.biometric.utils.ConfigManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

/**
 * Service pour charger les employés depuis le backend
 */
public class EmployeeService {
    private static final String TAG = "EmployeeService";
    
    private Context context;
    private ConfigManager configManager;
    
    public interface Callback {
        void onSuccess(List<Employee> employees);
        void onError(String error);
    }
    
    public EmployeeService(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
    }
    
    public void loadEmployees(Callback callback) {
        new LoadEmployeesTask(callback).execute();
    }
    
    private class LoadEmployeesTask extends AsyncTask<Void, Void, List<Employee>> {
        private Callback callback;
        private String errorMessage = null;
        
        public LoadEmployeesTask(Callback callback) {
            this.callback = callback;
        }
        
        @Override
        protected List<Employee> doInBackground(Void... voids) {
            List<Employee> employees = new ArrayList<>();
            
            try {
                // Construire l'URL depuis ConfigManager
                String baseUrl = configManager.getBackendUrl().replace("/api/test", "");
                String urlString = baseUrl.replace("/api/test", "") + "/api/data";
                Log.d(TAG, "Chargement depuis: " + urlString);
                
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
                    
                    String jsonResponse = response.toString();
                    Log.d(TAG, "Response: " + jsonResponse);
                    
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
                        
                        // Charger tous les employés (pas seulement ceux avec biométrie)
                        employees.add(employee);
                        Log.d(TAG, "Employé chargé: " + employee.toString() + " (role: " + employee.getRole() + ")");
                    }
                    
                } else {
                    errorMessage = "Erreur HTTP: " + responseCode;
                }
                
                connection.disconnect();
                
            } catch (Exception e) {
                Log.e(TAG, "Erreur lors du chargement des employés", e);
                errorMessage = "Erreur: " + e.getMessage();
            }
            
            return employees;
        }
        
        @Override
        protected void onPostExecute(List<Employee> employees) {
            if (callback != null) {
                if (errorMessage != null) {
                    callback.onError(errorMessage);
                } else {
                    callback.onSuccess(employees);
                }
            }
        }
    }
}

