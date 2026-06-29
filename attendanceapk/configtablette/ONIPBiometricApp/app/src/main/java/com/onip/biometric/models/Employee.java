package com.onip.biometric.models;

/**
 * Modèle de données pour un employé
 * Correspond à la structure du backend ONIP
 */
public class Employee {
    
    private String id;
    private String nin;
    private String firstName;
    private String lastName;
    private String middleName;
    private String photoPath;
    private String department;
    private String position;
    
    // Constructeur
    public Employee() {
    }
    
    public Employee(String id, String nin, String firstName, String lastName) {
        this.id = id;
        this.nin = nin;
        this.firstName = firstName;
        this.lastName = lastName;
    }
    
    // Getters et Setters
    public String getId() {
        return id;
    }
    
    public void setId(String id) {
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
}

