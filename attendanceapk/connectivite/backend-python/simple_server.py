#!/usr/bin/env python3
"""
Serveur Python simple SANS dépendances externes
Utilise uniquement les modules standard de Python
"""

import json
import datetime
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Stockage en mémoire des données reçues - VIDÉ POUR TEST PROPRE
received_data = []
attendance_data = []

print("🧹 BACKEND REDÉMARRÉ - DONNÉES VIDÉES POUR TEST PROPRE")
print("=" * 60)
print("📱 Prêt pour l'enregistrement depuis l'APK")
print("=" * 60)

class SimpleHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        """Définir les headers CORS pour toutes les réponses"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS (preflight CORS)"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        global received_data, attendance_data
        
        if self.path == '/api/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Serveur Python simple actif",
                "timestamp": datetime.datetime.now().isoformat(),
                "total_received": len(received_data)
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "total": len(received_data),
                "data": received_data
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/fingerprints':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            # Lister les fichiers d'empreintes
            fingerprints_dir = "fingerprints"
            fingerprint_files = []
            
            if os.path.exists(fingerprints_dir):
                for filename in os.listdir(fingerprints_dir):
                    if filename.endswith('.txt'):
                        filepath = os.path.join(fingerprints_dir, filename)
                        with open(filepath, 'r') as f:
                            content = f.read()
                        fingerprint_files.append({
                            "filename": filename,
                            "content": content
                        })
            
            response = {
                "status": "success",
                "total_fingerprints": len(fingerprint_files),
                "fingerprints": fingerprint_files
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path.startswith('/api/employees/'):
            # Détail d'un employé spécifique
            employee_id = int(self.path.split('/')[-1])
            employee = next((emp for emp in received_data if emp.get('id') == employee_id), None)
            
            if employee:
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "data": employee
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "error",
                    "message": "Employé non trouvé"
                }
                self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/attendance':
            # Liste des présences
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "total": len(attendance_data),
                "data": attendance_data
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path.startswith('/api/attendance/'):
            # Présences d'un employé spécifique
            employee_id = int(self.path.split('/')[-1])
            employee_attendance = [att for att in attendance_data if att.get('employeeId') == employee_id]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "total": len(employee_attendance),
                "data": employee_attendance
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/stats':
            # Statistiques globales
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            total_employees = len(received_data)
            biometric_enrolled = len([emp for emp in received_data if emp.get('biometricEnrolled', False)])
            total_attendance = len(attendance_data)
            
            response = {
                "status": "success",
                "data": {
                    "total_employees": total_employees,
                    "biometric_enrolled": biometric_enrolled,
                    "total_attendance_records": total_attendance,
                    "enrollment_rate": (biometric_enrolled / total_employees * 100) if total_employees > 0 else 0
                }
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/clear':
            # VIDAGE COMPLET DES DONNÉES
            received_data = []
            attendance_data = []
            
            print("🧹 DONNÉES VIDÉES - Backend prêt pour un test propre")
            print("=" * 60)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Toutes les données ont été vidées",
                "employees_cleared": True,
                "attendance_cleared": True,
                "timestamp": datetime.datetime.now().isoformat()
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Gérer les requêtes POST"""
        global received_data, attendance_data
        
        if self.path == '/api/test':
            try:
                # Lire les données JSON
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Ajouter un timestamp et un ID
                data['received_at'] = datetime.datetime.now().isoformat()
                data['id'] = len(received_data) + 1
                
                # Stocker les données
                received_data.append(data)
                
                # Sauvegarder les empreintes si présentes
                save_fingerprints(data)
                
                print(f"📱 Données reçues de l'APK:")
                print(f"   ID: {data['id']}")
                print(f"   Timestamp: {data['received_at']}")
                print("")
                print("📋 INFORMATIONS PERSONNELLES:")
                print(f"   NIN: {data.get('nin', 'N/A')}")
                print(f"   Prénom: {data.get('firstName', 'N/A')}")
                print(f"   Nom: {data.get('lastName', 'N/A')}")
                print(f"   Nom du milieu: {data.get('middleName', 'N/A')}")
                print(f"   Email: {data.get('email', 'N/A')}")
                print(f"   Téléphone: {data.get('phoneNumber', 'N/A')}")
                print(f"   Poste: {data.get('jobTitle', 'N/A')}")
                print(f"   Département: {data.get('department', 'N/A')}")
                print(f"   Salaire: {data.get('grossSalary', 'N/A')}")
                print(f"   Date d'embauche: {data.get('hireDate', 'N/A')}")
                print("")
                print("📸 DONNÉES BIOMÉTRIQUES:")
                print(f"   Photo: {data.get('photoPath', 'N/A')}")
                print(f"   Empreintes: {data.get('fingerprintTemplate', 'N/A')}")
                print(f"   Doigts: {data.get('fingerprintFinger', 'N/A')}")
                print(f"   Date d'enregistrement: {data.get('biometricEnrollmentDate', 'N/A')}")
                print(f"   Enregistré: {data.get('biometricEnrolled', 'N/A')}")
                print(f"   Nombre d'enfants: {data.get('numberOfChildren', 'N/A')}")
                print("")
                print("👆 DÉTAILS DES 10 EMPREINTES:")
                # Analyser les empreintes si elles sont présentes
                fingerprint_template = data.get('fingerprintTemplate', '')
                if fingerprint_template and fingerprint_template != 'N/A':
                    print(f"   Template complet: {len(fingerprint_template)} caractères")
                    # Parser les empreintes individuelles
                    fingerprints = fingerprint_template.split(';')
                    for i, fingerprint in enumerate(fingerprints):
                        if fingerprint.strip():
                            parts = fingerprint.split(':')
                            if len(parts) >= 2:
                                finger_name = parts[0]
                                template_size = parts[1]
                                print(f"   {i+1:2d}. {finger_name}: {template_size} bytes")
                            else:
                                print(f"   {i+1:2d}. Empreinte {i+1}: {len(fingerprint)} caractères")
                else:
                    print("   Aucune empreinte reçue")
                print("")
                print("🔍 TOUS LES CHAMPS REÇUS:")
                for key, value in data.items():
                    if key not in ['id', 'received_at']:
                        print(f"   {key}: {value}")
                print("=" * 80)
                
                # Répondre avec succès
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Données reçues avec succès",
                    "id": data['id'],
                    "received_at": data['received_at'],
                    "total_received": len(received_data)
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur lors de la réception des données: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "error",
                    "message": f"Erreur serveur: {str(e)}"
                }
                self.wfile.write(json.dumps(response).encode())
                
        elif self.path == '/api/attendance':
            # Enregistrer une présence
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                data['id'] = len(attendance_data) + 1
                data['timestamp'] = datetime.datetime.now().isoformat()
                attendance_data.append(data)
                
                print(f"📅 Présence enregistrée:")
                print(f"   ID: {data['id']}")
                print(f"   Employé: {data.get('employeeId', 'N/A')}")
                print(f"   Date: {data.get('date', 'N/A')}")
                print(f"   Heure: {data.get('time', 'N/A')}")
                print(f"   Type: {data.get('type', 'N/A')}")
                print(f"   Empreinte: {data.get('fingerprintUsed', 'N/A')}")
                print("=" * 50)
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Présence enregistrée avec succès",
                    "id": data['id'],
                    "timestamp": data['timestamp']
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur enregistrement présence: {str(e)}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "error",
                    "message": f"Erreur serveur: {str(e)}"
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.end_headers()
    
    def log_message(self, format, *args):
        """Désactiver les logs par défaut"""
        pass

def save_fingerprints(data):
    """Sauvegarder les empreintes dans des fichiers séparés"""
    try:
        fingerprint_template = data.get('fingerprintTemplate', '')
        if not fingerprint_template or fingerprint_template == 'N/A':
            return
        
        # Créer le dossier pour les empreintes
        fingerprints_dir = "fingerprints"
        if not os.path.exists(fingerprints_dir):
            os.makedirs(fingerprints_dir)
        
        # Parser les empreintes individuelles
        fingerprints = fingerprint_template.split(';')
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        print(f"💾 Sauvegarde des empreintes pour l'employé {data.get('firstName', 'Unknown')} {data.get('lastName', '')}")
        
        for i, fingerprint in enumerate(fingerprints):
            if fingerprint.strip():
                parts = fingerprint.split(':')
                if len(parts) >= 2:
                    finger_name = parts[0]
                    template_size = parts[1]
                    
                    # Créer un fichier pour chaque empreinte
                    filename = f"{fingerprints_dir}/fingerprint_{timestamp}_{finger_name}_{i+1}.txt"
                    with open(filename, 'w') as f:
                        f.write(f"Employé: {data.get('firstName', 'Unknown')} {data.get('lastName', '')}\n")
                        f.write(f"Doigt: {finger_name}\n")
                        f.write(f"Taille: {template_size} bytes\n")
                        f.write(f"Timestamp: {data.get('received_at', '')}\n")
                        f.write(f"Template: {fingerprint}\n")
                    
                    print(f"   ✅ {finger_name} sauvegardé: {filename}")
        
        print(f"💾 Toutes les empreintes sauvegardées dans le dossier '{fingerprints_dir}/'")
        
    except Exception as e:
        print(f"❌ Erreur sauvegarde empreintes: {str(e)}")

def start_server():
    """Démarrer le serveur"""
    server_address = ('0.0.0.0', 8082)
    httpd = HTTPServer(server_address, SimpleHandler)
    
    print("🚀 Démarrage du serveur de test de connectivité")
    print("📡 Endpoint: http://0.0.0.0:8082/api/test")
    print("🔍 GET: Vérifier la connectivité")
    print("📱 POST: Recevoir des données de l'APK")
    print("📊 GET /api/data: Voir toutes les données")
    print("👆 GET /api/fingerprints: Voir toutes les empreintes sauvegardées")
    print("=" * 60)
    print("✅ Serveur démarré sur le port 8082")
    print("🔄 En attente de connexions...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        httpd.shutdown()

if __name__ == '__main__':
    start_server()
