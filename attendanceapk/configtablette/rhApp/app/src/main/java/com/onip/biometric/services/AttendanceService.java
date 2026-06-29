package com.onip.biometric.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import com.onip.biometric.utils.ConfigManager;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Service pour enregistrer les présences au backend
 */
public class AttendanceService {
    private static final String TAG = "AttendanceService";
    
    private Context context;
    private ConfigManager configManager;
    
    public interface Callback {
        void onSuccess(String message);
        void onError(String error);
    }
    
    public AttendanceService(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
    }
    
    public void recordAttendance(int employeeId, String attendanceType, String fingerprintUsed, Callback callback) {
        new RecordAttendanceTask(callback).execute(employeeId, attendanceType, fingerprintUsed);
    }
    
    /**
     * Récupère l'historique des présences pour un employé aujourd'hui
     */
    public void getTodayAttendance(int employeeId, AttendanceHistoryCallback callback) {
        new GetAttendanceHistoryTask(callback).execute(employeeId);
    }
    
    public interface AttendanceHistoryCallback {
        void onSuccess(List<AttendanceRecord> records);
        void onError(String error);
    }
    
    public static class AttendanceRecord {
        public int id;
        public int employeeId;
        public String date;
        public String time;
        public String type;
        
        public AttendanceRecord(int id, int employeeId, String date, String time, String type) {
            this.id = id;
            this.employeeId = employeeId;
            this.date = date;
            this.time = time;
            this.type = type;
        }
    }
    
    private class RecordAttendanceTask extends AsyncTask<Object, Void, String> {
        private Callback callback;
        private boolean isSuccess = false;
        
        public RecordAttendanceTask(Callback callback) {
            this.callback = callback;
        }
        
        @Override
        protected String doInBackground(Object... params) {
            int employeeId = (Integer) params[0];
            String attendanceType = (String) params[1];
            String fingerprintUsed = (String) params[2];
            
            try {
                // Construire l'URL depuis ConfigManager
                String baseUrl = configManager.getBackendUrl().replace("/api/test", "");
                String urlString = baseUrl + "/api/attendance";
                Log.d(TAG, "Envoi présence à: " + urlString);
                
                URL url = new URL(urlString);
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(10000);
                connection.setReadTimeout(10000);
                
                // Préparer les données
                String currentDate = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());
                String currentTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());
                
                JSONObject jsonData = new JSONObject();
                jsonData.put("employeeId", employeeId);
                jsonData.put("date", currentDate);
                jsonData.put("time", currentTime);
                jsonData.put("type", attendanceType);
                jsonData.put("fingerprintUsed", fingerprintUsed);
                jsonData.put("status", "present");
                
                String jsonString = jsonData.toString();
                Log.d(TAG, "Données de présence: " + jsonString);
                
                // Envoyer les données
                OutputStream outputStream = connection.getOutputStream();
                outputStream.write(jsonString.getBytes("UTF-8"));
                outputStream.flush();
                outputStream.close();
                
                // Lire la réponse
                int responseCode = connection.getResponseCode();
                Log.d(TAG, "Response code: " + responseCode);
                
                BufferedReader reader;
                if (responseCode >= 200 && responseCode < 300) {
                    reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                    isSuccess = true;
                } else {
                    reader = new BufferedReader(new InputStreamReader(connection.getErrorStream()));
                    isSuccess = false;
                }
                
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                connection.disconnect();
                
                return response.toString();
                
            } catch (Exception e) {
                Log.e(TAG, "Erreur lors de l'enregistrement de la présence", e);
                return "Erreur: " + e.getMessage();
            }
        }
        
        @Override
        protected void onPostExecute(String result) {
            if (callback != null) {
                if (isSuccess) {
                    callback.onSuccess("Présence enregistrée avec succès");
                } else {
                    callback.onError(result);
                }
            }
        }
    }
    
    private class GetAttendanceHistoryTask extends AsyncTask<Integer, Void, List<AttendanceRecord>> {
        private AttendanceHistoryCallback callback;
        private String errorMessage = null;
        
        public GetAttendanceHistoryTask(AttendanceHistoryCallback callback) {
            this.callback = callback;
        }
        
        @Override
        protected List<AttendanceRecord> doInBackground(Integer... params) {
            int employeeId = params[0];
            List<AttendanceRecord> records = new ArrayList<>();
            
            try {
                String baseUrl = configManager.getBackendUrl().replace("/api/test", "");
                String urlString = baseUrl + "/api/attendance";
                Log.d(TAG, "Récupération historique depuis: " + urlString);
                
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
                    org.json.JSONObject jsonObject = new org.json.JSONObject(jsonResponse);
                    org.json.JSONArray dataArray = jsonObject.getJSONArray("data");
                    
                    // Filtrer pour l'employé et aujourd'hui
                    String today = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());
                    
                    for (int i = 0; i < dataArray.length(); i++) {
                        org.json.JSONObject attJson = dataArray.getJSONObject(i);
                        int attEmployeeId = attJson.optInt("employeeId", 0);
                        String attDate = attJson.optString("date", "");
                        
                        if (attEmployeeId == employeeId && attDate.equals(today)) {
                            AttendanceRecord record = new AttendanceRecord(
                                attJson.optInt("id", 0),
                                attEmployeeId,
                                attDate,
                                attJson.optString("time", ""),
                                attJson.optString("type", "")
                            );
                            records.add(record);
                        }
                    }
                    
                } else {
                    errorMessage = "Erreur HTTP: " + responseCode;
                }
                
                connection.disconnect();
                
            } catch (Exception e) {
                Log.e(TAG, "Erreur lors de la récupération de l'historique", e);
                errorMessage = "Erreur: " + e.getMessage();
            }
            
            return records;
        }
        
        @Override
        protected void onPostExecute(List<AttendanceRecord> records) {
            if (callback != null) {
                if (errorMessage != null) {
                    callback.onError(errorMessage);
                } else {
                    callback.onSuccess(records);
                }
            }
        }
    }
}

