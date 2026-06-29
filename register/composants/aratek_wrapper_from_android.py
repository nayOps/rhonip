#!/usr/bin/env python3
"""
Wrapper Python pour lecteur Aratek A400
Basé sur le SDK Android trouvé sur GitHub
Ref: https://github.com/Andoresu250/aratek-sdk-example

Les bibliothèques natives (.so) ne sont disponibles que pour Android ARM.
Pour utiliser sur Linux, il faut obtenir le SDK Linux officiel d'Aratek.

Ce fichier documente le protocole attendu basé sur l'analyse du SDK Android.
"""

import usb.core
import usb.util
import struct
import time
from typing import Optional, Tuple
import numpy as np


class AratekA400:
    """
    Classe pour communiquer avec le lecteur Aratek A400
    
    Basé sur l'analyse du SDK Android, le lecteur utilise:
    - Classe USB: Vendor Specific (255)
    - Endpoint IN: 0x81
    - Endpoint OUT: 0x02
    - Taille de paquet: 512 bytes
    
    Séquence d'initialisation découverte:
    1. powerOn()
    2. open()
    3. prepare()
    4. capture()
    5. finish()
    6. close()
    7. powerOff()
    """
    
    # Constantes d'erreur (du SDK Android)
    RESULT_OK = 0
    RESULT_FAIL = -1
    WRONG_CONNECTION = -2
    DEVICE_BUSY = -3
    DEVICE_NOT_OPEN = -4
    TIMEOUT = -5
    NO_PERMISSION = -6
    WRONG_PARAMETER = -7
    DECODE_ERROR = -8
    INIT_FAIL = -9
    UNKNOWN_ERROR = -10
    NOT_SUPPORT = -11
    NOT_ENOUGH_MEMORY = -12
    DEVICE_NOT_FOUND = -13
    DEVICE_REOPEN = -14
    NO_FINGER = -15
    
    def __init__(self):
        self.device = None
        self.ep_in = None
        self.ep_out = None
        self.is_open = False
        
    def find_device(self) -> bool:
        """Trouve le lecteur Aratek A400"""
        print("🔍 Recherche du lecteur Aratek A400...")
        
        self.device = usb.core.find(idVendor=0x28ed, idProduct=0x1063)
        
        if self.device is None:
            print("❌ Lecteur non trouvé")
            return False
        
        print(f"✅ Lecteur trouvé (Bus {self.device.bus}, Address {self.device.address})")
        return True
    
    def power_on(self) -> int:
        """
        Allume le lecteur
        
        Returns:
            int: RESULT_OK si succès
        """
        print("\n⚡ PowerOn...")
        
        if not self.device:
            return self.DEVICE_NOT_FOUND
        
        try:
            # Détacher le driver kernel si actif
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
            
            # Configuration USB
            self.device.set_configuration()
            
            # Récupérer les endpoints
            cfg = self.device.get_active_configuration()
            intf = cfg[(0, 0)]
            
            for ep in intf:
                if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
                    self.ep_in = ep
                else:
                    self.ep_out = ep
            
            print(f"✅ PowerOn OK (EP IN: {hex(self.ep_in.bEndpointAddress)}, EP OUT: {hex(self.ep_out.bEndpointAddress)})")
            return self.RESULT_OK
            
        except Exception as e:
            print(f"❌ PowerOn erreur: {e}")
            return self.RESULT_FAIL
    
    def open(self) -> int:
        """
        Ouvre le lecteur
        
        Returns:
            int: RESULT_OK si succès
        """
        print("📂 Open device...")
        
        if not self.device:
            return self.DEVICE_NOT_FOUND
        
        # TODO: Envoyer la commande d'ouverture
        # La commande exacte n'est pas connue sans le SDK natif
        # Il faudrait faire du reverse-engineering ou obtenir le SDK Linux
        
        # Tentative de commandes possibles
        possible_commands = [
            b'\x01\x00',  # Open cmd 1
            b'\x01\x00\x00\x00',  # Open cmd 2
            b'\x55\xAA\x01\x00',  # Open avec header
        ]
        
        for cmd in possible_commands:
            try:
                self.device.write(self.ep_out.bEndpointAddress, cmd, timeout=1000)
                response = self.device.read(self.ep_in.bEndpointAddress, 512, timeout=500)
                
                if response:
                    print(f"   Réponse: {bytes(response).hex()}")
                    self.is_open = True
                    print("✅ Open OK")
                    return self.RESULT_OK
            except:
                pass
        
        print("⚠️  Open: pas de réponse (SDK natif requis)")
        return self.NOT_SUPPORT
    
    def get_sn(self) -> Tuple[int, Optional[str]]:
        """Récupère le numéro de série"""
        print("🔢 Get SN...")
        
        # Le SN est disponible via USB descriptor
        try:
            sn = usb.util.get_string(self.device, self.device.iSerialNumber)
            print(f"✅ SN: {sn}")
            return (self.RESULT_OK, sn)
        except:
            return (self.RESULT_FAIL, None)
    
    def get_firmware_version(self) -> Tuple[int, Optional[str]]:
        """Récupère la version du firmware"""
        print("📌 Get Firmware Version...")
        
        # TODO: Commande pour récupérer la version firmware
        # Nécessite le protocole propriétaire
        
        print("⚠️  Commande non implémentée (SDK requis)")
        return (self.NOT_SUPPORT, "Unknown")
    
    def prepare(self) -> int:
        """Prépare le capteur pour la capture"""
        print("🔧 Prepare...")
        
        # TODO: Commande de préparation
        return self.NOT_SUPPORT
    
    def capture(self, timeout: int = 10) -> Tuple[int, Optional[bytes]]:
        """
        Capture une empreinte
        
        Args:
            timeout: Timeout en secondes
            
        Returns:
            tuple: (error_code, image_data)
        """
        print(f"👆 Capture (timeout={timeout}s)...")
        print("   Placez votre doigt sur le lecteur...")
        
        # TODO: Commande de capture
        # Sans le SDK, on ne peut pas envoyer les bonnes commandes
        
        return (self.NOT_SUPPORT, None)
    
    def finish(self) -> int:
        """Termine la capture"""
        print("✅ Finish capture")
        return self.RESULT_OK
    
    def close(self) -> int:
        """Ferme le lecteur"""
        print("📕 Close device...")
        self.is_open = False
        return self.RESULT_OK
    
    def power_off(self) -> int:
        """Éteint le lecteur"""
        print("⚡ PowerOff...")
        
        if self.device:
            usb.util.dispose_resources(self.device)
        
        return self.RESULT_OK


def main():
    """Test du wrapper Aratek"""
    print("="*70)
    print("🔐 WRAPPER ARATEK A400 - Basé sur SDK Android")
    print("="*70)
    print()
    print("Source: https://github.com/Andoresu250/aratek-sdk-example")
    print()
    
    reader = AratekA400()
    
    # Trouver le lecteur
    if not reader.find_device():
        return
    
    # Séquence d'initialisation
    if reader.power_on() != AratekA400.RESULT_OK:
        print("\n❌ PowerOn échoué")
        return
    
    if reader.open() != AratekA400.RESULT_OK:
        print("\n⚠️  Open échoué - SDK natif requis")
    
    # Récupérer infos
    error, sn = reader.get_sn()
    error, fw = reader.get_firmware_version()
    
    # Test de capture (ne fonctionnera pas sans SDK)
    reader.prepare()
    error, data = reader.capture(timeout=5)
    reader.finish()
    
    # Fermeture
    reader.close()
    reader.power_off()
    
    print("\n" + "="*70)
    print("📊 CONCLUSION")
    print("="*70)
    print()
    print("✅ Connexion USB:        OK")
    print("✅ Endpoints trouvés:    OK")
    print("❌ Protocole propriétaire: REQUIS SDK")
    print()
    print("Pour faire fonctionner complètement ce lecteur:")
    print("  1. Contactez Aratek: https://www.aratek.co/")
    print("  2. Demandez le SDK Linux pour A400")
    print("  3. Ou utilisez leur application Android avec ce repo")
    print()
    print("Alternative immédiate:")
    print("  - Utilisez le lecteur d'IRIS qui fonctionne déjà ✅")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrompu")

