package com.onip.attendance.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Log;
import com.onip.attendance.storage.OfflinePunchQueue;
import com.onip.attendance.utils.ConfigManager;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

/**
 * Enregistrement des pointages RH + file offline.
 */
public class AttendanceService {
    private static final String TAG = "AttendanceService";

    private final Context context;
    private final ConfigManager configManager;
    private final OfflinePunchQueue offlineQueue;

    public interface PunchCallback {
        void onSuccess(PunchResult result);
        void onError(String error);
    }

    public static class PunchResult {
        public String message;
        public String employeeName;
        public JSONObject assignedSlot;
        public JSONObject dayEvaluation;
        public boolean queuedOffline;
    }

    public AttendanceService(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
        this.offlineQueue = new OfflinePunchQueue(context);
    }

    public void recordPunch(int employeeId, PunchCallback callback) {
        new RecordPunchTask(employeeId, callback).execute();
    }

    public void syncPendingPunches() {
        new SyncPendingTask().execute();
    }

    public int getPendingCount() {
        return offlineQueue.count();
    }

    private class RecordPunchTask extends AsyncTask<Void, Void, PunchResult> {
        private final int employeeId;
        private final PunchCallback callback;
        private String errorMessage;
        private boolean isSuccess;

        RecordPunchTask(int employeeId, PunchCallback callback) {
            this.employeeId = employeeId;
            this.callback = callback;
        }

        @Override
        protected PunchResult doInBackground(Void... voids) {
            String currentDate = new SimpleDateFormat("yyyy-MM-dd", Locale.getDefault()).format(new Date());
            String currentTime = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(new Date());

            try {
                PunchResult result = postPunch(employeeId, currentDate, currentTime);
                isSuccess = true;
                return result;
            } catch (Exception e) {
                Log.w(TAG, "Pointage offline: " + e.getMessage());
                offlineQueue.enqueue(employeeId, currentDate, currentTime);
                PunchResult queued = new PunchResult();
                queued.message = "Pointage enregistré localement (sync en attente)";
                queued.queuedOffline = true;
                isSuccess = true;
                return queued;
            }
        }

        @Override
        protected void onPostExecute(PunchResult result) {
            if (callback == null) {
                return;
            }
            if (isSuccess && result != null) {
                callback.onSuccess(result);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Erreur inconnue");
            }
        }
    }

    private class SyncPendingTask extends AsyncTask<Void, Void, Void> {
        @Override
        protected Void doInBackground(Void... voids) {
            List<OfflinePunchQueue.PendingPunch> pending = offlineQueue.listAll();
            for (OfflinePunchQueue.PendingPunch punch : pending) {
                try {
                    postPunch(punch.employeeId, punch.date, punch.time);
                    offlineQueue.remove(punch.id);
                } catch (Exception e) {
                    Log.w(TAG, "Sync pending échouée id=" + punch.id + ": " + e.getMessage());
                    break;
                }
            }
            return null;
        }
    }

    private PunchResult postPunch(int employeeId, String currentDate, String currentTime) throws Exception {
        String urlString = configManager.getBackendUrl("/api/attendance");
        HttpURLConnection connection = (HttpURLConnection) new URL(urlString).openConnection();
        connection.setRequestMethod("POST");
        connection.setRequestProperty("Content-Type", "application/json");
        connection.setDoOutput(true);
        connection.setConnectTimeout(10000);
        connection.setReadTimeout(10000);

        JSONObject jsonData = new JSONObject();
        jsonData.put("employeeId", employeeId);
        jsonData.put("date", currentDate);
        jsonData.put("time", currentTime);
        jsonData.put("source", "fingerprint");

        OutputStream outputStream = connection.getOutputStream();
        outputStream.write(jsonData.toString().getBytes("UTF-8"));
        outputStream.flush();
        outputStream.close();

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

        JSONObject jsonObject = new JSONObject(response.toString());
        if (!"success".equals(jsonObject.optString("status"))) {
            throw new Exception(jsonObject.optString("message", response.toString()));
        }

        PunchResult result = new PunchResult();
        result.message = jsonObject.optString("message", "Pointage enregistré.");
        result.employeeName = jsonObject.optString("employeeName", "");
        result.assignedSlot = jsonObject.optJSONObject("assignedSlot");
        result.dayEvaluation = jsonObject.optJSONObject("dayEvaluation");
        return result;
    }
}
