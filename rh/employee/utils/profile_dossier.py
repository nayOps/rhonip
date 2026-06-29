from django.utils.formats import date_format
from django.utils.translation import gettext as _


def _display(value, fallback='—'):
    if value is None or value == '':
        return fallback
    return value


def _format_date(value):
    if not value:
        return '—'
    return date_format(value, 'j F Y')


def build_profile_dossier(employee):
    designation = _display(str(employee.designation) if employee.designation else None)
    direction = _display(str(employee.direction) if employee.direction else None)
    service = _display(str(employee.service) if employee.service else None)
    department_parts = [part for part in (designation, direction or service) if part != '—']
    subtitle = ' — '.join(department_parts) if department_parts else '—'

    grade_label = _display(str(employee.grade) if employee.grade else None)
    status_label = _display(
        employee.get_agent_situation_display() if employee.agent_situation else None
    )

    agreement_label = _display(employee.agreement)
    if employee.agreement and hasattr(employee.agreement, 'name'):
        agreement_label = employee.agreement.name

    site_label = _display(employee.branch)
    if employee.branch and hasattr(employee.branch, 'name'):
        site_label = employee.branch.name

    grade_parts = []
    if employee.grade:
        grade_parts.append(str(employee.grade))
    if employee.designation:
        grade_parts.append(str(employee.designation))
    echelon_grade = ' — '.join(grade_parts) if grade_parts else '—'

    return {
        'subtitle': subtitle,
        'status_badge': status_label,
        'grade_badge': grade_label if grade_label != '—' else None,
        'personal': {
            'full_name': employee.full_name(),
            'citizenship': _display(employee.citizenship),
            'date_of_birth': _format_date(employee.date_of_birth),
            'gender': _display(employee.get_gender_display() if employee.gender else None),
            'place_of_birth': _display(employee.place_of_birth),
            'marital_status': _display(employee.get_marital_status_display() if employee.marital_status else None),
            'spouse': _display(employee.spouse),
        },
        'contact': {
            'address': _display(employee.physical_address),
            'email_professional': _display(employee.email_professional or employee.email),
            'telephone_professional': _display(employee.telephone_number),
            'telephone_personal': _display(employee.mobile_number),
        },
        'emergency': {
            'name': _display(employee.emergency_contact),
            'phone': _display(employee.emergency_phone),
            'relationship': _display(employee.relationship),
            'information': _display(employee.emergency_information, ''),
        },
        'admin': {
            'registration_number': _display(employee.registration_number),
            'social_security_number': _display(employee.social_security_number),
            'site': site_label,
            'direction': direction,
            'sub_direction': _display(str(employee.sub_direction) if employee.sub_direction else None),
            'service': service,
            'agreement': agreement_label,
            'date_of_join': _format_date(employee.date_of_join),
            'onip_start_date': _format_date(employee.onip_start_date),
            'echelon_grade': echelon_grade,
            'appointment_number': _display(employee.appointment_number),
            'type_of_identity': _display(
                employee.get_type_of_identity_display() if employee.type_of_identity else None
            ),
            'identity_number': _display(employee.identity_number),
            'date_of_issue': _format_date(employee.date_of_issue),
            'date_of_expiry': _format_date(employee.date_of_expiry),
            'place_of_issue': _display(employee.place_of_issue),
            'payment_method': _display(
                employee.get_payment_method_display() if employee.payment_method else None
            ),
            'payment_account': _display(employee.payment_account),
        },
    }
