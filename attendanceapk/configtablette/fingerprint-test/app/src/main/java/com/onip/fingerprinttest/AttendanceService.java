package com.onip.fingerprinttest;

import android.os.AsyncTask;
import android.util.Log;

import org.json.JSONObject;

import java.io.OutputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class AttendanceService {
    private static final String TAG = "AttendanceService";
    private static final String BASE_URL = "http://192.168.1.73:8083";
    
    public interface Callback {
        void onSuccess(String message);
        void onError(String error);
    }
    
    public void recordAttendance(int employeeId, String attendanceType, String fingerprintUsed, Callback callback) {
        new RecordAttendanceTask(callback).execute(employeeId, attendanceType, fingerprintUsed);
    }
    
    private static class RecordAttendanceTask extends AsyncTask<Object, Void, String> {
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
                URL url = new URL(BASE_URL + "/api/attendance");
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(5000);
                connection.setReadTimeout(5000);
                
                // Préparer les données
                String currentDate = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());
                String currentTime = new SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(new Date());
                
                JSONObject jsonData = new JSONObject();
                jsonData.put("employeeId", employeeId);
                jsonData.put("date", currentDate);
                jsonData.put("time", currentTime);
                jsonData.put("type", attendanceType);
                jsonData.put("fingerprintUsed", fingerprintUsed);
                jsonData.put("status", "present");
                
                String jsonString = jsonData.toString();
                Log.d(TAG, "Envoi des données de présence: " + jsonString);
                
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
}

