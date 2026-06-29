"""
Capture d'iris via caméra USB
"""

import cv2
import numpy as np
import json
import time
from pathlib import Path


class IrisCamera:
    """
    Classe pour capturer des images d'iris via caméra
    """
    
    def __init__(self, camera_index=0, config_file='config.json'):
        """
        Initialise la caméra
        
        Args:
            camera_index: Index de la caméra (0 = caméra par défaut)
            config_file: Fichier de configuration
        """
        self.camera_index = camera_index
        self.camera = None
        self.config = {}
        self.connected = False
        
        # Charger la configuration
        self.load_config(config_file)
        
        # Charger le détecteur de visage et d'yeux
        self.face_cascade = None
        self.eye_cascade = None
        self.load_cascades()
    
    def load_config(self, config_file):
        """Charge la configuration"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                iris_config = config.get('iris', {})
                
                self.camera_index = iris_config.get('camera_index', 0)
                self.resolution = iris_config.get('resolution', {'width': 640, 'height': 480})
                self.config = iris_config
        except Exception as e:
            print(f"⚠ Erreur chargement config: {e}")
            self.resolution = {'width': 640, 'height': 480}
    
    def load_cascades(self):
        """Charge les classificateurs Haar Cascade pour détection"""
        try:
            # Chemins vers les cascades OpenCV
            cascade_path = cv2.data.haarcascades
            
            face_cascade_path = cascade_path + 'haarcascade_frontalface_default.xml'
            eye_cascade_path = cascade_path + 'haarcascade_eye.xml'
            
            self.face_cascade = cv2.CascadeClassifier(face_cascade_path)
            self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
            
            if self.face_cascade.empty() or self.eye_cascade.empty():
                print("⚠ Erreur chargement des cascades Haar")
            else:
                print("✓ Cascades Haar chargées")
        except Exception as e:
            print(f"⚠ Erreur chargement cascades: {e}")
    
    def connect(self):
        """
        Ouvre la caméra
        
        Returns:
            bool: True si ouverture réussie
        """
        print(f"📷 Ouverture de la caméra #{self.camera_index}...")
        
        self.camera = cv2.VideoCapture(self.camera_index)
        
        if not self.camera.isOpened():
            print("❌ Impossible d'ouvrir la caméra")
            return False
        
        # Configurer la résolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution['width'])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution['height'])
        
        # Vérifier
        actual_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        actual_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
        
        print(f"✓ Caméra ouverte ({int(actual_width)}x{int(actual_height)})")
        
        self.connected = True
        return True
    
    def disconnect(self):
        """Ferme la caméra"""
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
        self.connected = False
        print("✓ Caméra fermée")
    
    def capture_frame(self):
        """
        Capture une frame
        
        Returns:
            numpy.ndarray: Frame capturée ou None
        """
        if not self.connected:
            print("❌ Caméra non connectée")
            return None
        
        ret, frame = self.camera.read()
        
        if not ret:
            print("❌ Erreur capture frame")
            return None
        
        return frame
    
    def detect_face(self, frame):
        """
        Détecte le visage dans la frame
        
        Args:
            frame: Image à analyser
            
        Returns:
            tuple: (x, y, w, h) du visage ou None
        """
        if self.face_cascade is None:
            return None
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            # Retourner le visage le plus grand
            return max(faces, key=lambda f: f[2] * f[3])
        
        return None
    
    def detect_eyes(self, frame, face_region=None):
        """
        Détecte les yeux dans la frame
        
        Args:
            frame: Image à analyser
            face_region: (x, y, w, h) de la région du visage (optionnel)
            
        Returns:
            list: Liste de tuples (x, y, w, h) pour chaque œil
        """
        if self.eye_cascade is None:
            return []
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Si région du visage fournie, rechercher uniquement dedans
        if face_region is not None:
            x, y, w, h = face_region
            roi_gray = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
            
            # Ajuster les coordonnées
            eyes = [(x + ex, y + ey, ew, eh) for (ex, ey, ew, eh) in eyes]
        else:
            eyes = self.eye_cascade.detectMultiScale(gray, 1.1, 5)
        
        # Filtrer et garder les 2 meilleurs yeux
        if len(eyes) > 2:
            eyes = sorted(eyes, key=lambda e: e[2] * e[3], reverse=True)[:2]
        
        return eyes
    
    def extract_eye_region(self, frame, eye_bbox):
        """
        Extrait la région de l'œil
        
        Args:
            frame: Image source
            eye_bbox: (x, y, w, h) de l'œil
            
        Returns:
            numpy.ndarray: Région de l'œil
        """
        x, y, w, h = eye_bbox
        
        # Agrandir légèrement la région
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = w + 2 * padding
        h = h + 2 * padding
        
        eye_region = frame[y:y+h, x:x+w]
        return eye_region
    
    def capture_iris(self, timeout=30, preview=True):
        """
        Capture une image d'iris avec détection automatique
        
        Args:
            timeout: Temps d'attente maximum en secondes
            preview: Afficher la prévisualisation
            
        Returns:
            dict: Informations de capture avec image d'iris
        """
        print("\n👁️  Capture d'iris")
        print("=" * 50)
        print("Positionnez votre œil face à la caméra")
        print("Appuyez sur ESPACE pour capturer, ESC pour annuler\n")
        
        start_time = time.time()
        best_capture = None
        
        while time.time() - start_time < timeout:
            frame = self.capture_frame()
            
            if frame is None:
                continue
            
            # Copie pour affichage
            display_frame = frame.copy()
            
            # Détecter le visage
            face = self.detect_face(frame)
            
            if face is not None:
                fx, fy, fw, fh = face
                cv2.rectangle(display_frame, (fx, fy), (fx+fw, fy+fh), (0, 255, 0), 2)
                
                # Détecter les yeux
                eyes = self.detect_eyes(frame, face)
                
                if len(eyes) > 0:
                    for (ex, ey, ew, eh) in eyes:
                        cv2.rectangle(display_frame, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
                    
                    # Préparer la meilleure capture
                    best_eye = eyes[0]  # Premier œil détecté
                    eye_region = self.extract_eye_region(frame, best_eye)
                    
                    best_capture = {
                        'full_frame': frame,
                        'eye_region': eye_region,
                        'eye_bbox': best_eye,
                        'timestamp': time.time()
                    }
                    
                    cv2.putText(display_frame, "Oeil detecte! ESPACE = capturer", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                else:
                    cv2.putText(display_frame, "Visage detecte, cherche les yeux...", (10, 30),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            else:
                cv2.putText(display_frame, "Aucun visage detecte", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if preview:
                cv2.imshow('Capture Iris', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                
                if key == 27:  # ESC
                    print("❌ Capture annulée")
                    cv2.destroyAllWindows()
                    return None
                
                elif key == 32:  # SPACE
                    if best_capture is not None:
                        print("✓ Image capturée!")
                        cv2.destroyAllWindows()
                        return best_capture
        
        print("⏱️ Timeout atteint")
        
        if preview:
            cv2.destroyAllWindows()
        
        return best_capture
    
    def capture_iris_batch(self, num_captures=3, delay=1):
        """
        Capture plusieurs images d'iris
        
        Args:
            num_captures: Nombre de captures
            delay: Délai entre captures en secondes
            
        Returns:
            list: Liste de captures
        """
        captures = []
        
        for i in range(num_captures):
            print(f"\n📸 Capture {i+1}/{num_captures}")
            
            capture = self.capture_iris(timeout=30, preview=True)
            
            if capture:
                captures.append(capture)
                
                if i < num_captures - 1:
                    print(f"⏳ Attente {delay}s...")
                    time.sleep(delay)
            else:
                print("❌ Capture échouée")
                break
        
        return captures
    
    def save_image(self, image, filename):
        """
        Sauvegarde une image
        
        Args:
            image: Image numpy
            filename: Nom du fichier
        """
        try:
            cv2.imwrite(filename, image)
            print(f"✓ Image sauvegardée: {filename}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde: {e}")
            return False
    
    def __enter__(self):
        """Support pour context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique"""
        self.disconnect()


# Fonction helper
def list_cameras(max_index=10):
    """
    Liste les caméras disponibles
    
    Args:
        max_index: Index maximum à tester
        
    Returns:
        list: Liste d'indices de caméras disponibles
    """
    cameras = []
    
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, _ = cap.read()
            if ret:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cameras.append({
                    'index': i,
                    'resolution': f'{width}x{height}'
                })
            cap.release()
    
    return cameras

