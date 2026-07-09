from employee.models import Employee, Child, Education
from django.apps import apps
import json

employees = open('employees.json', mode='rb')
employees = json.loads(employees.read())
employees = employees['F_Form1']
total = len(employees)
data = []

print('Processing')

def return_none_if_whitespace(value):
    return None if value.isspace() else value

def return_object_or_create(app, model, field, value):
    if not value: return None
    model = apps.get_model(app, model_name=model)
    obj, created = model.objects.get_or_create(**{field:value})
    return obj.id

def contains(list, filter):
    for x in list:
        if filter(x):
            return True
    return False

def return_enum_or_value(app, model, field, value):
    if not value: return None
    model = apps.get_model(app, model_name=model)
    choices = model._meta.get_field(field).choices
    for choice in choices:
        if choice[1].lower() != value.lower():
            continue
        return choice[0].lower()
    return value.lower()

for idx, employee in enumerate(employees):
    if 'nomEnfant' in employee:
        continue

    count = idx + 1 
    emp = employee.copy()
    if 'children' not in emp : emp['children'] = []

    while total > count and 'nomEnfant' in employees[count]:
        emp['children'].append(employees[count])
        count = count + 1
    
    data.append(emp)
    
_data = []

for obj in data:
    _data.append(Employee(**{
        'registration_number': obj.get('UID'),
        'social_security_number': None,
        'agreement': None,
        'date_of_join': None,
        'photo': None,
        'designation_id': return_object_or_create('employee', 'designation', 'name', obj.get('fonction', None)),
        'branch': None,
        'grade': None,
        'direction': None,
        'sub_direction': None,
        'service_id': return_object_or_create('employee', 'service', 'name', obj.get('service', None)),
        'first_name': obj.get('prenom', None),
        'middle_name': obj.get('postnom', None),
        'last_name': obj.get('nom', None),
        'gender': return_enum_or_value('employee', 'employee', 'gender', obj.get('sexe', None)),
        'date_of_birth': obj.get('dateNaiss', None),
        'place_of_birth': obj.get('lieuNaiss', None),
        'citizenship': obj.get('nationalite', None),
        'home_country': obj.get('paysOrigine', None),
        'home_province': obj.get('provinceOrigine', None),
        'home_territory': obj.get('territoire', None),
        'home_sector': obj.get('secteur', None),
        'home_village': obj.get('village', None),
        'type_of_identity': return_enum_or_value('employee', 'employee', 'type_of_identity', obj.get('typePieceIdentite', None)),
        'identity_number': obj.get('numeroPiece', None),
        'date_of_issue': obj.get('dateDelivrance', None),
        'date_of_expiry': obj.get('dateExpiration', None),
        'place_of_issue': None,
        'marital_status': return_enum_or_value('employee', 'employee', 'marital_status', obj.get('etatCivil', None)),
        'spouse': return_none_if_whitespace(' '.join([obj.get('prenomConjoint'), obj.get('nomConjoint')])),
        'telephone_number': return_none_if_whitespace(''.join([obj.get('codePays_1'), obj.get('phoneProfessionnel')])),
        'mobile_number': return_none_if_whitespace(''.join([obj.get('codePays'), obj.get('phonePrive')])),
        'email_professional': obj.get('emailProfessionnel', None),
        'email': obj.get('emailPrive', None),
        'appointment_letter': None,
        'appointment_number': obj.get('numeroActe', None),
        'physical_address': obj.get('adressePermanente', None),
        'emergency_information': None,
        'emergency_contact': obj.get('personneContact', None),
        'emergency_phone': return_none_if_whitespace(''.join([obj.get('codePays_2'), obj.get('phonePersonneContact')])),
        'relationship': obj.get('lienParente', None),
        'refering_doctor': obj.get('nomMedecin', None),
        'refering_doctor_phone': return_none_if_whitespace(''.join([obj.get('codePays_3'), obj.get('phoneMedecin')])),
        'refering_doctor_email': obj.get('emailMedecin', None),
        'payment_account': obj.get('numeroCompte', None),
        'payment_method': return_enum_or_value('employee', 'employee', 'payment_method', 'banque'),
        'payer_name': obj.get('banqueAffectation', None),
        'metadata': obj
    }))


# Serializing json
qs = Employee.objects.bulk_create(_data)

# Children & Education
for obj in qs:
    # Children
    children = [Child(**{
        'employee': obj,
        'full_name': ' '.join([child.get('prenomEnfant'), child.get('postnomEnfant'), child.get('nomEnfant')]),
        'date_of_birth': child.get('dateNaissEnfant'),
        'metadata': child
    }) for child in obj.metadata.get('children')]
    Child.objects.bulk_create(children)

    # Education
    meta = obj.metadata or {}
    study_level_raw = (meta.get('niveauEtude') or '').strip() or None
    field_of_study_raw = (meta.get('domaineEtude') or meta.get('domaine') or '').strip() or None
    from employee.models.education_references import FieldOfStudy, StudyLevel
    from employee.utils.education_references import resolve_reference

    study_level = resolve_reference(StudyLevel, study_level_raw) if study_level_raw else None
    field_of_study = resolve_reference(FieldOfStudy, field_of_study_raw) if field_of_study_raw else None
    edu, created = Education.objects.get_or_create(
        employee=obj,
        defaults={
            'institution': None,
            'study_level': study_level,
            'field_of_study': field_of_study,
            'degree': None,
        },
    )

print('Loaded')
