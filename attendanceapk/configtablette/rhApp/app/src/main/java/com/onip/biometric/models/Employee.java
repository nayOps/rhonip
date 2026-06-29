package com.onip.biometric.models;

import java.util.HashMap;
import java.util.Map;

/**
 * Modèle de données pour un employé
 * Correspond à la structure du backend ONIP
 */
public class Employee {
    
    private int id;
    private String nin;
    private String firstName;
    private String lastName;
    private String middleName;
    private String email;
    private String phoneNumber;
    private String fingerprintTemplate;
    private boolean biometricEnrolled;
    private String photoPath;
    private String department;
    private String position;
    private String role; // 'employee' ou 'super_admin'
    
    // Templates binaires d'empreintes (chargés depuis l'API)
    private Map<String, byte[]> fingerprintTemplates = new HashMap<>();
    
    // Constructeur
    public Employee() {
    }
    
    public Employee(int id, String nin, String firstName, String lastName) {
        this.id = id;
        this.nin = nin;
        this.firstName = firstName;
        this.lastName = lastName;
    }
    
    // Getters et Setters
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
    }
    
    public String getNin() {
        return nin;
    }
    
    public void setNin(String nin) {
        this.nin = nin;
    }
    
    public String getFirstName() {
        return firstName;
    }
    
    public void setFirstName(String firstName) {
        this.firstName = firstName;
    }
    
    public String getLastName() {
        return lastName;
    }
    
    public void setLastName(String lastName) {
        this.lastName = lastName;
    }
    
    public String getMiddleName() {
        return middleName;
    }
    
    public void setMiddleName(String middleName) {
        this.middleName = middleName;
    }
    
    public String getPhotoPath() {
        return photoPath;
    }
    
    public void setPhotoPath(String photoPath) {
        this.photoPath = photoPath;
    }
    
    public String getDepartment() {
        return department;
    }
    
    public void setDepartment(String department) {
        this.department = department;
    }
    
    public String getPosition() {
        return position;
    }
    
    public void setPosition(String position) {
        this.position = position;
    }
    
    public String getRole() {
        return role;
    }
    
    public void setRole(String role) {
        this.role = role;
    }
    
    public boolean isSuperAdmin() {
        return "super_admin".equalsIgnoreCase(role);
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
    
    public String getPhoneNumber() {
        return phoneNumber;
    }
    
    public void setPhoneNumber(String phoneNumber) {
        this.phoneNumber = phoneNumber;
    }
    
    public String getFingerprintTemplate() {
        return fingerprintTemplate;
    }
    
    public void setFingerprintTemplate(String fingerprintTemplate) {
        this.fingerprintTemplate = fingerprintTemplate;
    }
    
    public boolean isBiometricEnrolled() {
        return biometricEnrolled;
    }
    
    public void setBiometricEnrolled(boolean biometricEnrolled) {
        this.biometricEnrolled = biometricEnrolled;
    }
    
    /**
     * Retourne le nom complet de l'employé
     */
    public String getFullName() {
        StringBuilder fullName = new StringBuilder();
        if (firstName != null && !firstName.isEmpty()) {
            fullName.append(firstName);
        }
        if (middleName != null && !middleName.isEmpty()) {
            if (fullName.length() > 0) fullName.append(" ");
            fullName.append(middleName);
        }
        if (lastName != null && !lastName.isEmpty()) {
            if (fullName.length() > 0) fullName.append(" ");
            fullName.append(lastName);
        }
        return fullName.toString();
    }
    
    // Templates binaires d'empreintes
    public Map<String, byte[]> getFingerprintTemplates() {
        return fingerprintTemplates;
    }
    
    public void setFingerprintTemplates(Map<String, byte[]> fingerprintTemplates) {
        this.fingerprintTemplates = fingerprintTemplates != null ? fingerprintTemplates : new HashMap<>();
    }
    
    public void addFingerprintTemplate(String fingerName, byte[] template) {
        if (fingerprintTemplates == null) {
            fingerprintTemplates = new HashMap<>();
        }
        fingerprintTemplates.put(fingerName, template);
    }
    
    public int getTemplateCount() {
        return fingerprintTemplates != null ? fingerprintTemplates.size() : 0;
    }
    
    @Override
    public String toString() {
        return firstName + " " + lastName + " (ID: " + id + ", Templates: " + getTemplateCount() + ")";
    }
}

