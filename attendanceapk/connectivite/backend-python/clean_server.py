#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
            
        elif self.path == '/api/attendance':
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
            
        elif self.path == '/api/clear':
            # VIDAGE COMPLET DES DONNÉES
            global received_data, attendance_data
            received_data.clear()
            attendance_data.clear()
            
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
            self._set_cors_headers()
            self.end_headers()
    
    def do_POST(self):
        """Gérer les requêtes POST"""
        if self.path == '/api/test':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                data['received_at'] = datetime.datetime.now().isoformat()
                data['id'] = len(received_data) + 1
                
                received_data.append(data)
                
                print(f"📱 NOUVEL EMPLOYÉ ENREGISTRÉ:")
                print(f"   ID: {data['id']}")
                print(f"   Nom: {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')}")
                print(f"   Email: {data.get('email', 'N/A')}")
                print(f"   Biométrie: {data.get('biometricEnrolled', False)}")
                print("=" * 60)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Employé enregistré avec succès",
                    "id": data['id'],
                    "received_at": data['received_at'],
                    "total_received": len(received_data)
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur lors de l'enregistrement: {str(e)}")
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
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                data['id'] = len(attendance_data) + 1
                data['timestamp'] = datetime.datetime.now().isoformat()
                attendance_data.append(data)
                
                print(f"📅 PRÉSENCE ENREGISTRÉE:")
                print(f"   ID: {data['id']}")
                print(f"   Employé: {data.get('employeeId', 'N/A')}")
                print(f"   Type: {data.get('type', 'N/A')}")
                print(f"   Date: {data.get('date', 'N/A')}")
                print("=" * 60)
                
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
            self._set_cors_headers()
            self.end_headers()
    
    def log_message(self, format, *args):
        """Désactiver les logs par défaut"""
        pass

def start_server():
    server_address = ('0.0.0.0', 8082)
    httpd = HTTPServer(server_address, SimpleHandler)
    print(f"🚀 Serveur démarré sur http://0.0.0.0:8082")
    print(f"📱 Prêt pour l'enregistrement depuis l'APK")
    httpd.serve_forever()

if __name__ == '__main__':
    start_server()
