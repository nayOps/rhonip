#!/usr/bin/env python3
"""
Script de test pour le lecteur d'iris
"""

import sys
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from modules.iris import IrisCamera, IrisSegmentation, IrisMatcher
from modules.database import BiometricDatabase
import cv2
import time


def test_camera():
    """Test de la caméra"""
    print("\n" + "="*60)
    print("TEST CAMÉRA IRIS")
    print("="*60)
    
    with IrisCamera() as camera:
        if not camera.connected:
            print("\n⚠️  Caméra non connectée.")
            print("Vérifiez que:")
            print("  1. Une caméra est branchée")
            print("  2. L'index de caméra est correct dans config.json")
            print("  3. Vous avez les permissions sur /dev/video*")
            return False
        
        # Capturer un iris
        capture = camera.capture_iris(timeout=30, preview=True)
        
        if capture:
            # Sauvegarder les images
            timestamp = int(time.time())
            camera.save_image(capture['full_frame'], 
                            f"data/iris_full_{timestamp}.jpg")
            camera.save_image(capture['eye_region'], 
                            f"data/iris_eye_{timestamp}.jpg")
            
            print(f"\n✅ Test réussi!")
            return True
        
        print("\n❌ Test échoué")
        return False


def test_segmentation():
    """Test de la segmentation d'iris"""
    print("\n" + "="*60)
    print("TEST SEGMENTATION IRIS")
    print("="*60)
    
    segmenter = IrisSegmentation(min_radius=30, max_radius=120)
    
    with IrisCamera() as camera:
        if not camera.connected:
            print("❌ Caméra non connectée")
            return False
        
        # Capturer
        print("\n👁️  Positionnez votre œil...")
        capture = camera.capture_iris(timeout=30, preview=True)
        
        if not capture:
            return False
        
        eye_region = capture['eye_region']
        
        # Segmenter
        print("\n🔍 Segmentation en cours...")
        segmentation = segmenter.segment_iris(eye_region)
        
        if segmentation:
            # Vérifier la qualité
            quality = segmenter.check_quality(segmentation, eye_region)
            
            print(f"\n📊 Résultats:")
            print(f"   Iris détecté: {'✅ OUI' if segmentation['iris'] else '❌ NON'}")
            print(f"   Pupille détectée: {'✅ OUI' if segmentation['pupil'] else '❌ NON'}")
            print(f"   Qualité globale: {quality['overall']:.2%}")
            print(f"   Valide: {'✅ OUI' if quality['valid'] else '❌ NON'}")
            
            # Visualiser
            vis = segmenter.visualize_segmentation(eye_region, segmentation)
            cv2.imshow('Segmentation', vis)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            
            # Sauvegarder
            timestamp = int(time.time())
            cv2.imwrite(f"data/iris_segmented_{timestamp}.jpg", vis)
            
            # Normaliser
            normalized = segmenter.normalize_iris(eye_region, segmentation)
            if normalized is not None:
                cv2.imwrite(f"data/iris_normalized_{timestamp}.jpg", normalized)
                print(f"\n✅ Iris normalisé sauvegardé")
            
            return True
        
        print("\n❌ Segmentation échouée")
        return False


def test_matcher():
    """Test du matcher d'iris"""
    print("\n" + "="*60)
    print("TEST MATCHER IRIS")
    print("="*60)
    
    segmenter = IrisSegmentation()
    matcher = IrisMatcher(threshold=0.35)
    
    # Capturer deux iris
    print("\n📸 Capturez le même œil deux fois pour tester...")
    
    with IrisCamera() as camera:
        if not camera.connected:
            print("❌ Caméra non connectée")
            return False
        
        # Première capture
        print("\n1️⃣  Première capture...")
        capture1 = camera.capture_iris(timeout=30, preview=True)
        if not capture1:
            return False
        
        seg1 = segmenter.segment_iris(capture1['eye_region'])
        if not seg1:
            print("❌ Segmentation 1 échouée")
            return False
        
        norm1 = segmenter.normalize_iris(capture1['eye_region'], seg1)
        if norm1 is None:
            return False
        
        print("⏳ Clignez des yeux et repositionnez-vous...")
        time.sleep(3)
        
        # Deuxième capture
        print("\n2️⃣  Deuxième capture (même œil)...")
        capture2 = camera.capture_iris(timeout=30, preview=True)
        if not capture2:
            return False
        
        seg2 = segmenter.segment_iris(capture2['eye_region'])
        if not seg2:
            print("❌ Segmentation 2 échouée")
            return False
        
        norm2 = segmenter.normalize_iris(capture2['eye_region'], seg2)
        if norm2 is None:
            return False
    
    # Encoder
    print("\n🔄 Encodage des iris...")
    template1 = matcher.encode_iris(norm1)
    template2 = matcher.encode_iris(norm2)
    
    if template1 and template2:
        # Comparer
        is_match, score = matcher.compare_templates(template1, template2)
        
        print(f"\n📊 Résultat de la comparaison:")
        print(f"   Match: {'✅ OUI' if is_match else '❌ NON'}")
        print(f"   Score: {score:.2%}")
        
        return True
    
    return False


def test_full_pipeline():
    """Test du pipeline complet (capture → segmentation → encodage → comparaison)"""
    print("\n" + "="*60)
    print("TEST PIPELINE COMPLET IRIS")
    print("="*60)
    
    camera = IrisCamera()
    segmenter = IrisSegmentation()
    matcher = IrisMatcher()
    
    def capture_and_encode(label):
        """Capture et encode un iris"""
        print(f"\n{label}")
        
        if not camera.connected:
            camera.connect()
        
        # Capturer
        capture = camera.capture_iris(timeout=30, preview=True)
        if not capture:
            return None
        
        # Segmenter
        segmentation = segmenter.segment_iris(capture['eye_region'])
        if not segmentation:
            print("❌ Segmentation échouée")
            return None
        
        # Vérifier la qualité
        quality = segmenter.check_quality(segmentation, capture['eye_region'])
        if not quality['valid']:
            print("❌ Qualité insuffisante")
            return None
        
        # Normaliser
        normalized = segmenter.normalize_iris(capture['eye_region'], segmentation)
        if normalized is None:
            return None
        
        # Encoder
        template = matcher.encode_iris(normalized)
        
        return template
    
    # Capturer plusieurs iris
    print("\n📝 Enregistrement de 2 échantillons...")
    
    template1 = capture_and_encode("1️⃣  Premier échantillon")
    if not template1:
        camera.disconnect()
        return False
    
    time.sleep(2)
    
    template2 = capture_and_encode("2️⃣  Deuxième échantillon (même œil)")
    if not template2:
        camera.disconnect()
        return False
    
    time.sleep(2)
    
    # Vérification
    print("\n🔍 Test de vérification...")
    template_verify = capture_and_encode("🔍 Capture pour vérification")
    
    camera.disconnect()
    
    if not template_verify:
        return False
    
    # Comparer avec les échantillons enregistrés
    database = [template1, template2]
    
    match_idx, score = matcher.match(template_verify, database)
    
    print(f"\n📊 Résultat:")
    if match_idx is not None:
        print(f"   ✅ Match trouvé (échantillon #{match_idx + 1})")
        print(f"   Score: {score:.2%}")
    else:
        print(f"   ❌ Aucun match")
        print(f"   Meilleur score: {score:.2%}")
    
    return True


def test_database():
    """Test de la base de données pour iris"""
    print("\n" + "="*60)
    print("TEST BASE DE DONNÉES IRIS")
    print("="*60)
    
    with BiometricDatabase('test_biometric.db') as db:
        # Créer un utilisateur de test
        user_id = db.add_user("Test Iris User")
        
        # Créer un template fictif
        import numpy as np
        template = {
            'code': np.random.randint(0, 2, (8, 64, 256), dtype=np.uint8),
            'mask': np.ones((64, 256), dtype=np.uint8),
            'shape': (8, 64, 256),
            'method': 'gabor_phase'
        }
        
        # Ajouter un iris
        iris_id = db.add_iris(user_id, template, eye='left', quality_score=0.85)
        
        # Récupérer
        iris_list = db.get_iris(user_id)
        
        print(f"\n✅ Test réussi!")
        print(f"   Utilisateur créé: ID {user_id}")
        print(f"   Iris: {len(iris_list)}")
        
        # Nettoyer
        db.delete_user(user_id)
        
        return True


def main():
    """Test principal"""
    print("\n" + "="*70)
    print(" 👁️  TESTS LECTEUR D'IRIS")
    print("="*70)
    
    # Menu
    print("\nChoisissez un test:")
    print("  1. Test caméra")
    print("  2. Test segmentation")
    print("  3. Test matcher (comparaison)")
    print("  4. Test pipeline complet")
    print("  5. Test base de données")
    print("  6. Tous les tests")
    print("  0. Quitter")
    
    choice = input("\nVotre choix: ").strip()
    
    if choice == '1':
        test_camera()
    elif choice == '2':
        test_segmentation()
    elif choice == '3':
        test_matcher()
    elif choice == '4':
        test_full_pipeline()
    elif choice == '5':
        test_database()
    elif choice == '6':
        print("\n🔄 Exécution de tous les tests...\n")
        results = {
            'Caméra': test_camera(),
            'Segmentation': test_segmentation(),
            'Matcher': test_matcher(),
            'Pipeline': test_full_pipeline(),
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

