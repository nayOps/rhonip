#!/usr/bin/env python3
"""
Simple HTTP Server for MorphoTablet Testing
No dependencies, runs with standard Python 3
"""

import http.server
import socketserver
import os

# Change to the script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 8888

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers for cross-origin requests
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        # Custom logging with colors
        print(f"\033[92m[{self.log_date_time_string()}]\033[0m {format%args}")

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print("\033[94m" + "="*60 + "\033[0m")
    print("\033[96m    MorphoTablet Test Server\033[0m")
    print("\033[94m" + "="*60 + "\033[0m")
    print(f"\n\033[92m✓ Server started on port {PORT}\033[0m")
    print(f"\n\033[93mAccess the interface at:\033[0m")
    print(f"  • Local:   \033[96mhttp://localhost:{PORT}\033[0m")
    print(f"  • Network: \033[96mhttp://[YOUR_IP]:{PORT}\033[0m")
    print(f"\n\033[95mTo find your IP:\033[0m")
    print(f"  \033[90mip addr show | grep 'inet '\033[0m")
    print(f"\n\033[91mPress Ctrl+C to stop the server\033[0m")
    print("\033[94m" + "="*60 + "\033[0m\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n\033[91m✗ Server stopped\033[0m")
        httpd.shutdown()

