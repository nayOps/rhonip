package com.onip.fingerprinttest;

public class Employee {
    private int id;
    private String firstName;
    private String lastName;
    private String nin;
    private String email;
    private String phoneNumber;
    private String fingerprintTemplate;
    private boolean biometricEnrolled;
    
    public Employee() {}
    
    public int getId() {
        return id;
    }
    
    public void setId(int id) {
        this.id = id;
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
    
    public String getNin() {
        return nin;
    }
    
    public void setNin(String nin) {
        this.nin = nin;
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
    
    @Override
    public String toString() {
        return firstName + " " + lastName + " (ID: " + id + ")";
    }
}

