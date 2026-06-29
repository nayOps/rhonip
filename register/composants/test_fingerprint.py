#!/usr/bin/env python3
"""
Script de test pour le lecteur d'empreintes
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from modules.fingerprint import USBFingerprintReader, SerialFingerprintReader, FingerprintMatcher
from modules.database import BiometricDatabase
import time


def test_usb_reader():
    """Test du lecteur USB"""
    print("\n" + "="*60)
    print("TEST LECTEUR D'EMPREINTES USB")
    print("="*60)
    
    with USBFingerprintReader() as reader:
        if not reader.connected:
            print("\n⚠️  Lecteur non connecté.")
            print("Vérifiez que:")
            print("  1. Le lecteur est branché")
            print("  2. Les IDs USB sont corrects dans config.json")
            print("  3. Vous avez les permissions (ajoutez-vous au groupe plugdev)")
            return False
        
        # Initialiser
        reader.initialize_sensor()
        
        # Capturer une empreinte
        image = reader.capture_fingerprint(timeout=15)
        
        if image is not None:
            # Sauvegarder l'image
            filename = f"data/fingerprint_{int(time.time())}.png"
            reader.save_image(image, filename)
            
            # Extraire le template
            template = reader.extract_template(image)
            
            if template:
                print(f"\n✅ Test réussi!")
                print(f"   Qualité: {template.get('quality', 'N/A')}")
                return True
        
        print("\n❌ Test échoué")
        return False


def test_serial_reader():
    """Test du lecteur série"""
    print("\n" + "="*60)
    print("TEST LECTEUR D'EMPREINTES SÉRIE")
    print("="*60)
    
    with SerialFingerprintReader() as reader:
        if not reader.connected:
            print("\n⚠️  Port série non connecté.")
            print("Vérifiez que:")
            print("  1. Le lecteur est branché")
            print("  2. Le port est correct dans config.json")
            print("  3. Vous avez les permissions sur /dev/ttyUSB*")
            return False
        
        # Vérifier le mot de passe
        if not reader.verify_password():
            print("⚠️  Mot de passe incorrect (essayez le défaut: 0x00000000)")
        
        # Enregistrement complet
        template = reader.enroll_fingerprint()
        
        if template:
            print(f"\n✅ Test réussi!")
            return True
        
        print("\n❌ Test échoué")
        return False


def test_matcher():
    """Test du matcher d'empreintes"""
    print("\n" + "="*60)
    print("TEST MATCHER D'EMPREINTES")
    print("="*60)
    
    matcher = FingerprintMatcher(threshold=0.4)
    
    # Créer deux templates de test
    print("\n📸 Capturez la même empreinte deux fois pour tester...")
    
    with USBFingerprintReader() as reader:
        if not reader.connected:
            print("❌ Lecteur non connecté")
            return False
        
        # Première capture
        print("\n1️⃣  Première capture...")
        img1 = reader.capture_fingerprint(timeout=15)
        if img1 is None:
            return False
        
        template1 = reader.extract_template(img1)
        
        print("\n⏳ Retirez votre doigt...")
        time.sleep(2)
        
        # Deuxième capture
        print("\n2️⃣  Deuxième capture (même doigt)...")
        img2 = reader.capture_fingerprint(timeout=15)
        if img2 is None:
            return False
        
        template2 = reader.extract_template(img2)
    
    # Comparer
    if template1 and template2:
        is_match, score = matcher.compare_templates(template1, template2)
        
        print(f"\n📊 Résultat de la comparaison:")
        print(f"   Match: {'✅ OUI' if is_match else '❌ NON'}")
        print(f"   Score: {score:.2%}")
        
        return True
    
    return False


def test_database():
    """Test de la base de données"""
    print("\n" + "="*60)
    print("TEST BASE DE DONNÉES")
    print("="*60)
    
    with BiometricDatabase('test_biometric.db') as db:
        # Créer un utilisateur de test
        user_id = db.add_user("Test User")
        
        # Créer un template fictif
        template = {
            'minutiae': [
                {'x': 100, 'y': 150, 'type': 'ending', 'angle': 45},
                {'x': 200, 'y': 250, 'type': 'bifurcation', 'angle': 90}
            ],
            'image_shape': (288, 256),
            'quality': 75
        }
        
        # Ajouter une empreinte
        fp_id = db.add_fingerprint(user_id, template, finger_index=1, quality_score=75)
        
        # Récupérer
        fingerprints = db.get_fingerprints(user_id)
        
        print(f"\n✅ Test réussi!")
        print(f"   Utilisateur créé: ID {user_id}")
        print(f"   Empreintes: {len(fingerprints)}")
        
        # Nettoyer
        db.delete_user(user_id)
        
        return True


def main():
    """Test principal"""
    print("\n" + "="*70)
    print(" 👆 TESTS LECTEUR D'EMPREINTES DIGITALES")
    print("="*70)
    
    # Menu
    print("\nChoisissez un test:")
    print("  1. Test lecteur USB")
    print("  2. Test lecteur série")
    print("  3. Test matcher (comparaison)")
    print("  4. Test base de données")
    print("  5. Tous les tests")
    print("  0. Quitter")
    
    choice = input("\nVotre choix: ").strip()
    
    if choice == '1':
        test_usb_reader()
    elif choice == '2':
        test_serial_reader()
    elif choice == '3':
        test_matcher()
    elif choice == '4':
        test_database()
    elif choice == '5':
        print("\n🔄 Exécution de tous les tests...\n")
        results = {
            'USB': test_usb_reader(),
            'Série': test_serial_reader(),
            'Matcher': test_matcher(),
            'Database': test_database()
        }
        
        print("\n" + "="*60)
        print("RÉSUMÉ DES TESTS")
        print("="*60)
        for name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{name:15} {status}")
    elif choice == '0':
        print("Au revoir!")
        return
    else:
        print("❌ Choix invalide")
    
    print("\n" + "="*70)
    print("Tests terminés!")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Programme interrompu")
        sys.exit(0)

