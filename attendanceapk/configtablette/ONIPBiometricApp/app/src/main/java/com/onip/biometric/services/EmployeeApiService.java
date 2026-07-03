package com.onip.biometric.services;

import android.content.Context;
import android.util.Log;
import com.onip.biometric.models.EmployeeData;
import com.onip.biometric.utils.ConfigManager;
import org.json.JSONObject;
import org.json.JSONException;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

/**
 * Envoi des données employé vers l'API guichet RH.
 */
public class EmployeeApiService {

    private static final String TAG = "EmployeeApiService";

    private final Context context;
    private final ConfigManager configManager;

    public EmployeeApiService(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
    }

    public void saveEmployee(EmployeeData employeeData, ApiCallback callback) {
        new Thread(() -> {
            try {
                JSONObject jsonData = buildGuichetPayload(employeeData);
                Log.d(TAG, "Données guichet: " + jsonData);

                String response = sendToApi(jsonData);
                if (response != null) {
                    callback.onSuccess("Employé enregistré avec succès !");
                } else {
                    callback.onError("Erreur lors de la sauvegarde");
                }
            } catch (Exception e) {
                Log.e(TAG, "Erreur envoi", e);
                callback.onError("Erreur: " + e.getMessage());
            }
        }).start();
    }

    private JSONObject buildGuichetPayload(EmployeeData data) throws JSONException {
        JSONObject json = new JSONObject();

        String matricule = firstNonEmpty(data.getEmployeeId(), data.getNin());
        putIfPresent(json, "registration_number", matricule);
        putIfPresent(json, "first_name", data.getFirstName());
        putIfPresent(json, "last_name", data.getLastName());
        putIfPresent(json, "middle_name", data.getMiddleName());
        putIfPresent(json, "gender", data.getGender());
        putIfPresent(json, "date_of_birth", data.getBirthDate());
        putIfPresent(json, "place_of_birth", data.getBirthPlace());
        putIfPresent(json, "citizenship", data.getNationality());
        putIfPresent(json, "email", data.getEmail());
        putIfPresent(json, "mobile_number", data.getPhoneNumber());
        putIfPresent(json, "physical_address", data.getPostalAddress());
        putIfPresent(json, "marital_status", data.getMaritalStatus());
        putIfPresent(json, "spouse", data.getSpouseName());
        putIfPresent(json, "identity_number", data.getNationalIdNumber());
        putIfPresent(json, "date_of_join", data.getHireDate());
        putIfPresent(json, "emergency_contact", data.getEmergencyContactName());
        putIfPresent(json, "emergency_phone", data.getEmergencyContactPhone());
        putIfPresent(json, "payment_account", data.getBankAccountNumber());
        putIfPresent(json, "payer_name", data.getBankName());
        putIfPresent(json, "comment", data.getWorkStatus());

        putIfPresent(json, "home_province", data.getOriginProvince());
        putIfPresent(json, "home_territory", data.getOriginTerritory());
        putIfPresent(json, "home_sector", data.getOriginCommune());
        putIfPresent(json, "home_groupement", data.getOriginGroupement());
        putIfPresent(json, "home_village", data.getOriginVillage());

        if (data.getPhotoPath() != null && !data.getPhotoPath().isEmpty()) {
            json.put("photo_base64", data.getPhotoPath());
        }

        return json;
    }

    private static void putIfPresent(JSONObject json, String key, String value) throws JSONException {
        if (value != null && !value.trim().isEmpty()) {
            json.put(key, value.trim());
        }
    }

    private static String firstNonEmpty(String... values) {
        for (String value : values) {
            if (value != null && !value.trim().isEmpty()) {
                return value.trim();
            }
        }
        return null;
    }

    private String sendToApi(JSONObject jsonData) {
        String apiUrl = configManager.getGuichetUpsertUrl();
        try {
            Log.d(TAG, "POST " + apiUrl);
            URL url = new URL(apiUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();

            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            connection.setRequestProperty("X-Guichet-Internal-Key", configManager.getGuichetKey());
            connection.setDoOutput(true);
            connection.setConnectTimeout(30000);
            connection.setReadTimeout(30000);

            byte[] input = jsonData.toString().getBytes(StandardCharsets.UTF_8);
            try (OutputStream os = connection.getOutputStream()) {
                os.write(input, 0, input.length);
            }

            int responseCode = connection.getResponseCode();
            Log.d(TAG, "Code réponse: " + responseCode);

            String response = readStream(
                    responseCode >= 200 && responseCode < 300
                            ? connection.getInputStream()
                            : connection.getErrorStream()
            );
            Log.d(TAG, "Réponse: " + response);

            if (responseCode == HttpURLConnection.HTTP_OK || responseCode == HttpURLConnection.HTTP_CREATED) {
                return response;
            }
            return null;
        } catch (IOException e) {
            Log.e(TAG, "Erreur connexion", e);
            return null;
        }
    }

    private static String readStream(java.io.InputStream stream) {
        if (stream == null) {
            return "";
        }
        try {
            java.io.BufferedReader reader = new java.io.BufferedReader(
                    new java.io.InputStreamReader(stream, StandardCharsets.UTF_8));
            StringBuilder builder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
            return builder.toString();
        } catch (Exception e) {
            Log.e(TAG, "Erreur lecture réponse", e);
            return "";
        }
    }

    public interface ApiCallback {
        void onSuccess(String message);
        void onError(String error);
    }
}
