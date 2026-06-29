#!/usr/bin/env python3
"""
Test visuel en temps réel des composants biométriques
Vous verrez immédiatement si ça marche !
"""

import cv2
import usb.core
import usb.util
import sys
from colorama import Fore, Style, init

init(autoreset=True)

print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}🔍 TEST EN TEMPS RÉEL DES COMPOSANTS BIOMÉTRIQUES")
print(f"{Fore.CYAN}{'='*70}\n")

# TEST 1: Lecteur d'empreintes
print(f"{Fore.YELLOW}📍 TEST 1/2: Lecteur d'empreintes Aratek...")
print("-" * 70)

try:
    fp_device = usb.core.find(idVendor=0x28ed, idProduct=0x1063)
    
    if fp_device is None:
        print(f"{Fore.RED}❌ Lecteur d'empreintes NON DÉTECTÉ")
        print(f"{Fore.YELLOW}   → Vérifiez qu'il est bien branché\n")
    else:
        print(f"{Fore.GREEN}✅ Lecteur d'empreintes DÉTECTÉ")
        print(f"{Fore.WHITE}   Fabricant: Aratek Biometric")
        print(f"{Fore.WHITE}   VID:PID: 0x28ed:0x1063")
        print(f"{Fore.WHITE}   Bus: {fp_device.bus}, Address: {fp_device.address}")
        
        # Test de connexion
        try:
            # Détacher driver si nécessaire
            if fp_device.is_kernel_driver_active(0):
                fp_device.detach_kernel_driver(0)
            
            # Configurer
            fp_device.set_configuration()
            cfg = fp_device.get_active_configuration()
            intf = cfg[(0,0)]
            
            # Trouver endpoints
            ep_in = None
            ep_out = None
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    ep_in = ep
                else:
                    ep_out = ep
            
            print(f"{Fore.GREEN}✅ CONNEXION RÉUSSIE!")
            print(f"{Fore.WHITE}   Endpoint IN:  {hex(ep_in.bEndpointAddress)}")
            print(f"{Fore.WHITE}   Endpoint OUT: {hex(ep_out.bEndpointAddress)}")
            print(f"{Fore.GREEN}   🎉 Prêt à capturer des empreintes!\n")
            
            usb.util.dispose_resources(fp_device)
            
        except usb.core.USBError as e:
            if "Access denied" in str(e) or "13" in str(e):
                print(f"{Fore.RED}❌ ERREUR DE PERMISSIONS")
                print(f"{Fore.YELLOW}   → Exécutez: sudo ./fix_permissions.sh")
                print(f"{Fore.YELLOW}   → Puis débranchez/rebranchez le lecteur\n")
            else:
                print(f"{Fore.RED}❌ Erreur: {e}\n")
        
except Exception as e:
    print(f"{Fore.RED}❌ Erreur: {e}\n")

# TEST 2: Lecteur d'iris (caméra)
print(f"{Fore.YELLOW}📍 TEST 2/2: Lecteur d'iris Sunplus...")
print("-" * 70)

try:
    # Tester la caméra #2 (lecteur d'iris)
    cap = cv2.VideoCapture(2)
    
    if not cap.isOpened():
        print(f"{Fore.RED}❌ Lecteur d'iris NON ACCESSIBLE")
        print(f"{Fore.YELLOW}   → Vérifiez qu'il est bien branché")
        print(f"{Fore.YELLOW}   → Vérifiez les permissions: sudo ./fix_permissions.sh\n")
    else:
        # Essayer de lire une image
        ret, frame = cap.read()
        
        if ret and frame is not None:
            h, w = frame.shape[:2]
            print(f"{Fore.GREEN}✅ Lecteur d'iris DÉTECTÉ ET FONCTIONNEL")
            print(f"{Fore.WHITE}   Device: Sunplus HK 1M CAM")
            print(f"{Fore.WHITE}   VID:PID: 0x1bcf:0x0b15")
            print(f"{Fore.WHITE}   Caméra: /dev/video2")
            print(f"{Fore.WHITE}   Résolution: {w}x{h}")
            print(f"{Fore.GREEN}   🎉 Prêt à capturer des iris!")
            
            # Afficher un aperçu
            print(f"\n{Fore.CYAN}📷 APERÇU EN TEMPS RÉEL...")
            print(f"{Fore.WHITE}   Positionnez votre œil devant le lecteur")
            print(f"{Fore.WHITE}   Appuyez sur 'q' ou ESC pour fermer\n")
            
            cv2.namedWindow('Lecteur Iris - Test', cv2.WINDOW_NORMAL)
            
            frame_count = 0
            while True:
                ret, frame = cap.read()
                
                if ret:
                    # Ajouter du texte sur l'image
                    cv2.putText(frame, "Lecteur d'iris Sunplus", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    cv2.putText(frame, "Appuyez sur Q pour quitter", (10, 60),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                    
                    cv2.imshow('Lecteur Iris - Test', frame)
                    
                    frame_count += 1
                    if frame_count == 1:
                        print(f"{Fore.GREEN}   ✓ Flux vidéo actif!")
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # q ou ESC
                    break
            
            cv2.destroyAllWindows()
            print(f"\n{Fore.GREEN}   ✓ Test terminé")
        else:
            print(f"{Fore.RED}❌ Impossible de lire l'image")
            print(f"{Fore.YELLOW}   → Le périphérique est détecté mais ne répond pas\n")
        
        cap.release()
        
except Exception as e:
    print(f"{Fore.RED}❌ Erreur: {e}\n")

# RÉSUMÉ
print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}📊 RÉSUMÉ")
print(f"{Fore.CYAN}{'='*70}\n")

print(f"{Fore.WHITE}Si tout est {Fore.GREEN}✅ vert{Fore.WHITE}, vos composants sont prêts!")
print(f"{Fore.WHITE}Si vous voyez du {Fore.RED}❌ rouge{Fore.WHITE}, suivez les instructions affichées.\n")

print(f"{Fore.YELLOW}Prochaines étapes:")
print(f"{Fore.WHITE}  1. Test capture empreinte: python3 test_fingerprint.py")
print(f"{Fore.WHITE}  2. Test capture iris: python3 test_iris.py")
print(f"{Fore.WHITE}  3. Interface graphique: python3 gui_app.py\n")

