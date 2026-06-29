#!/usr/bin/env python3
"""
Endpoint de test simple pour diagnostiquer le problème de l'APK
"""

import json
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/employees/mobile':
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"📱 DONNÉES REÇUES DE L'APK:")
                print(f"   Path: {self.path}")
                print(f"   Headers: {dict(self.headers)}")
                print(f"   Data: {data}")
                print("=" * 50)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "status": "success",
                    "message": "Données reçues avec succès",
                    "received_at": datetime.datetime.now().isoformat(),
                    "data_received": data
                }
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                print(f"❌ ERREUR: {e}")
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {"error": str(e)}
                self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"📡 {format % args}")

def start_server():
    server_address = ('0.0.0.0', 8083)
    httpd = HTTPServer(server_address, TestHandler)
    
    print("🚀 Serveur de test démarré sur le port 8083")
    print("📡 URL: http://192.168.1.73:8083/api/employees/mobile")
    print("🔄 En attente de connexions de l'APK...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
        httpd.shutdown()

if __name__ == '__main__':
    start_server()


