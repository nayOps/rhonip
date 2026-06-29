"""Sérialisation employé RH → formulaire guichet register."""
from __future__ import annotations


def employee_to_guichet_form(employee) -> dict:
    meta = employee.metadata or {}
    payroll = meta.get('payroll') or {}
    payroll_summary = payroll.get(next(iter(payroll), ''), {}) if payroll else {}

    designation_name = None
    if employee.designation_id and employee.designation:
        designation_name = employee.designation.name

    return {
        'employee_id': employee.id,
        'registration_number': employee.registration_number,
        'social_security_number': employee.social_security_number,
        'first_name': employee.first_name,
        'middle_name': employee.middle_name,
        'last_name': employee.last_name,
        'gender': employee.gender,
        'marital_status': employee.marital_status,
        'date_of_birth': employee.date_of_birth.isoformat() if employee.date_of_birth else None,
        'place_of_birth': employee.place_of_birth,
        'citizenship': employee.citizenship,
        'home_country': employee.home_country,
        'home_province': employee.home_province_id,
        'home_province_name': employee.home_province.name if employee.home_province_id else None,
        'home_territory': employee.home_territory_id,
        'home_territory_name': employee.home_territory.name if employee.home_territory_id else None,
        'home_sector': employee.home_sector_id,
        'home_sector_name': employee.home_sector.name if employee.home_sector_id else None,
        'home_groupement': employee.home_groupement_id,
        'home_groupement_name': employee.home_groupement.name if employee.home_groupement_id else None,
        'home_village': employee.home_village_id,
        'home_village_name': employee.home_village.name if employee.home_village_id else None,
        'type_of_identity': employee.type_of_identity,
        'identity_number': employee.identity_number,
        'date_of_issue': employee.date_of_issue.isoformat() if employee.date_of_issue else None,
        'date_of_expiry': employee.date_of_expiry.isoformat() if employee.date_of_expiry else None,
        'place_of_issue': employee.place_of_issue,
        'branch': employee.branch_id,
        'agreement': employee.agreement_id,
        'date_of_join': employee.date_of_join.isoformat() if employee.date_of_join else None,
        'onip_start_date': employee.onip_start_date.isoformat() if employee.onip_start_date else None,
        'direction': employee.direction_id,
        'sub_direction': employee.sub_direction_id,
        'service': employee.service_id,
        'grade': employee.grade_id,
        'designation': employee.designation_id,
        'designation_name': designation_name,
        'telephone_number': str(employee.telephone_number) if employee.telephone_number else None,
        'mobile_number': str(employee.mobile_number) if employee.mobile_number else None,
        'email_professional': employee.email_professional,
        'email': employee.email,
        'physical_address': employee.physical_address,
        'emergency_contact': employee.emergency_contact,
        'emergency_phone': str(employee.emergency_phone) if employee.emergency_phone else None,
        'relationship': employee.relationship,
        'emergency_information': employee.emergency_information,
        'refering_doctor': employee.refering_doctor,
        'refering_doctor_phone': str(employee.refering_doctor_phone) if employee.refering_doctor_phone else None,
        'refering_doctor_email': employee.refering_doctor_email,
        'payment_method': employee.payment_method,
        'payer_name': employee.payer_name,
        'payment_account': employee.payment_account,
        'comment': employee.comment,
        'nom_postnom': meta.get('nom_postnom'),
        'payroll': payroll,
        'payroll_summary': payroll_summary,
    }
