#!/usr/bin/env python3
"""
Script pour capturer et analyser le trafic USB
Utile pour faire du reverse-engineering du protocole
"""

import sys
import usb.core
import usb.util
import time
from colorama import init, Fore, Style

init(autoreset=True)


def hex_dump(data, width=16):
    """Affiche les données en format hexadécimal lisible"""
    if not data:
        return ""
    
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i+width]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{i:04x}  {hex_part:<{width*3}}  {ascii_part}")
    
    return '\n'.join(lines)


def list_usb_devices():
    """Liste tous les périphériques USB"""
    devices = list(usb.core.find(find_all=True))
    
    print(f"\n{Fore.CYAN}Périphériques USB disponibles:")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    for i, dev in enumerate(devices):
        try:
            manufacturer = usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else "N/A"
            product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else "N/A"
        except:
            manufacturer = "N/A"
            product = "N/A"
        
        print(f"{i}. {manufacturer} - {product}")
        print(f"   VID:PID = {hex(dev.idVendor)}:{hex(dev.idProduct)}")
        print()
    
    return devices


def monitor_device(vendor_id, product_id, duration=10):
    """
    Monitore un périphérique USB spécifique
    
    Args:
        vendor_id: Vendor ID en entier (ex: 0x1234)
        product_id: Product ID en entier (ex: 0x5678)
        duration: Durée du monitoring en secondes
    """
    print(f"\n{Fore.YELLOW}🔍 Recherche du périphérique {hex(vendor_id)}:{hex(product_id)}...")
    
    # Trouver le périphérique
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    
    if device is None:
        print(f"{Fore.RED}❌ Périphérique non trouvé!")
        return
    
    print(f"{Fore.GREEN}✓ Périphérique trouvé!")
    
    # Détacher le driver kernel si nécessaire
    if device.is_kernel_driver_active(0):
        try:
            device.detach_kernel_driver(0)
            print(f"{Fore.YELLOW}⚠ Driver kernel détaché")
        except usb.core.USBError as e:
            print(f"{Fore.RED}❌ Impossible de détacher le driver: {e}")
            return
    
    # Configurer le périphérique
    try:
        device.set_configuration()
    except usb.core.USBError as e:
        print(f"{Fore.RED}❌ Impossible de configurer le périphérique: {e}")
        return
    
    # Obtenir la configuration active
    cfg = device.get_active_configuration()
    intf = cfg[(0, 0)]
    
    # Trouver les endpoints
    ep_in = usb.util.find_descriptor(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
    )
    
    ep_out = usb.util.find_descriptor(
        intf,
        custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
    )
    
    print(f"\n{Fore.CYAN}Configuration:")
    print(f"  Interface: {intf.bInterfaceNumber}")
    if ep_in:
        print(f"  Endpoint IN:  {hex(ep_in.bEndpointAddress)} (max: {ep_in.wMaxPacketSize} bytes)")
    if ep_out:
        print(f"  Endpoint OUT: {hex(ep_out.bEndpointAddress)} (max: {ep_out.wMaxPacketSize} bytes)")
    
    print(f"\n{Fore.YELLOW}📡 Monitoring pendant {duration} secondes...")
    print(f"{Fore.YELLOW}Appuyez sur Ctrl+C pour arrêter\n")
    
    start_time = time.time()
    packet_count = 0
    
    try:
        while time.time() - start_time < duration:
            try:
                if ep_in:
                    # Lire depuis l'endpoint IN
                    data = device.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=100)
                    
                    if data:
                        packet_count += 1
                        timestamp = time.time() - start_time
                        
                        print(f"{Fore.GREEN}[{timestamp:7.3f}s] ← IN  ({len(data)} bytes)")
                        print(hex_dump(bytes(data)))
                        print()
                
            except usb.core.USBError as e:
                if e.errno != 110:  # Timeout
                    print(f"{Fore.RED}Erreur: {e}")
            
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ Monitoring interrompu")
    
    print(f"\n{Fore.CYAN}Statistiques:")
    print(f"  Paquets capturés: {packet_count}")
    print(f"  Durée: {time.time() - start_time:.2f}s")


def send_command(vendor_id, product_id, command_hex):
    """
    Envoie une commande au périphérique
    
    Args:
        vendor_id: Vendor ID en entier
        product_id: Product ID en entier
        command_hex: Commande en hexadécimal (ex: "01 02 03 04")
    """
    device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
    
    if device is None:
        print(f"{Fore.RED}❌ Périphérique non trouvé!")
        return
    
    # Convertir la commande hex en bytes
    command_bytes = bytes.fromhex(command_hex.replace(' ', ''))
    
    print(f"{Fore.CYAN}Envoi de la commande:")
    print(hex_dump(command_bytes))
    
    # Détacher le driver kernel si nécessaire
    if device.is_kernel_driver_active(0):
        try:
            device.detach_kernel_driver(0)
        except:
            pass
    
    try:
        device.set_configuration()
        cfg = device.get_active_configuration()
        intf = cfg[(0, 0)]
        
        ep_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )
        
        if ep_out:
            device.write(ep_out.bEndpointAddress, command_bytes)
            print(f"{Fore.GREEN}✓ Commande envoyée!")
            
            # Attendre et lire la réponse
            ep_in = usb.util.find_descriptor(
                intf,
                custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
            )
            
            if ep_in:
                try:
                    data = device.read(ep_in.bEndpointAddress, ep_in.wMaxPacketSize, timeout=1000)
                    print(f"\n{Fore.GREEN}Réponse reçue ({len(data)} bytes):")
                    print(hex_dump(bytes(data)))
                except usb.core.USBError:
                    print(f"{Fore.YELLOW}⚠ Pas de réponse")
        else:
            print(f"{Fore.RED}❌ Endpoint OUT non trouvé")
            
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur: {e}")


def main():
    print(f"{Fore.MAGENTA}{'='*70}")
    print(f"{Fore.MAGENTA}📡 CAPTURE DE TRAFIC USB - Reverse Engineering")
    print(f"{Fore.MAGENTA}{'='*70}")
    
    if len(sys.argv) < 2:
        print(f"\n{Fore.YELLOW}Usage:")
        print(f"  {sys.argv[0]} list                           - Liste les périphériques")
        print(f"  {sys.argv[0]} monitor VID PID [duration]     - Monitore un périphérique")
        print(f"  {sys.argv[0]} send VID PID 'hex command'     - Envoie une commande")
        print(f"\n{Fore.YELLOW}Exemple:")
        print(f"  {sys.argv[0]} monitor 0x1234 0x5678 30")
        print(f"  {sys.argv[0]} send 0x1234 0x5678 '01 02 03 04'")
        print()
        
        # Par défaut, lister les périphériques
        list_usb_devices()
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_usb_devices()
    
    elif command == "monitor":
        if len(sys.argv) < 4:
            print(f"{Fore.RED}❌ Usage: {sys.argv[0]} monitor VID PID [duration]")
            return
        
        vid = int(sys.argv[2], 16)
        pid = int(sys.argv[3], 16)
        duration = int(sys.argv[4]) if len(sys.argv) > 4 else 10
        
        monitor_device(vid, pid, duration)
    
    elif command == "send":
        if len(sys.argv) < 5:
            print(f"{Fore.RED}❌ Usage: {sys.argv[0]} send VID PID 'hex command'")
            return
        
        vid = int(sys.argv[2], 16)
        pid = int(sys.argv[3], 16)
        cmd = sys.argv[4]
        
        send_command(vid, pid, cmd)
    
    else:
        print(f"{Fore.RED}❌ Commande inconnue: {command}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠ Programme interrompu")
        sys.exit(0)

