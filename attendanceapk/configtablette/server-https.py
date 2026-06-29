#!/usr/bin/env python3
"""
HTTPS Server for MorphoTablet Testing
Requires: cert.pem and key.pem (run generate-cert.sh first)
"""

import http.server
import ssl
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8443  # Port HTTPS standard alternatif

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        print(f"\033[92m[{self.log_date_time_string()}]\033[0m {format%args}")

# Vérifier que les certificats existent
if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
    print("\033[91m❌ ERREUR: Certificats SSL manquants!\033[0m")
    print("\033[93mExécutez d'abord:\033[0m ./generate-cert.sh")
    exit(1)

httpd = http.server.HTTPServer(('', PORT), MyHTTPRequestHandler)

# Configurer SSL
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

print("\033[94m" + "="*60 + "\033[0m")
print("\033[96m    MorphoTablet HTTPS Server\033[0m")
print("\033[94m" + "="*60 + "\033[0m")
print(f"\n\033[92m✓ Serveur HTTPS démarré sur le port {PORT}\033[0m")
print(f"\n\033[93mAccess the interface at:\033[0m")
print(f"  • Local:   \033[96mhttps://localhost:{PORT}\033[0m")
print(f"  • Network: \033[96mhttps://192.168.100.101:{PORT}\033[0m")
print(f"\n\033[95m⚠️  Vous devrez accepter le certificat auto-signé\033[0m")
print(f"\n\033[91mPress Ctrl+C to stop\033[0m")
print("\033[94m" + "="*60 + "\033[0m\n")

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\n\n\033[91m✗ Server stopped\033[0m")
    httpd.shutdown()

