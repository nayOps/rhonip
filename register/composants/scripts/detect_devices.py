#!/usr/bin/env python3
"""
Script de détection des périphériques biométriques
Détecte les lecteurs USB et série connectés
"""

import sys
import json
from colorama import init, Fore, Style

init(autoreset=True)

def detect_usb_devices():
    """Détecte tous les périphériques USB connectés"""
    try:
        import usb.core
        import usb.util
        
        devices = usb.core.find(find_all=True)
        usb_devices = []
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}🔌 PÉRIPHÉRIQUES USB DÉTECTÉS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        for i, device in enumerate(devices):
            try:
                manufacturer = usb.util.get_string(device, device.iManufacturer) if device.iManufacturer else "N/A"
                product = usb.util.get_string(device, device.iProduct) if device.iProduct else "N/A"
                serial = usb.util.get_string(device, device.iSerialNumber) if device.iSerialNumber else "N/A"
            except:
                manufacturer = "N/A"
                product = "N/A"
                serial = "N/A"
            
            device_info = {
                "vendor_id": hex(device.idVendor),
                "product_id": hex(device.idProduct),
                "manufacturer": manufacturer,
                "product": product,
                "serial": serial,
                "bus": device.bus,
                "address": device.address
            }
            usb_devices.append(device_info)
            
            # Détecter les mots-clés biométriques
            keywords = ['fingerprint', 'finger', 'biometric', 'iris', 'scanner', 'reader']
            is_biometric = any(keyword in str(product).lower() or keyword in str(manufacturer).lower() 
                             for keyword in keywords)
            
            color = Fore.GREEN if is_biometric else Fore.WHITE
            icon = "✓ " if is_biometric else "  "
            
            print(f"{color}{icon}Device #{i+1}:")
            print(f"{color}  └─ VID:PID     : {device_info['vendor_id']}:{device_info['product_id']}")
            print(f"{color}  └─ Fabricant  : {manufacturer}")
            print(f"{color}  └─ Produit    : {product}")
            print(f"{color}  └─ Série      : {serial}")
            print(f"{color}  └─ Bus:Address: {device.bus}:{device.address}")
            
            # Afficher les interfaces
            try:
                cfg = device.get_active_configuration()
                for intf in cfg:
                    print(f"{color}  └─ Interface  : {intf.bInterfaceNumber} (Class: {intf.bInterfaceClass})")
                    for ep in intf:
                        ep_type = "IN " if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN else "OUT"
                        print(f"{color}      └─ Endpoint: {hex(ep.bEndpointAddress)} ({ep_type})")
            except:
                pass
            
            print()
        
        return usb_devices
        
    except ImportError:
        print(f"{Fore.RED}❌ Module 'pyusb' non installé. Installez avec: pip install pyusb")
        return []
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la détection USB: {e}")
        return []


def detect_serial_devices():
    """Détecte tous les ports série disponibles"""
    try:
        import serial.tools.list_ports
        
        ports = serial.tools.list_ports.comports()
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📡 PORTS SÉRIE DÉTECTÉS")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        serial_devices = []
        
        if not ports:
            print(f"{Fore.YELLOW}⚠ Aucun port série détecté")
            return []
        
        for i, port in enumerate(ports):
            device_info = {
                "port": port.device,
                "description": port.description,
                "hwid": port.hwid,
                "vid": hex(port.vid) if port.vid else None,
                "pid": hex(port.pid) if port.pid else None,
                "manufacturer": port.manufacturer
            }
            serial_devices.append(device_info)
            
            keywords = ['fingerprint', 'finger', 'biometric', 'iris', 'scanner', 'reader', 'ft232', 'ch340', 'cp210']
            is_biometric = any(keyword in str(port.description).lower() or 
                             keyword in str(port.manufacturer).lower() if port.manufacturer else False
                             for keyword in keywords)
            
            color = Fore.GREEN if is_biometric else Fore.WHITE
            icon = "✓ " if is_biometric else "  "
            
            print(f"{color}{icon}Port #{i+1}:")
            print(f"{color}  └─ Device     : {port.device}")
            print(f"{color}  └─ Description: {port.description}")
            print(f"{color}  └─ HWID       : {port.hwid}")
            if port.vid and port.pid:
                print(f"{color}  └─ VID:PID    : {hex(port.vid)}:{hex(port.pid)}")
            if port.manufacturer:
                print(f"{color}  └─ Fabricant  : {port.manufacturer}")
            print()
        
        return serial_devices
        
    except ImportError:
        print(f"{Fore.RED}❌ Module 'pyserial' non installé. Installez avec: pip install pyserial")
        return []
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la détection série: {e}")
        return []


def detect_cameras():
    """Détecte les caméras disponibles (pour lecteur iris)"""
    try:
        import cv2
        
        print(f"\n{Fore.CYAN}{'='*70}")
        print(f"{Fore.CYAN}📷 CAMÉRAS DÉTECTÉES")
        print(f"{Fore.CYAN}{'='*70}\n")
        
        cameras = []
        
        # Tester les indices de caméra de 0 à 10
        for i in range(10):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    height, width = frame.shape[:2]
                    camera_info = {
                        "index": i,
                        "width": width,
                        "height": height
                    }
                    cameras.append(camera_info)
                    
                    print(f"{Fore.GREEN}✓ Caméra #{i}:")
                    print(f"{Fore.GREEN}  └─ Résolution: {width}x{height}")
                    print()
                cap.release()
        
        if not cameras:
            print(f"{Fore.YELLOW}⚠ Aucune caméra détectée")
        
        return cameras
        
    except ImportError:
        print(f"{Fore.RED}❌ Module 'opencv-python' non installé. Installez avec: pip install opencv-python")
        return []
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur lors de la détection caméra: {e}")
        return []


def save_config(usb_devices, serial_devices, cameras):
    """Propose de sauvegarder la configuration détectée"""
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}💾 CONFIGURATION")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    if usb_devices or serial_devices or cameras:
        print(f"{Fore.YELLOW}💡 Conseil: Mettez à jour config.json avec les IDs de vos périphériques")
        
        if usb_devices:
            print(f"\n{Fore.WHITE}Exemple pour USB:")
            device = usb_devices[0]
            print(f'  "vendor_id": "{device["vendor_id"]}",')
            print(f'  "product_id": "{device["product_id"]}"')
        
        if serial_devices:
            print(f"\n{Fore.WHITE}Exemple pour Série:")
            device = serial_devices[0]
            print(f'  "port": "{device["port"]}"')
        
        if cameras:
            print(f"\n{Fore.WHITE}Exemple pour Caméra:")
            camera = cameras[0]
            print(f'  "camera_index": {camera["index"]}')


def main():
    print(f"\n{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}🔍 DÉTECTION DES PÉRIPHÉRIQUES BIOMÉTRIQUES")
    print(f"{Fore.MAGENTA}{'='*70}")
    
    usb_devices = detect_usb_devices()
    serial_devices = detect_serial_devices()
    cameras = detect_cameras()
    
    save_config(usb_devices, serial_devices, cameras)
    
    print(f"\n{Fore.GREEN}✅ Détection terminée!")
    print(f"{Fore.WHITE}Périphériques trouvés: {len(usb_devices)} USB, {len(serial_devices)} Série, {len(cameras)} Caméra(s)")


if __name__ == "__main__":
    main()

