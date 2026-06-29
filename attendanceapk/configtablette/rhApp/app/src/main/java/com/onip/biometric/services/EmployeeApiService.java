package com.onip.biometric.services;

import android.content.Context;
import android.util.Base64;
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
import java.util.Map;

/**
 * Service pour l'envoi des données employé vers le backend RH
 */
public class EmployeeApiService {
    
    private static final String TAG = "EmployeeApiService";
    
    private Context context;
    private ConfigManager configManager;
    
    public EmployeeApiService(Context context) {
        this.context = context;
        this.configManager = new ConfigManager(context);
    }
    
    /**
     * Récupère l'URL du backend depuis la configuration
     */
    private String getBaseUrl() {
        return configManager.getBackendUrl();
    }
    
    /**
     * Envoie les données de l'employé vers le backend
     */
    public void saveEmployee(EmployeeData employeeData, ApiCallback callback) {
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    // Sérialiser les données en JSON
                    JSONObject jsonData = serializeEmployeeData(employeeData);
                    Log.d(TAG, "Données à envoyer: " + jsonData.toString());
                    
                    // Envoyer vers l'API
                    boolean success = sendToApi(jsonData);
                    
                    if (success) {
                        Log.d(TAG, "Employé sauvegardé avec succès");
                        callback.onSuccess("Employé enregistré avec succès !");
                    } else {
                        Log.e(TAG, "Erreur lors de la sauvegarde");
                        callback.onError("Erreur lors de la sauvegarde");
                    }
                    
                } catch (Exception e) {
                    Log.e(TAG, "Erreur lors de l'envoi des données", e);
                    callback.onError("Erreur: " + e.getMessage());
                }
            }
        }).start();
    }
    
    /**
     * Sérialise les données employé en JSON
     */
    private JSONObject serializeEmployeeData(EmployeeData employeeData) throws JSONException {
        JSONObject json = new JSONObject();
        
        // ========== IDENTITÉ ==========
        json.put("nin", employeeData.getNin());
        json.put("firstName", employeeData.getFirstName());
        json.put("lastName", employeeData.getLastName());
        // employeeNumber optionnel - généré seulement si nécessaire
        if (employeeData.getFirstName() != null && !employeeData.getFirstName().isEmpty()) {
            json.put("employeeNumber", "EMP" + System.currentTimeMillis());
        }
        json.put("middleName", employeeData.getMiddleName());
        json.put("otherNames", employeeData.getOtherNames());
        json.put("gender", employeeData.getGender());
        json.put("birthPlace", employeeData.getBirthPlace());
        json.put("birthDate", employeeData.getBirthDate());
        json.put("nationality", employeeData.getNationality());
        json.put("eyeColor", employeeData.getEyeColor());
        json.put("height", employeeData.getHeight());
        json.put("email", employeeData.getEmail());
        json.put("postalAddress", employeeData.getPostalAddress());
        json.put("phoneNumber", employeeData.getPhoneNumber());
        
        // ========== ORIGINE ==========
        json.put("originProvince", employeeData.getOriginProvince());
        json.put("originTerritory", employeeData.getOriginTerritory());
        json.put("originCommune", employeeData.getOriginCommune());
        json.put("originGroupement", employeeData.getOriginGroupement());
        json.put("originVillage", employeeData.getOriginVillage());
        
        // ========== ADRESSE ==========
        json.put("currentProvince", employeeData.getCurrentProvince());
        json.put("currentTerritory", employeeData.getCurrentTerritory());
        json.put("currentCommune", employeeData.getCurrentCommune());
        json.put("currentGroupement", employeeData.getCurrentGroupement());
        json.put("currentVillage", employeeData.getCurrentVillage());
        
        // ========== SITUATION FAMILIALE ==========
        json.put("maritalStatus", employeeData.getMaritalStatus());
        json.put("spouseName", employeeData.getSpouseName());
        json.put("spouseFirstName", employeeData.getSpouseFirstName());
        json.put("spouseLastName", employeeData.getSpouseLastName());
        json.put("spouseMiddleName", employeeData.getSpouseMiddleName());
        json.put("spouseBirthPlace", employeeData.getSpouseBirthPlace());
        json.put("spouseBirthDate", employeeData.getSpouseBirthDate());
        json.put("numberOfChildren", employeeData.getNumberOfChildren());
        json.put("marriageCertificate", employeeData.getMarriageCertificate());
        
        // ========== FORMATION ==========
        json.put("educationLevel", employeeData.getEducationLevel());
        json.put("educationCountry", employeeData.getEducationCountry());
        json.put("educationInstitution", employeeData.getEducationInstitution());
        json.put("educationCity", employeeData.getEducationCity());
        json.put("educationStartYear", employeeData.getEducationStartYear());
        json.put("educationEndYear", employeeData.getEducationEndYear());
        json.put("educationField", employeeData.getEducationField());
        json.put("educationSpecialization", employeeData.getEducationSpecialization());
        json.put("educationResult", employeeData.getEducationResult());
        json.put("educationDocumentNumber", employeeData.getEducationDocumentNumber());
        json.put("educationDocument", employeeData.getEducationDocument());
        
        // ========== PROFESSIONNEL ==========
        json.put("employeeId", employeeData.getEmployeeId());
        json.put("hireDate", employeeData.getHireDate());
        json.put("contractType", employeeData.getContractType());
        json.put("jobTitle", employeeData.getJobTitle());
        json.put("department", employeeData.getDepartment());
        json.put("hierarchyLevel", employeeData.getHierarchyLevel());
        json.put("supervisor", employeeData.getSupervisor());
        json.put("professionalCategory", employeeData.getProfessionalCategory());
        json.put("workLocation", employeeData.getWorkLocation());
        json.put("workStatus", employeeData.getWorkStatus());
        
        // ========== DOCUMENTS ==========
        json.put("nationalIdNumber", employeeData.getNationalIdNumber());
        json.put("nationalIdDocument", employeeData.getNationalIdDocument());
        json.put("inssNumber", employeeData.getInssNumber());
        json.put("taxNumber", employeeData.getTaxNumber());
        json.put("workPermit", employeeData.getWorkPermit());
        json.put("voterCard", employeeData.getVoterCard());
        json.put("criminalRecord", employeeData.getCriminalRecord());
        json.put("identityPhoto", employeeData.getIdentityPhoto());
        json.put("diplomas", employeeData.getDiplomas());
        
        // ========== URGENCE ==========
        json.put("emergencyContactName", employeeData.getEmergencyContactName());
        json.put("emergencyContactAddress", employeeData.getEmergencyContactAddress());
        json.put("emergencyContactPhone", employeeData.getEmergencyContactPhone());
        
        // ========== BANCAIRE ==========
        json.put("bankName", employeeData.getBankName());
        json.put("bankAccountNumber", employeeData.getBankAccountNumber());
        json.put("paymentCurrency", employeeData.getPaymentCurrency());
        json.put("paymentMethod", employeeData.getPaymentMethod());
        json.put("grossSalary", employeeData.getGrossSalary());
        json.put("netSalary", employeeData.getNetSalary());
        json.put("benefits", employeeData.getBenefits());
        
        // ========== MÉDICAL ==========
        json.put("bloodType", employeeData.getBloodType());
        json.put("allergies", employeeData.getAllergies());
        json.put("disabilities", employeeData.getDisabilities());
        json.put("medicalInsurance", employeeData.getMedicalInsurance());
        json.put("doctorName", employeeData.getDoctorName());
        
        // ========== ÉQUIPEMENTS ==========
        json.put("accessBadge", employeeData.getAccessBadge());
        json.put("officeKeys", employeeData.getOfficeKeys());
        json.put("workEquipment", employeeData.getWorkEquipment());
        json.put("computerAccounts", employeeData.getComputerAccounts());
        
        // ========== BIOMÉTRIE ==========
        json.put("photoPath", employeeData.getPhotoPath());
        json.put("fingerprintTemplate", employeeData.getFingerprintTemplate());
        json.put("fingerprintFinger", employeeData.getFingerprintFinger());
        json.put("biometricEnrollmentDate", employeeData.getBiometricEnrollmentDate());
        json.put("biometricEnrolled", employeeData.isBiometricEnrolled());
        
        // NOUVEAU : Ajouter les templates binaires encodés en Base64
        if (employeeData.getCapturedFingerprints() != null && !employeeData.getCapturedFingerprints().isEmpty()) {
            try {
                JSONObject fingerprintsJson = new JSONObject();
                for (Map.Entry<String, byte[]> entry : employeeData.getCapturedFingerprints().entrySet()) {
                    // Encoder le template binaire en Base64
                    String base64Template = Base64.encodeToString(entry.getValue(), Base64.NO_WRAP);
                    fingerprintsJson.put(entry.getKey(), base64Template);
                    Log.d(TAG, "Template " + entry.getKey() + " encodé: " + entry.getValue().length + " bytes -> " + base64Template.length() + " chars Base64");
                }
                json.put("fingerprints", fingerprintsJson);
                Log.d(TAG, "✅ " + employeeData.getCapturedFingerprints().size() + " template(s) ajouté(s) au JSON");
            } catch (JSONException e) {
                Log.e(TAG, "Erreur encodage templates: " + e.getMessage());
            }
        } else {
            Log.d(TAG, "⚠️ Aucun template binaire à envoyer");
        }
        
        return json;
    }
    
    /**
     * Envoie les données vers l'API backend
     */
    private boolean sendToApi(JSONObject jsonData) {
        try {
            String baseUrl = getBaseUrl();
            Log.d(TAG, "Tentative de connexion à: " + baseUrl);
            URL url = new URL(baseUrl);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            Log.d(TAG, "Connexion établie");
            
            // Configuration de la requête
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setRequestProperty("Accept", "application/json");
            connection.setDoOutput(true);
            connection.setConnectTimeout(30000); // 30 secondes
            connection.setReadTimeout(30000); // 30 secondes
            
            // Envoi des données
            String jsonString = jsonData.toString();
            byte[] input = jsonString.getBytes(StandardCharsets.UTF_8);
            
            try (OutputStream os = connection.getOutputStream()) {
                os.write(input, 0, input.length);
            }
            
            // Vérification de la réponse
            int responseCode = connection.getResponseCode();
            Log.d(TAG, "Code de réponse: " + responseCode);
            
            // Lecture de la réponse pour debug
            String response = "";
            try {
                if (responseCode >= 200 && responseCode < 300) {
                    // Succès
                    java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(connection.getInputStream()));
                    StringBuilder responseBuilder = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        responseBuilder.append(line);
                    }
                    response = responseBuilder.toString();
                    Log.d(TAG, "Réponse succès: " + response);
                } else {
                    // Erreur
                    java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.InputStreamReader(connection.getErrorStream()));
                    StringBuilder responseBuilder = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        responseBuilder.append(line);
                    }
                    response = responseBuilder.toString();
                    Log.e(TAG, "Réponse erreur: " + response);
                }
            } catch (Exception e) {
                Log.e(TAG, "Erreur lecture réponse: " + e.getMessage());
            }
            
            if (responseCode == HttpURLConnection.HTTP_OK || responseCode == HttpURLConnection.HTTP_CREATED) {
                return true;
            } else {
                Log.e(TAG, "Erreur HTTP: " + responseCode + " - " + response);
                return false;
            }
            
        } catch (IOException e) {
            Log.e(TAG, "Erreur de connexion", e);
            return false;
        }
    }
    
    /**
     * Interface de callback pour les réponses API
     */
    public interface ApiCallback {
        void onSuccess(String message);
        void onError(String error);
    }
}
