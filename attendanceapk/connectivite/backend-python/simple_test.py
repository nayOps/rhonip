#!/usr/bin/env python3
"""
Serveur de test ultra-simple pour la connectivité
"""

import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Stockage des données
data_storage = []

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/test':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "success",
                "message": "Serveur de test actif",
                "timestamp": datetime.datetime.now().isoformat(),
                "total_received": len(data_storage)
            }
            self.wfile.write(json.dumps(response).encode())
            
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "status": "success",
                "total": len(data_storage),
                "data": data_storage
            }
            self.wfile.write(json.dumps(response).encode())
            
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/test':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                data['received_at'] = datetime.datetime.now().isoformat()
                data['id'] = len(data_storage) + 1
                data_storage.append(data)
                
                print(f"📱 Données reçues: {data}")
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Données reçues",
                    "id": data['id']
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ Erreur: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"status": "error", "message": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

def start_server():
    server_address = ('0.0.0.0', 8082)
    httpd = HTTPServer(server_address, TestHandler)
    
    print("🚀 Serveur de test démarré")
    print("📡 URL: http://192.168.1.73:8082/api/test")
    print("🔄 En attente de connexions...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        httpd.shutdown()

if __name__ == '__main__':
    start_server()
