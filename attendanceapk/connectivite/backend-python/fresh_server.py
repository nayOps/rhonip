#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# NOUVELLES LISTES VIDES
employees = []
attendance = []

print("🆕 SERVEUR FRAIS DÉMARRÉ - DONNÉES VIDES")
print("=" * 50)
print("📱 Prêt pour l'enregistrement depuis l'APK")
print("=" * 50)

class FreshHandler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "total": len(employees),
                "data": employees
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/attendance':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self._set_cors_headers()
            self.end_headers()
            
            response = {
                "status": "success",
                "total": len(attendance),
                "data": attendance
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/test':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                data['id'] = len(employees) + 1
                data['received_at'] = datetime.datetime.now().isoformat()
                employees.append(data)
                
                print(f"📱 NOUVEL EMPLOYÉ:")
                print(f"   ID: {data['id']}")
                print(f"   Nom: {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')}")
                print(f"   Biométrie: {data.get('biometricEnrolled', False)}")
                print("=" * 50)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Employé enregistré",
                    "id": data['id']
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
                
        elif self.path == '/api/attendance':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                data['id'] = len(attendance) + 1
                data['timestamp'] = datetime.datetime.now().isoformat()
                attendance.append(data)
                
                print(f"📅 PRÉSENCE:")
                print(f"   ID: {data['id']}")
                print(f"   Employé: {data.get('employeeId', 'N/A')}")
                print(f"   Type: {data.get('type', 'N/A')}")
                print("=" * 50)
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Présence enregistrée",
                    "id": data['id']
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                self.send_response(500)
                self._set_cors_headers()
                self.end_headers()
        else:
            self.send_response(404)
            self._set_cors_headers()
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8082), FreshHandler)
    print("🚀 Serveur frais démarré sur http://0.0.0.0:8082")
    server.serve_forever()
