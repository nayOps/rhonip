#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import sqlite3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configuration de la base de données
DB_PATH = "rh_database.db"

print("🗄️ SERVEUR AVEC BASE DE DONNÉES SQLITE")
print("=" * 50)
print("📱 Prêt pour l'enregistrement depuis l'APK")
print("=" * 50)

def init_database():
    """Initialiser la base de données"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Table des employés
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nin TEXT,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            middleName TEXT,
            email TEXT,
            phoneNumber TEXT,
            jobTitle TEXT,
            department TEXT,
            grossSalary TEXT,
            hireDate TEXT,
            photoPath TEXT,
            fingerprintTemplate TEXT,
            fingerprintFinger TEXT,
            biometricEnrollmentDate TEXT,
            biometricEnrolled BOOLEAN DEFAULT 0,
            numberOfChildren INTEGER DEFAULT 0,
            received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des présences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employeeId INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT NOT NULL,
            fingerprintUsed TEXT,
            status TEXT DEFAULT 'present',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employeeId) REFERENCES employees (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Base de données initialisée")

def get_employees():
    """Récupérer tous les employés"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees ORDER BY id')
    employees = []
    for row in cursor.fetchall():
        employee = {
            'id': row[0],
            'nin': row[1],
            'firstName': row[2],
            'lastName': row[3],
            'middleName': row[4],
            'email': row[5],
            'phoneNumber': row[6],
            'jobTitle': row[7],
            'department': row[8],
            'grossSalary': row[9],
            'hireDate': row[10],
            'photoPath': row[11],
            'fingerprintTemplate': row[12],
            'fingerprintFinger': row[13],
            'biometricEnrollmentDate': row[14],
            'biometricEnrolled': bool(row[15]),
            'numberOfChildren': row[16],
            'received_at': row[17]
        }
        employees.append(employee)
    conn.close()
    return employees

def get_attendance():
    """Récupérer toutes les présences"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM attendance ORDER BY timestamp DESC')
    attendance = []
    for row in cursor.fetchall():
        att = {
            'id': row[0],
            'employeeId': row[1],
            'date': row[2],
            'time': row[3],
            'type': row[4],
            'fingerprintUsed': row[5],
            'status': row[6],
            'timestamp': row[7]
        }
        attendance.append(att)
    conn.close()
    return attendance

def add_employee(data):
    """Ajouter un employé"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO employees (nin, firstName, lastName, middleName, email, phoneNumber, 
                             jobTitle, department, grossSalary, hireDate, photoPath, 
                             fingerprintTemplate, fingerprintFinger, biometricEnrollmentDate, 
                             biometricEnrolled, numberOfChildren)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('nin', ''),
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
    return employee_id

def add_attendance(employee_id, attendance_type, fingerprint_used):
    """Ajouter une présence"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute('''
        INSERT INTO attendance (employeeId, date, time, type, fingerprintUsed)
        VALUES (?, ?, ?, ?, ?)
    ''', (employee_id, date, time, attendance_type, fingerprint_used))
    
    attendance_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return attendance_id

def find_employee_by_fingerprint(fingerprint_template):
    """Trouver un employé par son template d'empreinte"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Recherche par correspondance de template
    cursor.execute('''
        SELECT * FROM employees 
        WHERE biometricEnrolled = 1 
        AND fingerprintTemplate LIKE ?
    ''', (f'%{fingerprint_template}%',))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'nin': row[1],
            'firstName': row[2],
            'lastName': row[3],
            'middleName': row[4],
            'email': row[5],
            'phoneNumber': row[6],
            'jobTitle': row[7],
            'department': row[8],
            'grossSalary': row[9],
            'hireDate': row[10],
            'photoPath': row[11],
            'fingerprintTemplate': row[12],
            'fingerprintFinger': row[13],
            'biometricEnrollmentDate': row[14],
            'biometricEnrolled': bool(row[15]),
            'numberOfChildren': row[16],
            'received_at': row[17]
        }
    return None

class DatabaseHandler(BaseHTTPRequestHandler):
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
            
            attendance = get_attendance()
            response = {
                "status": "success",
                "total": len(attendance),
                "data": attendance
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
                
                employee_id = add_employee(data)
                
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
                
        elif self.path == '/api/attendance':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                attendance_id = add_attendance(
                    data.get('employeeId'),
                    data.get('type'),
                    data.get('fingerprintUsed', 'fingerprint_capture')
                )
                
                print(f"📅 PRÉSENCE ENREGISTRÉE EN BASE:")
                print(f"   ID: {attendance_id}")
                print(f"   Employé: {data.get('employeeId', 'N/A')}")
                print(f"   Type: {data.get('type', 'N/A')}")
                print("=" * 50)
                
                self.send_response(201)
                self.send_header('Content-type', 'application/json')
                self._set_cors_headers()
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Présence enregistrée en base de données",
                    "id": attendance_id
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur présence: {e}")
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
    # Initialiser la base de données
    init_database()
    
    # Démarrer le serveur
    server = HTTPServer(('0.0.0.0', 8082), DatabaseHandler)
    print("🚀 Serveur avec base de données démarré sur http://0.0.0.0:8082")
    print("🗄️ Base de données SQLite: rh_database.db")
    server.serve_forever()
