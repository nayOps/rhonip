package com.onip.biometric.models;

/**
 * Modèle de données pour un enfant d'employé
 */
public class ChildData {
    
    private String firstName;
    private String lastName;
    private String middleName;
    private String gender;
    private String birthPlace;
    private String birthDate;
    private String birthCertificate;
    
    // Constructeur
    public ChildData() {}
    
    public ChildData(String firstName, String lastName, String middleName, 
                    String gender, String birthPlace, String birthDate) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.middleName = middleName;
        this.gender = gender;
        this.birthPlace = birthPlace;
        this.birthDate = birthDate;
    }
    
    // Getters et Setters
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    
    public String getMiddleName() { return middleName; }
    public void setMiddleName(String middleName) { this.middleName = middleName; }
    
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    
    public String getBirthPlace() { return birthPlace; }
    public void setBirthPlace(String birthPlace) { this.birthPlace = birthPlace; }
    
    public String getBirthDate() { return birthDate; }
    public void setBirthDate(String birthDate) { this.birthDate = birthDate; }
    
    public String getBirthCertificate() { return birthCertificate; }
    public void setBirthCertificate(String birthCertificate) { this.birthCertificate = birthCertificate; }
    
    public String getFullName() {
        StringBuilder fullName = new StringBuilder();
        if (firstName != null) fullName.append(firstName);
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
    
    @Override
    public String toString() {
        return getFullName();
    }
}
