package com.onip.fingerprinttest;

import android.os.AsyncTask;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.List;

public class EmployeeService {
    private static final String TAG = "EmployeeService";
    private static final String BASE_URL = "http://192.168.1.73:8083";
    
    public interface Callback {
        void onSuccess(List<Employee> employees);
        void onError(String error);
    }
    
    public void loadEmployees(Callback callback) {
        new LoadEmployeesTask(callback).execute();
    }
    
    private static class LoadEmployeesTask extends AsyncTask<Void, Void, List<Employee>> {
        private Callback callback;
        private String errorMessage = null;
        
        public LoadEmployeesTask(Callback callback) {
            this.callback = callback;
        }
        
        @Override
        protected List<Employee> doInBackground(Void... voids) {
            List<Employee> employees = new ArrayList<>();
            
            try {
                URL url = new URL(BASE_URL + "/api/data");
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
                        
                        if (employee.isBiometricEnrolled() && 
                            employee.getFingerprintTemplate() != null && 
                            !employee.getFingerprintTemplate().isEmpty()) {
                            employees.add(employee);
                            Log.d(TAG, "Employé chargé: " + employee.toString());
                        }
                    }
                    
                } else {
                    errorMessage = "Erreur HTTP: " + responseCode + " - Impossible de se connecter au backend";
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

