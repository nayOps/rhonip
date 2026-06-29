package com.onip.enroll.services;

import android.content.Context;
import android.os.AsyncTask;
import android.util.Base64;
import android.util.Log;
import com.onip.enroll.utils.ConfigManager;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

public class EnrollService {
    private static final String TAG = "EnrollService";

    private final ConfigManager configManager;

    public interface EnrollCallback {
        void onSuccess(JSONObject response);
        void onError(String error);
    }

    public interface StatusCallback {
        void onSuccess(org.json.JSONObject response);
        void onError(String error);
    }

    public EnrollService(Context context) {
        this.configManager = new ConfigManager(context);
    }

    public void uploadFingerprint(int employeeId, String fingerPosition, byte[] templateData, EnrollCallback callback) {
        new UploadTask(callback).execute(employeeId, fingerPosition, templateData);
    }

    public void fetchEnrollmentStatus(int employeeId, StatusCallback callback) {
        new StatusTask(callback).execute(employeeId);
    }

    private class UploadTask extends AsyncTask<Object, Void, JSONObject> {
        private final EnrollCallback callback;
        private String errorMessage;
        private boolean success;

        UploadTask(EnrollCallback callback) {
            this.callback = callback;
        }

        @Override
        protected JSONObject doInBackground(Object... params) {
            int employeeId = (Integer) params[0];
            String fingerPosition = (String) params[1];
            byte[] templateData = (byte[]) params[2];

            try {
                String urlString = configManager.getBackendUrl("/api/fingerprints/enroll");
                HttpURLConnection connection = (HttpURLConnection) new URL(urlString).openConnection();
                connection.setRequestMethod("POST");
                connection.setRequestProperty("Content-Type", "application/json");
                connection.setDoOutput(true);
                connection.setConnectTimeout(15000);
                connection.setReadTimeout(15000);

                JSONObject json = new JSONObject();
                json.put("employeeId", employeeId);
                json.put("fingerPosition", fingerPosition);
                json.put("template_base64", Base64.encodeToString(templateData, Base64.NO_WRAP));
                json.put("template_format", "MORPHO_PK_ISO_FMR");
                json.put("device", "morpho_tablet");

                OutputStream os = connection.getOutputStream();
                os.write(json.toString().getBytes("UTF-8"));
                os.flush();
                os.close();

                int code = connection.getResponseCode();
                BufferedReader reader = new BufferedReader(new InputStreamReader(
                        code >= 200 && code < 300 ? connection.getInputStream() : connection.getErrorStream()));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                connection.disconnect();

                JSONObject body = new JSONObject(response.toString());
                if (code >= 200 && code < 300 && "success".equals(body.optString("status"))) {
                    success = true;
                    return body;
                }
                errorMessage = body.optString("message", response.toString());
                success = false;
                return null;
            } catch (Exception e) {
                Log.e(TAG, "Upload fingerprint failed", e);
                errorMessage = e.getMessage();
                success = false;
                return null;
            }
        }

        @Override
        protected void onPostExecute(JSONObject result) {
            if (callback == null) {
                return;
            }
            if (success && result != null) {
                callback.onSuccess(result);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Erreur upload");
            }
        }
    }

    private class StatusTask extends AsyncTask<Integer, Void, JSONObject> {
        private final StatusCallback callback;
        private String errorMessage;
        private boolean success;

        StatusTask(StatusCallback callback) {
            this.callback = callback;
        }

        @Override
        protected JSONObject doInBackground(Integer... params) {
            int employeeId = params[0];
            try {
                String urlString = configManager.getBackendUrl("/api/fingerprints/enroll/status/" + employeeId);
                HttpURLConnection connection = (HttpURLConnection) new URL(urlString).openConnection();
                connection.setRequestMethod("GET");
                connection.setConnectTimeout(15000);
                connection.setReadTimeout(15000);

                int code = connection.getResponseCode();
                BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                StringBuilder response = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    response.append(line);
                }
                reader.close();
                connection.disconnect();

                JSONObject body = new JSONObject(response.toString());
                if (code == HttpURLConnection.HTTP_OK && "success".equals(body.optString("status"))) {
                    success = true;
                    return body;
                }
                errorMessage = body.optString("message", "Erreur statut");
                return null;
            } catch (Exception e) {
                errorMessage = e.getMessage();
                return null;
            }
        }

        @Override
        protected void onPostExecute(JSONObject result) {
            if (callback == null) {
                return;
            }
            if (success && result != null) {
                callback.onSuccess(result);
            } else {
                callback.onError(errorMessage != null ? errorMessage : "Erreur statut");
            }
        }
    }
}
