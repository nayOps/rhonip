#!/usr/bin/env python3
"""
Test rapide de connexion au lecteur d'empreintes Aratek
"""

import sys
import usb.core
import usb.util

# IDs du lecteur Aratek
VENDOR_ID = 0x28ed
PRODUCT_ID = 0x1063

print("="*60)
print("🔍 TEST CONNEXION LECTEUR D'EMPREINTES ARATEK")
print("="*60)

# Trouver le périphérique
print(f"\n1. Recherche du périphérique {hex(VENDOR_ID)}:{hex(PRODUCT_ID)}...")
device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if device is None:
    print("❌ Périphérique non trouvé!")
    sys.exit(1)

print("✅ Périphérique trouvé!")

# Afficher les infos
print(f"\n2. Informations:")
print(f"   Fabricant: Aratek Biometric")
print(f"   Produit: Aratek FingerPrint")
print(f"   Bus: {device.bus}, Address: {device.address}")

# Détacher le driver kernel si nécessaire
print(f"\n3. Vérification du driver...")
try:
    if device.is_kernel_driver_active(0):
        print("   ⚠️  Driver kernel actif, détachement...")
        device.detach_kernel_driver(0)
        print("   ✅ Driver détaché")
    else:
        print("   ✅ Pas de driver kernel à détacher")
except Exception as e:
    print(f"   ⚠️  Erreur: {e}")

# Configurer le périphérique
print(f"\n4. Configuration...")
try:
    device.set_configuration()
    print("   ✅ Configuration réussie")
except usb.core.USBError as e:
    print(f"   ❌ Erreur configuration: {e}")
    sys.exit(1)

# Obtenir la configuration
print(f"\n5. Analyse des endpoints...")
cfg = device.get_active_configuration()
intf = cfg[(0,0)]

print(f"   Interface: {intf.bInterfaceNumber}")
print(f"   Classe: {intf.bInterfaceClass} (255 = Vendor Specific)")

# Trouver les endpoints
ep_in = None
ep_out = None

for ep in intf:
    if usb.util.endpoint_direction(ep.bEndpointAddress) == usb.util.ENDPOINT_IN:
        ep_in = ep
        print(f"   ✅ Endpoint IN:  {hex(ep.bEndpointAddress)} (max: {ep.wMaxPacketSize} bytes)")
    else:
        ep_out = ep
        print(f"   ✅ Endpoint OUT: {hex(ep.bEndpointAddress)} (max: {ep.wMaxPacketSize} bytes)")

if ep_in and ep_out:
    print(f"\n✅ SUCCÈS! Lecteur d'empreintes prêt à l'emploi!")
    print(f"\nEndpoints à utiliser:")
    print(f"   IN:  {hex(ep_in.bEndpointAddress)}")
    print(f"   OUT: {hex(ep_out.bEndpointAddress)}")
else:
    print(f"\n⚠️  Endpoints incomplets")

# Nettoyage
usb.util.dispose_resources(device)

print("\n" + "="*60)

