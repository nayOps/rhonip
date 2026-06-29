#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration de la base de données
DB_PATH = "rh_database.db"

print("🧪 SERVEUR DE TEST AVEC BASE DE DONNÉES")
print("=" * 50)

def get_employees():
    """Récupérer tous les employés"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees ORDER BY id')
    employees = []
    for row in cursor.fetchall():
        employee = {
            'id': row[0],
            'firstName': row[2],
            'lastName': row[3],
            'biometricEnrolled': bool(row[15])
        }
        employees.append(employee)
    conn.close()
    return employees

class TestHandler(BaseHTTPRequestHandler):
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
            
            employees = get_employees()
            print(f"📊 EMPLOYES DANS LA BASE: {len(employees)}")
            
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
                "total": 0,
                "data": []
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path.startswith('/api/employees/'):
            # Détail d'un employé spécifique
            try:
                employee_id = int(self.path.split('/')[-1])
                employees = get_employees()
                employee = next((emp for emp in employees if emp['id'] == employee_id), None)
                
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
            except ValueError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                response = {"status": "error", "message": "ID d'employé invalide"}
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
                
                # Ajouter l'employé à la base de données
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO employees (firstName, lastName, middleName, email, phoneNumber, 
                                         jobTitle, department, grossSalary, hireDate, photoPath, 
                                         fingerprintTemplate, fingerprintFinger, biometricEnrollmentDate, 
                                         biometricEnrolled, numberOfChildren)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data.get('firstName', ''),
                    data.get('lastName', ''),
                    data.get('middleName', ''),
                    data.get('email', ''),
                    data.get('phoneNumber', ''),
                    data.get('jobTitle', ''),
                    data.get('department', ''),
                    data.get('grossSalary', ''),
                    data.get('hireDate', ''),
                    data.get('photoPath', ''),
                    data.get('fingerprintTemplate', ''),
                    data.get('fingerprintFinger', ''),
                    data.get('biometricEnrollmentDate', ''),
                    data.get('biometricEnrolled', False),
                    data.get('numberOfChildren', 0)
                ))
                
                employee_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                print(f"📱 NOUVEL EMPLOYÉ ENREGISTRÉ EN BASE:")
                print(f"   ID: {employee_id}")
                print(f"   Nom: {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')}")
                print(f"   Biométrie: {data.get('biometricEnrolled', False)}")
                print("=" * 50)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Employé enregistré en base de données",
                    "id": employee_id
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur enregistrement: {e}")
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
        pass

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 8083), TestHandler)
    print("🚀 Serveur de test démarré sur http://0.0.0.0:8083")
    server.serve_forever()
