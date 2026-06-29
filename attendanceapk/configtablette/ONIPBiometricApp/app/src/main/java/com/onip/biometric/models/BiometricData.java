package com.onip.biometric.models;

/**
 * Modèle pour les données biométriques
 */
public class BiometricData {
    
    private String employeeId;
    private byte[] photoData;
    private byte[] fingerprintTemplate;
    private int fingerIndex; // 0: Index Gauche, 1: Index Droit, 2: Pouce Gauche, 3: Pouce Droit
    private long timestamp;
    
    public BiometricData() {
        this.timestamp = System.currentTimeMillis();
    }
    
    public String getEmployeeId() {
        return employeeId;
    }
    
    public void setEmployeeId(String employeeId) {
        this.employeeId = employeeId;
    }
    
    public byte[] getPhotoData() {
        return photoData;
    }
    
    public void setPhotoData(byte[] photoData) {
        this.photoData = photoData;
    }
    
    public byte[] getFingerprintTemplate() {
        return fingerprintTemplate;
    }
    
    public void setFingerprintTemplate(byte[] fingerprintTemplate) {
        this.fingerprintTemplate = fingerprintTemplate;
    }
    
    public int getFingerIndex() {
        return fingerIndex;
    }
    
    public void setFingerIndex(int fingerIndex) {
        this.fingerIndex = fingerIndex;
    }
    
    public long getTimestamp() {
        return timestamp;
    }
    
    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }
    
    /**
     * Retourne le nom du doigt basé sur l'index
     */
    public String getFingerName() {
        switch (fingerIndex) {
            case 0: return "Index Gauche";
            case 1: return "Index Droit";
            case 2: return "Pouce Gauche";
            case 3: return "Pouce Droit";
            default: return "Doigt " + fingerIndex;
        }
    }
}

