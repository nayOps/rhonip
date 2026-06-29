package com.onip.biometric.models;

import java.util.ArrayList;
import java.util.List;

/**
 * Modèle de données pour un employé
 * Contient tous les champs du formulaire multi-étapes
 */
public class EmployeeData {
    
    // ========== IDENTITÉ ==========
    private String nin;
    private String firstName;
    private String lastName;
    private String middleName;
    private String otherNames;
    private String gender;
    private String birthPlace;
    private String birthDate;
    private String nationality;
    private String eyeColor;
    private String height;
    private String email;
    private String postalAddress;
    private String phoneNumber;
    
    // ========== ORIGINE ==========
    private String originProvince;
    private String originTerritory;
    private String originCommune;
    private String originGroupement;
    private String originVillage;
    
    // ========== ADRESSE ==========
    private String currentProvince;
    private String currentTerritory;
    private String currentCommune;
    private String currentGroupement;
    private String currentVillage;
    
    // ========== SITUATION FAMILIALE ==========
    private String spouseName;
    private String maritalStatus;
    private String spouseFirstName;
    private String spouseLastName;
    private String spouseMiddleName;
    private String spouseBirthPlace;
    private String spouseBirthDate;
    private int numberOfChildren;
    private String marriageCertificate;
    private List<ChildData> children;
    
    // ========== FORMATION ==========
    private String educationLevel;
    private String educationCountry;
    private String educationInstitution;
    private String educationCity;
    private String educationStartYear;
    private String educationEndYear;
    private String educationField;
    private String educationSpecialization;
    private String educationResult;
    private String educationDocumentNumber;
    private String educationDocument;
    
    // ========== PROFESSIONNEL ==========
    private String employeeId;
    private String hireDate;
    private String contractType;
    private String jobTitle;
    private String department;
    private String hierarchyLevel;
    private String supervisor;
    private String professionalCategory;
    private String workLocation;
    private String workStatus;
    
    // ========== DOCUMENTS ==========
    private String nationalIdNumber;
    private String nationalIdDocument;
    private String inssNumber;
    private String taxNumber;
    private String workPermit;
    private String voterCard;
    private String criminalRecord;
    private String identityPhoto;
    private String diplomas;
    
    // ========== URGENCE ==========
    private String emergencyContactName;
    private String emergencyContactAddress;
    private String emergencyContactPhone;
    
    // ========== BANCAIRE ==========
    private String bankName;
    private String bankAccountNumber;
    private String paymentCurrency;
    private String paymentMethod;
    private String grossSalary;
    private String netSalary;
    private String benefits;
    
    // ========== MÉDICAL ==========
    private String bloodType;
    private String allergies;
    private String disabilities;
    private String medicalInsurance;
    private String doctorName;
    
    // ========== ÉQUIPEMENTS ==========
    private String accessBadge;
    private String officeKeys;
    private String workEquipment;
    private String computerAccounts;
    
    // ========== BIOMÉTRIE ==========
    private String photoPath;
    private String fingerprintTemplate;
    private String fingerprintFinger;
    private String biometricEnrollmentDate;
    private boolean biometricEnrolled;
    
    // Constructeur
    public EmployeeData() {
        this.children = new ArrayList<>();
        this.biometricEnrolled = false;
    }
    
    // ========== GETTERS ET SETTERS ==========
    
    // Identité
    public String getNin() { return nin; }
    public void setNin(String nin) { this.nin = nin; }
    
    public String getFirstName() { return firstName; }
    public void setFirstName(String firstName) { this.firstName = firstName; }
    
    public String getLastName() { return lastName; }
    public void setLastName(String lastName) { this.lastName = lastName; }
    
    public String getMiddleName() { return middleName; }
    public void setMiddleName(String middleName) { this.middleName = middleName; }
    
    public String getOtherNames() { return otherNames; }
    public void setOtherNames(String otherNames) { this.otherNames = otherNames; }
    
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    
    public String getBirthPlace() { return birthPlace; }
    public void setBirthPlace(String birthPlace) { this.birthPlace = birthPlace; }
    
    public String getBirthDate() { return birthDate; }
    public void setBirthDate(String birthDate) { this.birthDate = birthDate; }
    
    public String getNationality() { return nationality; }
    public void setNationality(String nationality) { this.nationality = nationality; }
    
    public String getEyeColor() { return eyeColor; }
    public void setEyeColor(String eyeColor) { this.eyeColor = eyeColor; }
    
    public String getHeight() { return height; }
    public void setHeight(String height) { this.height = height; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
    
    public String getPostalAddress() { return postalAddress; }
    public void setPostalAddress(String postalAddress) { this.postalAddress = postalAddress; }
    
    public String getPhoneNumber() { return phoneNumber; }
    public void setPhoneNumber(String phoneNumber) { this.phoneNumber = phoneNumber; }
    
    // Origine
    public String getOriginProvince() { return originProvince; }
    public void setOriginProvince(String originProvince) { this.originProvince = originProvince; }
    
    public String getOriginTerritory() { return originTerritory; }
    public void setOriginTerritory(String originTerritory) { this.originTerritory = originTerritory; }
    
    public String getOriginCommune() { return originCommune; }
    public void setOriginCommune(String originCommune) { this.originCommune = originCommune; }
    
    public String getOriginGroupement() { return originGroupement; }
    public void setOriginGroupement(String originGroupement) { this.originGroupement = originGroupement; }
    
    public String getOriginVillage() { return originVillage; }
    public void setOriginVillage(String originVillage) { this.originVillage = originVillage; }
    
    // Adresse
    public String getCurrentProvince() { return currentProvince; }
    public void setCurrentProvince(String currentProvince) { this.currentProvince = currentProvince; }
    
    public String getCurrentTerritory() { return currentTerritory; }
    public void setCurrentTerritory(String currentTerritory) { this.currentTerritory = currentTerritory; }
    
    public String getCurrentCommune() { return currentCommune; }
    public void setCurrentCommune(String currentCommune) { this.currentCommune = currentCommune; }
    
    public String getCurrentGroupement() { return currentGroupement; }
    public void setCurrentGroupement(String currentGroupement) { this.currentGroupement = currentGroupement; }
    
    public String getCurrentVillage() { return currentVillage; }
    public void setCurrentVillage(String currentVillage) { this.currentVillage = currentVillage; }
    
    // Situation familiale
    public String getSpouseName() { return spouseName; }
    public void setSpouseName(String spouseName) { this.spouseName = spouseName; }
    
    public String getMaritalStatus() { return maritalStatus; }
    public void setMaritalStatus(String maritalStatus) { this.maritalStatus = maritalStatus; }
    
    public String getSpouseFirstName() { return spouseFirstName; }
    public void setSpouseFirstName(String spouseFirstName) { this.spouseFirstName = spouseFirstName; }
    
    public String getSpouseLastName() { return spouseLastName; }
    public void setSpouseLastName(String spouseLastName) { this.spouseLastName = spouseLastName; }
    
    public String getSpouseMiddleName() { return spouseMiddleName; }
    public void setSpouseMiddleName(String spouseMiddleName) { this.spouseMiddleName = spouseMiddleName; }
    
    public String getSpouseBirthPlace() { return spouseBirthPlace; }
    public void setSpouseBirthPlace(String spouseBirthPlace) { this.spouseBirthPlace = spouseBirthPlace; }
    
    public String getSpouseBirthDate() { return spouseBirthDate; }
    public void setSpouseBirthDate(String spouseBirthDate) { this.spouseBirthDate = spouseBirthDate; }
    
    public int getNumberOfChildren() { return numberOfChildren; }
    public void setNumberOfChildren(int numberOfChildren) { this.numberOfChildren = numberOfChildren; }
    
    public String getMarriageCertificate() { return marriageCertificate; }
    public void setMarriageCertificate(String marriageCertificate) { this.marriageCertificate = marriageCertificate; }
    
    public List<ChildData> getChildren() { return children; }
    public void setChildren(List<ChildData> children) { this.children = children; }
    
    // Formation
    public String getEducationLevel() { return educationLevel; }
    public void setEducationLevel(String educationLevel) { this.educationLevel = educationLevel; }
    
    public String getEducationCountry() { return educationCountry; }
    public void setEducationCountry(String educationCountry) { this.educationCountry = educationCountry; }
    
    public String getEducationInstitution() { return educationInstitution; }
    public void setEducationInstitution(String educationInstitution) { this.educationInstitution = educationInstitution; }
    
    public String getEducationCity() { return educationCity; }
    public void setEducationCity(String educationCity) { this.educationCity = educationCity; }
    
    public String getEducationStartYear() { return educationStartYear; }
    public void setEducationStartYear(String educationStartYear) { this.educationStartYear = educationStartYear; }
    
    public String getEducationEndYear() { return educationEndYear; }
    public void setEducationEndYear(String educationEndYear) { this.educationEndYear = educationEndYear; }
    
    public String getEducationField() { return educationField; }
    public void setEducationField(String educationField) { this.educationField = educationField; }
    
    public String getEducationSpecialization() { return educationSpecialization; }
    public void setEducationSpecialization(String educationSpecialization) { this.educationSpecialization = educationSpecialization; }
    
    public String getEducationResult() { return educationResult; }
    public void setEducationResult(String educationResult) { this.educationResult = educationResult; }
    
    public String getEducationDocumentNumber() { return educationDocumentNumber; }
    public void setEducationDocumentNumber(String educationDocumentNumber) { this.educationDocumentNumber = educationDocumentNumber; }
    
    public String getEducationDocument() { return educationDocument; }
    public void setEducationDocument(String educationDocument) { this.educationDocument = educationDocument; }
    
    // Professionnel
    public String getEmployeeId() { return employeeId; }
    public void setEmployeeId(String employeeId) { this.employeeId = employeeId; }
    
    public String getHireDate() { return hireDate; }
    public void setHireDate(String hireDate) { this.hireDate = hireDate; }
    
    public String getContractType() { return contractType; }
    public void setContractType(String contractType) { this.contractType = contractType; }
    
    public String getJobTitle() { return jobTitle; }
    public void setJobTitle(String jobTitle) { this.jobTitle = jobTitle; }
    
    public String getDepartment() { return department; }
    public void setDepartment(String department) { this.department = department; }
    
    public String getHierarchyLevel() { return hierarchyLevel; }
    public void setHierarchyLevel(String hierarchyLevel) { this.hierarchyLevel = hierarchyLevel; }
    
    public String getSupervisor() { return supervisor; }
    public void setSupervisor(String supervisor) { this.supervisor = supervisor; }
    
    public String getProfessionalCategory() { return professionalCategory; }
    public void setProfessionalCategory(String professionalCategory) { this.professionalCategory = professionalCategory; }
    
    public String getWorkLocation() { return workLocation; }
    public void setWorkLocation(String workLocation) { this.workLocation = workLocation; }
    
    public String getWorkStatus() { return workStatus; }
    public void setWorkStatus(String workStatus) { this.workStatus = workStatus; }
    
    // Documents
    public String getNationalIdNumber() { return nationalIdNumber; }
    public void setNationalIdNumber(String nationalIdNumber) { this.nationalIdNumber = nationalIdNumber; }
    
    public String getNationalIdDocument() { return nationalIdDocument; }
    public void setNationalIdDocument(String nationalIdDocument) { this.nationalIdDocument = nationalIdDocument; }
    
    public String getInssNumber() { return inssNumber; }
    public void setInssNumber(String inssNumber) { this.inssNumber = inssNumber; }
    
    public String getTaxNumber() { return taxNumber; }
    public void setTaxNumber(String taxNumber) { this.taxNumber = taxNumber; }
    
    public String getWorkPermit() { return workPermit; }
    public void setWorkPermit(String workPermit) { this.workPermit = workPermit; }
    
    public String getVoterCard() { return voterCard; }
    public void setVoterCard(String voterCard) { this.voterCard = voterCard; }
    
    public String getCriminalRecord() { return criminalRecord; }
    public void setCriminalRecord(String criminalRecord) { this.criminalRecord = criminalRecord; }
    
    public String getIdentityPhoto() { return identityPhoto; }
    public void setIdentityPhoto(String identityPhoto) { this.identityPhoto = identityPhoto; }
    
    public String getDiplomas() { return diplomas; }
    public void setDiplomas(String diplomas) { this.diplomas = diplomas; }
    
    // Urgence
    public String getEmergencyContactName() { return emergencyContactName; }
    public void setEmergencyContactName(String emergencyContactName) { this.emergencyContactName = emergencyContactName; }
    
    public String getEmergencyContactAddress() { return emergencyContactAddress; }
    public void setEmergencyContactAddress(String emergencyContactAddress) { this.emergencyContactAddress = emergencyContactAddress; }
    
    public String getEmergencyContactPhone() { return emergencyContactPhone; }
    public void setEmergencyContactPhone(String emergencyContactPhone) { this.emergencyContactPhone = emergencyContactPhone; }
    
    // Bancaire
    public String getBankName() { return bankName; }
    public void setBankName(String bankName) { this.bankName = bankName; }
    
    public String getBankAccountNumber() { return bankAccountNumber; }
    public void setBankAccountNumber(String bankAccountNumber) { this.bankAccountNumber = bankAccountNumber; }
    
    public String getPaymentCurrency() { return paymentCurrency; }
    public void setPaymentCurrency(String paymentCurrency) { this.paymentCurrency = paymentCurrency; }
    
    public String getPaymentMethod() { return paymentMethod; }
    public void setPaymentMethod(String paymentMethod) { this.paymentMethod = paymentMethod; }
    
    public String getGrossSalary() { return grossSalary; }
    public void setGrossSalary(String grossSalary) { this.grossSalary = grossSalary; }
    
    public String getNetSalary() { return netSalary; }
    public void setNetSalary(String netSalary) { this.netSalary = netSalary; }
    
    public String getBenefits() { return benefits; }
    public void setBenefits(String benefits) { this.benefits = benefits; }
    
    // Médical
    public String getBloodType() { return bloodType; }
    public void setBloodType(String bloodType) { this.bloodType = bloodType; }
    
    public String getAllergies() { return allergies; }
    public void setAllergies(String allergies) { this.allergies = allergies; }
    
    public String getDisabilities() { return disabilities; }
    public void setDisabilities(String disabilities) { this.disabilities = disabilities; }
    
    public String getMedicalInsurance() { return medicalInsurance; }
    public void setMedicalInsurance(String medicalInsurance) { this.medicalInsurance = medicalInsurance; }
    
    public String getDoctorName() { return doctorName; }
    public void setDoctorName(String doctorName) { this.doctorName = doctorName; }
    
    // Équipements
    public String getAccessBadge() { return accessBadge; }
    public void setAccessBadge(String accessBadge) { this.accessBadge = accessBadge; }
    
    public String getOfficeKeys() { return officeKeys; }
    public void setOfficeKeys(String officeKeys) { this.officeKeys = officeKeys; }
    
    public String getWorkEquipment() { return workEquipment; }
    public void setWorkEquipment(String workEquipment) { this.workEquipment = workEquipment; }
    
    public String getComputerAccounts() { return computerAccounts; }
    public void setComputerAccounts(String computerAccounts) { this.computerAccounts = computerAccounts; }
    
    // Biométrie
    public String getPhotoPath() { return photoPath; }
    public void setPhotoPath(String photoPath) { this.photoPath = photoPath; }
    
    public String getFingerprintTemplate() { return fingerprintTemplate; }
    public void setFingerprintTemplate(String fingerprintTemplate) { this.fingerprintTemplate = fingerprintTemplate; }
    
    public String getFingerprintFinger() { return fingerprintFinger; }
    public void setFingerprintFinger(String fingerprintFinger) { this.fingerprintFinger = fingerprintFinger; }
    
    public String getBiometricEnrollmentDate() { return biometricEnrollmentDate; }
    public void setBiometricEnrollmentDate(String biometricEnrollmentDate) { this.biometricEnrollmentDate = biometricEnrollmentDate; }
    
    public boolean isBiometricEnrolled() { return biometricEnrolled; }
    public void setBiometricEnrolled(boolean biometricEnrolled) { this.biometricEnrolled = biometricEnrolled; }
    
    // Méthodes utilitaires
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
    
    public boolean isComplete() {
        return firstName != null && !firstName.isEmpty() &&
               lastName != null && !lastName.isEmpty() &&
               email != null && !email.isEmpty() &&
               phoneNumber != null && !phoneNumber.isEmpty();
    }
}
