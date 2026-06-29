"""
Lecteur d'empreintes via USB (communication directe)
Pour périphériques sans driver ou SDK
"""

import usb.core
import usb.util
import numpy as np
from PIL import Image
import time
import json


class USBFingerprintReader:
    """
    Classe pour communiquer avec un lecteur d'empreintes via USB
    """
    
    def __init__(self, vendor_id=None, product_id=None, config_file='config.json'):
        """
        Initialise le lecteur USB
        
        Args:
            vendor_id: ID du fabricant (ex: 0x1234)
            product_id: ID du produit (ex: 0x5678)
            config_file: Fichier de configuration
        """
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.endpoint_in = None
        self.endpoint_out = None
        self.config = {}
        
        # Charger la configuration si pas d'IDs fournis
        if vendor_id is None or product_id is None:
            self.load_config(config_file)
        
        self.connected = False
    
    def load_config(self, config_file):
        """Charge la configuration depuis le fichier JSON"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                fp_config = config.get('fingerprint', {}).get('usb', {})
                
                if fp_config.get('vendor_id'):
                    self.vendor_id = int(fp_config['vendor_id'], 16)
                if fp_config.get('product_id'):
                    self.product_id = int(fp_config['product_id'], 16)
                
                self.config = fp_config
        except Exception as e:
            print(f"Erreur chargement config: {e}")
    
    def connect(self):
        """
        Connecte au lecteur d'empreintes
        
        Returns:
            bool: True si connexion réussie
        """
        if self.vendor_id is None or self.product_id is None:
            print("❌ VID/PID non configurés. Utilisez detect_devices.py pour les trouver")
            return False
        
        print(f"🔍 Recherche du périphérique {hex(self.vendor_id)}:{hex(self.product_id)}...")
        
        # Trouver le périphérique
        self.device = usb.core.find(idVendor=self.vendor_id, idProduct=self.product_id)
        
        if self.device is None:
            print("❌ Périphérique non trouvé!")
            return False
        
        print("✓ Périphérique trouvé!")
        
        # Détacher le driver kernel si nécessaire
        try:
            if self.device.is_kernel_driver_active(0):
                self.device.detach_kernel_driver(0)
                print("⚠ Driver kernel détaché")
        except usb.core.USBError as e:
            print(f"⚠ Impossible de détacher le driver: {e}")
        
        # Configurer le périphérique
        try:
            self.device.set_configuration()
        except usb.core.USBError as e:
            print(f"❌ Impossible de configurer: {e}")
            return False
        
        # Trouver les endpoints
        cfg = self.device.get_active_configuration()
        intf = cfg[(0, 0)]
        
        self.endpoint_in = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
        )
        
        self.endpoint_out = usb.util.find_descriptor(
            intf,
            custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
        )
        
        if self.endpoint_in is None and self.endpoint_out is None:
            print("❌ Aucun endpoint trouvé!")
            return False
        
        print(f"✓ Endpoints configurés (IN: {hex(self.endpoint_in.bEndpointAddress) if self.endpoint_in else 'N/A'}, "
              f"OUT: {hex(self.endpoint_out.bEndpointAddress) if self.endpoint_out else 'N/A'})")
        
        self.connected = True
        return True
    
    def disconnect(self):
        """Déconnecte du périphérique"""
        if self.device:
            usb.util.dispose_resources(self.device)
        self.connected = False
        print("✓ Déconnecté")
    
    def send_command(self, command):
        """
        Envoie une commande au lecteur
        
        Args:
            command: bytes à envoyer
            
        Returns:
            bool: True si envoi réussi
        """
        if not self.connected or self.endpoint_out is None:
            print("❌ Non connecté ou pas d'endpoint OUT")
            return False
        
        try:
            self.device.write(self.endpoint_out.bEndpointAddress, command)
            return True
        except usb.core.USBError as e:
            print(f"❌ Erreur envoi: {e}")
            return False
    
    def read_response(self, timeout=1000, size=None):
        """
        Lit la réponse du lecteur
        
        Args:
            timeout: Timeout en ms
            size: Taille à lire (None = taille max du paquet)
            
        Returns:
            bytes: Données lues ou None
        """
        if not self.connected or self.endpoint_in is None:
            print("❌ Non connecté ou pas d'endpoint IN")
            return None
        
        try:
            if size is None:
                size = self.endpoint_in.wMaxPacketSize
            
            data = self.device.read(self.endpoint_in.bEndpointAddress, size, timeout=timeout)
            return bytes(data)
        except usb.core.USBError as e:
            if e.errno == 110:  # Timeout
                return None
            print(f"❌ Erreur lecture: {e}")
            return None
    
    def initialize_sensor(self):
        """
        Initialise le capteur (commandes génériques)
        À adapter selon votre lecteur spécifique
        
        Returns:
            bool: True si initialisé
        """
        print("🔧 Initialisation du capteur...")
        
        # Commandes d'initialisation communes (exemples)
        # Ces commandes varient selon le fabricant
        init_commands = [
            b'\x01\x00\x00\x00',  # Exemple: Reset
            b'\x02\x00\x00\x00',  # Exemple: Get status
        ]
        
        for cmd in init_commands:
            if self.send_command(cmd):
                response = self.read_response(timeout=500)
                if response:
                    print(f"  Réponse: {response.hex()}")
        
        print("✓ Capteur initialisé (commandes génériques envoyées)")
        return True
    
    def capture_fingerprint(self, timeout=10):
        """
        Capture une empreinte digitale
        
        Args:
            timeout: Temps d'attente maximum en secondes
            
        Returns:
            numpy.ndarray: Image de l'empreinte ou None
        """
        print("👆 Placez votre doigt sur le capteur...")
        
        # Commande de capture (à adapter)
        capture_cmd = b'\x03\x00\x00\x00'  # Exemple
        
        if not self.send_command(capture_cmd):
            return None
        
        # Lire l'image
        start_time = time.time()
        image_data = bytearray()
        
        while time.time() - start_time < timeout:
            data = self.read_response(timeout=1000)
            if data:
                image_data.extend(data)
                
                # Vérifier si l'image est complète (à adapter)
                # La plupart des lecteurs envoient un marqueur de fin
                if len(image_data) >= 73728:  # Exemple: 256x288 pixels
                    break
        
        if len(image_data) == 0:
            print("❌ Aucune donnée reçue")
            return None
        
        print(f"✓ Données reçues: {len(image_data)} bytes")
        
        # Convertir en image (dimensions à adapter)
        try:
            # Exemple pour image 8-bit grayscale 256x288
            width, height = 256, 288
            
            if len(image_data) < width * height:
                print(f"⚠ Données incomplètes ({len(image_data)} bytes)")
                # Padding si nécessaire
                image_data.extend([0] * (width * height - len(image_data)))
            
            image_array = np.frombuffer(image_data[:width*height], dtype=np.uint8)
            image_array = image_array.reshape((height, width))
            
            return image_array
            
        except Exception as e:
            print(f"❌ Erreur conversion image: {e}")
            return None
    
    def save_image(self, image_array, filename):
        """
        Sauvegarde l'image de l'empreinte
        
        Args:
            image_array: Image numpy
            filename: Nom du fichier
        """
        if image_array is None:
            return False
        
        try:
            img = Image.fromarray(image_array)
            img.save(filename)
            print(f"✓ Image sauvegardée: {filename}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def extract_template(self, image_array):
        """
        Extrait un template de l'empreinte (minuties)
        Version simplifiée - pour production, utilisez un algo plus robuste
        
        Args:
            image_array: Image numpy
            
        Returns:
            dict: Template avec minuties
        """
        if image_array is None:
            return None
        
        try:
            from scipy import ndimage
            from skimage import morphology, feature
            
            # Normalisation
            img = (image_array - image_array.min()) / (image_array.max() - image_array.min())
            
            # Binarisation
            threshold = img.mean()
            binary = img > threshold
            
            # Squelettisation
            skeleton = morphology.skeletonize(binary)
            
            # Détection des minuties (fins et bifurcations)
            minutiae = []
            
            # Version simplifiée: détection des points d'intérêt
            corners = feature.corner_peaks(feature.corner_harris(img), min_distance=5)
            
            for y, x in corners:
                minutiae.append({
                    'x': int(x),
                    'y': int(y),
                    'type': 'corner',  # Simplification
                    'angle': 0
                })
            
            template = {
                'minutiae': minutiae,
                'image_shape': image_array.shape,
                'quality': len(minutiae)  # Score de qualité basique
            }
            
            print(f"✓ Template extrait: {len(minutiae)} minuties")
            return template
            
        except ImportError as e:
            print(f"⚠ Modules manquants pour extraction: {e}")
            # Fallback: utiliser l'image brute comme template
            return {
                'image_raw': image_array.tobytes(),
                'image_shape': image_array.shape,
                'quality': 50
            }
        except Exception as e:
            print(f"❌ Erreur extraction: {e}")
            return None
    
    def __enter__(self):
        """Support pour context manager (with statement)"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique"""
        self.disconnect()


# Fonction helper pour auto-détection
def find_fingerprint_readers():
    """
    Recherche automatique de lecteurs d'empreintes
    
    Returns:
        list: Liste de tuples (vendor_id, product_id, description)
    """
    devices = usb.core.find(find_all=True)
    readers = []
    
    # Mots-clés pour identifier les lecteurs
    keywords = ['fingerprint', 'finger', 'biometric', 'reader', 'scanner']
    
    for dev in devices:
        try:
            product = usb.util.get_string(dev, dev.iProduct) if dev.iProduct else ""
            manufacturer = usb.util.get_string(dev, dev.iManufacturer) if dev.iManufacturer else ""
            
            desc = f"{manufacturer} {product}".lower()
            
            if any(kw in desc for kw in keywords):
                readers.append((dev.idVendor, dev.idProduct, f"{manufacturer} - {product}"))
        except:
            pass
    
    return readers

