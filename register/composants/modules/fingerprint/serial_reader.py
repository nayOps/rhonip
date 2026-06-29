"""
Lecteur d'empreintes via port série (UART)
Pour capteurs avec interface série
"""

import serial
import json
import time
import numpy as np
from PIL import Image


class SerialFingerprintReader:
    """
    Classe pour communiquer avec un lecteur d'empreintes via port série
    Supporte les protocoles communs des capteurs série
    """
    
    def __init__(self, port=None, baudrate=9600, timeout=2, config_file='config.json'):
        """
        Initialise le lecteur série
        
        Args:
            port: Port série (ex: '/dev/ttyUSB0' ou 'COM3')
            baudrate: Vitesse de communication
            timeout: Timeout en secondes
            config_file: Fichier de configuration
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.connected = False
        
        # Charger config si port non fourni
        if port is None:
            self.load_config(config_file)
    
    def load_config(self, config_file):
        """Charge la configuration"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                serial_config = config.get('fingerprint', {}).get('serial', {})
                
                self.port = serial_config.get('port', '/dev/ttyUSB0')
                self.baudrate = serial_config.get('baudrate', 9600)
                self.timeout = serial_config.get('timeout', 2)
        except Exception as e:
            print(f"⚠ Erreur chargement config: {e}")
    
    def connect(self):
        """
        Connecte au port série
        
        Returns:
            bool: True si connexion réussie
        """
        try:
            print(f"🔌 Connexion à {self.port} @ {self.baudrate} bauds...")
            
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            time.sleep(0.5)  # Attendre stabilisation
            
            # Vider les buffers
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            
            self.connected = True
            print("✓ Connecté!")
            return True
            
        except serial.SerialException as e:
            print(f"❌ Erreur connexion: {e}")
            return False
    
    def disconnect(self):
        """Déconnecte du port série"""
        if self.serial and self.serial.is_open:
            self.serial.close()
        self.connected = False
        print("✓ Déconnecté")
    
    def send_command(self, command):
        """
        Envoie une commande
        
        Args:
            command: bytes à envoyer
            
        Returns:
            bool: True si envoi réussi
        """
        if not self.connected:
            print("❌ Non connecté")
            return False
        
        try:
            self.serial.write(command)
            self.serial.flush()
            return True
        except Exception as e:
            print(f"❌ Erreur envoi: {e}")
            return False
    
    def read_response(self, size=None, timeout=None):
        """
        Lit la réponse
        
        Args:
            size: Nombre d'octets à lire (None = lecture jusqu'à timeout)
            timeout: Timeout spécifique pour cette lecture
            
        Returns:
            bytes: Données lues
        """
        if not self.connected:
            return None
        
        try:
            if timeout:
                old_timeout = self.serial.timeout
                self.serial.timeout = timeout
            
            if size:
                data = self.serial.read(size)
            else:
                data = self.serial.read_until()
            
            if timeout:
                self.serial.timeout = old_timeout
            
            return data
            
        except Exception as e:
            print(f"❌ Erreur lecture: {e}")
            return None
    
    def calculate_checksum(self, data):
        """
        Calcule le checksum (méthode commune)
        
        Args:
            data: bytes pour calcul
            
        Returns:
            int: Checksum
        """
        return sum(data) & 0xFF
    
    def send_packet(self, command_id, data=b''):
        """
        Envoie un paquet formaté (protocole commun)
        Format: [Header(2)] [Addr(4)] [PID(1)] [Length(2)] [Data] [Checksum(2)]
        
        Args:
            command_id: ID de la commande
            data: Données optionnelles
            
        Returns:
            bool: True si envoi réussi
        """
        # Header standard pour beaucoup de capteurs
        header = b'\xEF\x01'
        
        # Adresse par défaut
        address = b'\xFF\xFF\xFF\xFF'
        
        # Package Identifier
        pid = bytes([0x01])  # Command packet
        
        # Longueur = data + checksum
        length = len(data) + 3  # +3 pour PID et checksum
        length_bytes = length.to_bytes(2, 'big')
        
        # Données
        payload = bytes([command_id]) + data
        
        # Checksum
        checksum = sum(pid + length_bytes + payload) & 0xFFFF
        checksum_bytes = checksum.to_bytes(2, 'big')
        
        # Construction du paquet complet
        packet = header + address + pid + length_bytes + payload + checksum_bytes
        
        return self.send_command(packet)
    
    def read_packet(self, timeout=2):
        """
        Lit un paquet formaté
        
        Returns:
            dict: Paquet décodé ou None
        """
        # Chercher le header
        header = self.serial.read(2)
        
        if header != b'\xEF\x01':
            print("⚠ Header invalide")
            return None
        
        # Lire l'adresse
        address = self.serial.read(4)
        
        # Lire PID et longueur
        pid = self.serial.read(1)
        length_bytes = self.serial.read(2)
        length = int.from_bytes(length_bytes, 'big')
        
        # Lire les données
        data = self.serial.read(length - 2)  # -2 pour le checksum
        
        # Lire le checksum
        checksum = self.serial.read(2)
        
        return {
            'pid': pid[0],
            'length': length,
            'data': data,
            'checksum': checksum
        }
    
    def verify_password(self, password=0x00000000):
        """
        Vérifie le mot de passe du module
        
        Args:
            password: Mot de passe (par défaut 0x00000000)
            
        Returns:
            bool: True si OK
        """
        print("🔐 Vérification du mot de passe...")
        
        password_bytes = password.to_bytes(4, 'big')
        
        if self.send_packet(0x13, password_bytes):
            response = self.read_packet()
            
            if response and len(response['data']) > 0:
                if response['data'][0] == 0x00:
                    print("✓ Mot de passe OK")
                    return True
        
        print("❌ Échec vérification mot de passe")
        return False
    
    def get_image(self):
        """
        Capture une image d'empreinte
        
        Returns:
            bool: True si capture OK
        """
        print("👆 Placez votre doigt sur le capteur...")
        
        # Commande GenImg (0x01)
        if self.send_packet(0x01):
            response = self.read_packet()
            
            if response and len(response['data']) > 0:
                status = response['data'][0]
                
                if status == 0x00:
                    print("✓ Image capturée")
                    return True
                elif status == 0x02:
                    print("❌ Pas de doigt détecté")
                elif status == 0x03:
                    print("❌ Échec de capture")
        
        return False
    
    def img_to_tz(self, buffer_id=1):
        """
        Convertit l'image en template
        
        Args:
            buffer_id: Numéro du buffer (1 ou 2)
            
        Returns:
            bool: True si conversion OK
        """
        print(f"🔄 Conversion en template (buffer {buffer_id})...")
        
        # Commande Img2Tz (0x02)
        if self.send_packet(0x02, bytes([buffer_id])):
            response = self.read_packet()
            
            if response and len(response['data']) > 0:
                status = response['data'][0]
                
                if status == 0x00:
                    print("✓ Template généré")
                    return True
                elif status == 0x06:
                    print("❌ Image désordonnée")
                elif status == 0x07:
                    print("❌ Minuties insuffisantes")
                elif status == 0x15:
                    print("❌ Image invalide")
        
        return False
    
    def match_templates(self):
        """
        Compare deux templates (buffer 1 et 2)
        
        Returns:
            tuple: (match, score)
        """
        print("🔍 Comparaison des templates...")
        
        # Commande Match (0x03)
        if self.send_packet(0x03):
            response = self.read_packet()
            
            if response and len(response['data']) >= 3:
                status = response['data'][0]
                
                if status == 0x00:
                    score = int.from_bytes(response['data'][1:3], 'big')
                    print(f"✓ Match! Score: {score}")
                    return (True, score)
                elif status == 0x08:
                    print("❌ Pas de correspondance")
                    return (False, 0)
        
        return (False, 0)
    
    def enroll_fingerprint(self):
        """
        Enregistre une nouvelle empreinte (processus complet)
        
        Returns:
            dict: Template ou None
        """
        print("\n📝 Enregistrement d'une nouvelle empreinte")
        print("=" * 50)
        
        # Première capture
        print("\n1️⃣ Première capture...")
        if not self.get_image():
            return None
        
        if not self.img_to_tz(1):
            return None
        
        print("\n⏳ Retirez votre doigt...")
        time.sleep(2)
        
        # Deuxième capture
        print("\n2️⃣ Deuxième capture (même doigt)...")
        if not self.get_image():
            return None
        
        if not self.img_to_tz(2):
            return None
        
        # Créer le modèle
        print("\n🔄 Création du modèle...")
        if self.send_packet(0x05):  # RegModel
            response = self.read_packet()
            
            if response and response['data'][0] == 0x00:
                print("✓ Modèle créé avec succès!")
                
                # Récupérer le template du buffer 1
                return {
                    'status': 'success',
                    'timestamp': time.time()
                }
        
        return None
    
    def verify_fingerprint(self):
        """
        Vérifie une empreinte
        
        Returns:
            bool: True si match
        """
        print("\n🔍 Vérification d'empreinte")
        print("=" * 50)
        
        if not self.get_image():
            return False
        
        if not self.img_to_tz(1):
            return False
        
        # Chercher dans la bibliothèque (commande Search: 0x04)
        # Page start: 0, Page num: 10 (exemple)
        search_params = bytes([0x01, 0x00, 0x00, 0x00, 0x0A])
        
        if self.send_packet(0x04, search_params):
            response = self.read_packet()
            
            if response and len(response['data']) >= 5:
                status = response['data'][0]
                
                if status == 0x00:
                    page_id = int.from_bytes(response['data'][1:3], 'big')
                    score = int.from_bytes(response['data'][3:5], 'big')
                    print(f"✓ Correspondance trouvée! ID: {page_id}, Score: {score}")
                    return True
                elif status == 0x09:
                    print("❌ Aucune correspondance")
        
        return False
    
    def __enter__(self):
        """Support pour context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique"""
        self.disconnect()

