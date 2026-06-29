#!/usr/bin/env python3
"""
Test de capture d'empreinte avec le lecteur Aratek
"""

import usb.core
import usb.util
import time
from colorama import Fore, Style, init

init(autoreset=True)

class AratekReader:
    def __init__(self):
        self.device = None
        self.ep_in = None
        self.ep_out = None
        
    def connect(self):
        """Connecte au lecteur Aratek"""
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}👆 TEST LECTEUR D'EMPREINTES ARATEK")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        print(f"{Fore.YELLOW}1. Connexion au lecteur...")
        
        # Trouver le périphérique
        self.device = usb.core.find(idVendor=0x28ed, idProduct=0x1063)
        
        if self.device is None:
            print(f"{Fore.RED}❌ Lecteur non trouvé!")
            return False
        
        print(f"{Fore.GREEN}✅ Lecteur trouvé")
        
        # Détacher driver kernel
        try:
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
        except:
            pass
        
        # Configurer
        try:
            self.device.set_configuration()
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur configuration: {e}")
            return False
        
        # Trouver les endpoints
        cfg = self.device.get_active_configuration()
        intf = cfg[(0,0)]
        
        for ep in intf:
            if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                self.ep_in = ep
            else:
                self.ep_out = ep
        
        print(f"{Fore.GREEN}✅ Connexion établie")
        print(f"{Fore.WHITE}   Endpoint IN:  {hex(self.ep_in.bEndpointAddress)}")
        print(f"{Fore.WHITE}   Endpoint OUT: {hex(self.ep_out.bEndpointAddress)}")
        
        return True
    
    def send_command(self, data):
        """Envoie une commande au lecteur"""
        try:
            written = self.device.write(self.ep_out.bEndpointAddress, data, timeout=1000)
            return written
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur envoi: {e}")
            return 0
    
    def read_response(self, size=512, timeout=2000):
        """Lit la réponse du lecteur"""
        try:
            data = self.device.read(self.ep_in.bEndpointAddress, size, timeout=timeout)
            return bytes(data)
        except usb.core.USBTimeoutError:
            return None
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️  Lecture: {e}")
            return None
    
    def test_communication(self):
        """Test de communication basique"""
        print(f"\n{Fore.YELLOW}2. Test de communication...")
        
        # Commandes génériques à essayer
        test_commands = [
            b'\x01\x00\x00\x00',  # Init possible
            b'\x55\xAA\x00\x00',  # Pattern commun
            b'\x00\x00\x00\x00',  # Null
            b'\x01',              # Simple 1
            b'\x02',              # Simple 2
            b'\xFF\xFF\xFF\xFF',  # All FF
        ]
        
        print(f"{Fore.WHITE}   Essai de différentes commandes...\n")
        
        for i, cmd in enumerate(test_commands, 1):
            print(f"   Test {i}: {cmd.hex()} ... ", end='')
            
            written = self.send_command(cmd)
            if written > 0:
                # Attendre une réponse
                response = self.read_response(timeout=500)
                
                if response:
                    print(f"{Fore.GREEN}✓ Réponse reçue: {response[:20].hex()}...")
                else:
                    print(f"{Fore.YELLOW}○ Pas de réponse")
            else:
                print(f"{Fore.RED}✗ Échec envoi")
            
            time.sleep(0.1)
    
    def monitor_continuous(self, duration=10):
        """Monitore en continu pour détecter des événements"""
        print(f"\n{Fore.YELLOW}3. Monitoring continu ({duration}s)...")
        print(f"{Fore.WHITE}   Placez votre doigt sur le lecteur pendant ce temps\n")
        
        start_time = time.time()
        packet_count = 0
        
        while time.time() - start_time < duration:
            # Essayer de lire des données
            data = self.read_response(timeout=100)
            
            if data and len(data) > 0:
                packet_count += 1
                elapsed = time.time() - start_time
                print(f"{Fore.GREEN}   [{elapsed:6.2f}s] Données reçues ({len(data)} bytes): {data[:30].hex()}...")
            
            time.sleep(0.01)
        
        print(f"\n{Fore.CYAN}   Total paquets reçus: {packet_count}")
        
        if packet_count == 0:
            print(f"{Fore.YELLOW}   ⚠️  Aucune donnée spontanée détectée")
    
    def try_capture(self):
        """Essaie différentes méthodes de capture"""
        print(f"\n{Fore.YELLOW}4. Tentative de capture d'empreinte...")
        print(f"{Fore.WHITE}   Placez votre doigt sur le lecteur\n")
        
        # Méthode 1: Envoyer une commande de capture
        capture_commands = [
            b'\x01\x00\x00\x00',
            b'\x03\x00\x00\x00',
            b'\x20\x00\x00\x00',
            b'\x55\xAA\x01\x00',
        ]
        
        for i, cmd in enumerate(capture_commands, 1):
            print(f"   Méthode {i}: Envoi {cmd.hex()}...", end=' ')
            
            self.send_command(cmd)
            
            # Lire plusieurs fois
            for attempt in range(5):
                response = self.read_response(timeout=1000)
                
                if response and len(response) > 10:
                    print(f"\n{Fore.GREEN}   ✓ Réponse obtenue! ({len(response)} bytes)")
                    print(f"{Fore.WHITE}   Début: {response[:50].hex()}...")
                    
                    # Sauvegarder
                    filename = f"aratek_response_{int(time.time())}.bin"
                    with open(filename, 'wb') as f:
                        f.write(response)
                    print(f"{Fore.GREEN}   ✓ Sauvegardé: {filename}")
                    return True
            
            print(f"{Fore.YELLOW}○ Pas de réponse significative")
            time.sleep(0.5)
        
        return False
    
    def disconnect(self):
        """Déconnecte"""
        if self.device:
            usb.util.dispose_resources(self.device)
        print(f"\n{Fore.GREEN}✓ Déconnecté")


def main():
    reader = AratekReader()
    
    if not reader.connect():
        return
    
    # Test de communication
    reader.test_communication()
    
    # Monitoring
    reader.monitor_continuous(duration=10)
    
    # Tentative de capture
    success = reader.try_capture()
    
    reader.disconnect()
    
    # Résumé
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}📊 RÉSUMÉ")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    if success:
        print(f"{Fore.GREEN}✅ Capture réussie!")
        print(f"{Fore.WHITE}   Le lecteur répond aux commandes")
    else:
        print(f"{Fore.YELLOW}⚠️  Pas de capture détectée")
        print(f"{Fore.WHITE}   Le lecteur nécessite un protocole spécifique")
        print(f"\n{Fore.CYAN}Solutions:")
        print(f"{Fore.WHITE}   1. Contactez Aratek pour la documentation du protocole")
        print(f"{Fore.WHITE}   2. Utilisez leur SDK officiel")
        print(f"{Fore.WHITE}   3. Reverse engineering (capture USB avec Wireshark)")
    
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️  Interrompu par l'utilisateur")

