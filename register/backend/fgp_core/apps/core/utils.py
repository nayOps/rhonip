"""
Utilitaires pour l'application Core
"""
import random
import string
from datetime import datetime
from django.conf import settings


def generate_nin_number():
    """
    Génère un nouveau numéro NIN (Numéro d'Identification Nationale)
    Format: CD-YYYY-NNNN-NNNNNNN (20 caractères en base)
    """
    year = datetime.now().year
    sequence = random.randint(1000, 9999)
    unique_number = random.randint(1000000, 9999999)  # 7 chiffres
    return f"CD-{year}-{sequence:04d}-{unique_number:07d}"


def validate_nin_format(nin):
    """
    Valide le format d'un NIN
    """
    import re
    pattern = r'^CD-\d{4}-\d{4}-\d{7}$'
    return bool(re.match(pattern, nin))


def generate_document_hash(file_content):
    """
    Génère un hash SHA-256 pour un document
    """
    import hashlib
    return hashlib.sha256(file_content).hexdigest()


def validate_phone_number(phone):
    """
    Valide un numéro de téléphone congolais
    """
    import re
    # Format: +243XXXXXXXXX (12 chiffres après +243)
    pattern = r'^\+243[0-9]{9}$'
    return bool(re.match(pattern, phone))


def normalize_phone_number(phone):
    """
    Normalise un numéro de téléphone
    """
    # Supprimer tous les espaces et caractères non numériques sauf +
    import re
    cleaned = re.sub(r'[^\d+]', '', phone)
    
    # Si commence par 243, ajouter +
    if cleaned.startswith('243'):
        cleaned = '+' + cleaned
    
    # Si commence par 0, remplacer par +243
    if cleaned.startswith('0'):
        cleaned = '+243' + cleaned[1:]
    
    return cleaned


def get_province_choices():
    """
    Retourne les choix de provinces de la RDC
    """
    return [
        ('Kinshasa', 'Kinshasa'),
        ('Kongo-Central', 'Kongo-Central'),
        ('Kwango', 'Kwango'),
        ('Kwilu', 'Kwilu'),
        ('Mai-Ndombe', 'Mai-Ndombe'),
        ('Kasaï', 'Kasaï'),
        ('Kasaï-Central', 'Kasaï-Central'),
        ('Kasaï-Oriental', 'Kasaï-Oriental'),
        ('Lomami', 'Lomami'),
        ('Sankuru', 'Sankuru'),
        ('Maniema', 'Maniema'),
        ('Sud-Kivu', 'Sud-Kivu'),
        ('Nord-Kivu', 'Nord-Kivu'),
        ('Ituri', 'Ituri'),
        ('Haut-Uele', 'Haut-Uele'),
        ('Tshopo', 'Tshopo'),
        ('Bas-Uele', 'Bas-Uele'),
        ('Nord-Ubangi', 'Nord-Ubangi'),
        ('Mongala', 'Mongala'),
        ('Sud-Ubangi', 'Sud-Ubangi'),
        ('Equateur', 'Equateur'),
        ('Tshuapa', 'Tshuapa'),
        ('Tanganyika', 'Tanganyika'),
        ('Haut-Lomami', 'Haut-Lomami'),
        ('Lualaba', 'Lualaba'),
        ('Haut-Katanga', 'Haut-Katanga'),
    ]


def get_territory_choices(province=None):
    """
    Retourne les choix de territoires selon la province
    """
    territories = {
        'Kinshasa': [
            ('Funa', 'Funa'),
            ('Lukunga', 'Lukunga'),
            ('Mont-Amba', 'Mont-Amba'),
            ('Tshangu', 'Tshangu'),
        ],
        'Kongo-Central': [
            ('Boma', 'Boma'),
            ('Matadi', 'Matadi'),
            ('Mbanza-Ngungu', 'Mbanza-Ngungu'),
            ('Songololo', 'Songololo'),
        ],
        # Ajouter d'autres provinces selon les besoins
    }
    
    if province:
        return territories.get(province, [])
    
    # Retourner tous les territoires si aucune province spécifiée
    all_territories = []
    for prov_territories in territories.values():
        all_territories.extend(prov_territories)
    return all_territories


def calculate_age(birth_date):
    """
    Calcule l'âge en années à partir d'une date de naissance
    """
    from datetime import date
    today = date.today()
    return today.year - birth_date.year - (
        (today.month, today.day) < (birth_date.month, birth_date.day)
    )


def is_adult(birth_date):
    """
    Vérifie si une personne est majeure (18 ans et plus)
    """
    return calculate_age(birth_date) >= 18


def format_address(province, territoire=None, commune=None, quartier=None, avenue=None, numero=None):
    """
    Formate une adresse complète
    """
    parts = []
    if numero:
        parts.append(numero)
    if avenue:
        parts.append(avenue)
    if quartier:
        parts.append(quartier)
    if commune:
        parts.append(commune)
    if territoire:
        parts.append(territoire)
    if province:
        parts.append(province)
    
    return ', '.join(parts)


def get_strate_choices():
    """
    Retourne les choix de strates
    """
    return [
        ('ELEVES', 'Élèves'),
        ('ETUDIANTS', 'Étudiants'),
        ('ELECTEURS', 'Électeurs'),
        ('PNC', 'Police Nationale Congolaise'),
        ('FARDC', 'Forces Armées'),
        ('PRISON', 'Prisonniers'),
        ('REFUGIE', 'Réfugiés/Apatrides'),
        ('ENFANT', 'Enfants'),
        ('FONCTIONNAIRE', 'Fonctionnaires'),
    ]


def get_document_type_choices():
    """
    Retourne les choix de types de documents
    """
    return [
        ('acte_naissance', 'Acte de naissance'),
        ('carte_identite', 'Carte d\'identité'),
        ('passeport', 'Passeport'),
        ('diplome', 'Diplôme'),
        ('attestation', 'Attestation'),
        ('autre', 'Autre'),
    ]


def validate_file_size(file_size, max_size=None):
    """
    Valide la taille d'un fichier
    """
    if max_size is None:
        max_size = getattr(settings, 'FGP_SETTINGS', {}).get('MAX_FILE_SIZE', 10 * 1024 * 1024)
    
    return file_size <= max_size


def validate_file_type(file_name, allowed_types=None):
    """
    Valide le type d'un fichier
    """
    if allowed_types is None:
        allowed_types = getattr(settings, 'FGP_SETTINGS', {}).get('ALLOWED_DOCUMENT_FORMATS', ['PDF', 'JPEG', 'PNG', 'JPG'])
    
    import os
    file_ext = os.path.splitext(file_name)[1].upper().lstrip('.')
    return file_ext in allowed_types
