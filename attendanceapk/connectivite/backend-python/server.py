#!/usr/bin/env python3
"""
Serveur Python simple pour tester la connectivité
Endpoint: /api/test
Méthode: POST
Port: 8082
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime

app = Flask(__name__)
CORS(app)  # Permettre les requêtes cross-origin

# Stockage en mémoire des données reçues
received_data = []
attendance_data = []  # Stockage des présences

@app.route('/', methods=['GET'])
def index():
    """Page d'accueil"""
    return f"""
    <html>
    <head>
        <title>Serveur de Test de Connectivité</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{ color: #333; }}
            .endpoint {{
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-left: 4px solid #007bff;
                border-radius: 4px;
            }}
            .method {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: bold;
                margin-right: 10px;
            }}
            .get {{ background: #28a745; color: white; }}
            .post {{ background: #007bff; color: white; }}
            a {{
                color: #007bff;
                text-decoration: none;
            }}
            a:hover {{ text-decoration: underline; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Serveur de Test de Connectivité</h1>
            <p>Serveur Python Flask actif sur le port <strong>8082</strong></p>
            
            <h2>📡 Endpoints disponibles :</h2>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/api/test">/api/test</a>
                <p>Vérifier que le serveur répond</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/test</strong>
                <p>Recevoir des données de l'APK</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/api/data">/api/data</a>
                <p>Voir toutes les données reçues (Total: {len(received_data)})</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/clear</strong>
                <p>Effacer les données stockées</p>
            </div>
            
            <div class="endpoint">
                <span class="method get">GET</span>
                <a href="/api/attendance">/api/attendance</a>
                <p>Voir toutes les présences (Total: {len(attendance_data)})</p>
            </div>
            
            <div class="endpoint">
                <span class="method post">POST</span>
                <strong>/api/attendance</strong>
                <p>Enregistrer une présence</p>
            </div>
            
            <hr style="margin: 30px 0;">
            <p><small>Timestamp: {datetime.datetime.now().isoformat()}</small></p>
        </div>
    </body>
    </html>
    """

@app.route('/api/test', methods=['GET'])
def test_get():
    """Test GET - Vérifier que le serveur répond"""
    return jsonify({
        "status": "success",
        "message": "Serveur Python actif",
        "timestamp": datetime.datetime.now().isoformat(),
        "total_received": len(received_data)
    })

@app.route('/api/test', methods=['POST'])
def test_post():
    """Test POST - Recevoir des données de l'APK"""
    try:
        # Récupérer les données JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Aucune donnée JSON reçue"
            }), 400
        
        # Ajouter un timestamp
        data['received_at'] = datetime.datetime.now().isoformat()
        data['id'] = len(received_data) + 1
        
        # Stocker les données
        received_data.append(data)
        
        print(f"📱 Données reçues de l'APK:")
        print(f"   ID: {data['id']}")
        print(f"   Nom: {data.get('firstName', 'N/A')} {data.get('lastName', 'N/A')}")
        print(f"   Email: {data.get('email', 'N/A')}")
        print(f"   Timestamp: {data['received_at']}")
        print("=" * 50)
        
        return jsonify({
            "status": "success",
            "message": "Données reçues avec succès",
            "id": data['id'],
            "received_at": data['received_at'],
            "total_received": len(received_data)
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur lors de la réception des données: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Récupérer toutes les données reçues"""
    return jsonify({
        "status": "success",
        "total": len(received_data),
        "data": received_data
    })

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Vider les données stockées"""
    global received_data
    received_data = []
    return jsonify({
        "status": "success",
        "message": "Données effacées"
    })

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Récupérer toutes les présences"""
    return jsonify({
        "status": "success",
        "total": len(attendance_data),
        "data": attendance_data
    })

@app.route('/api/attendance', methods=['POST'])
def record_attendance():
    """Enregistrer une présence"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Aucune donnée JSON reçue"
            }), 400
        
        # Ajouter un ID et timestamp
        attendance_record = {
            "id": len(attendance_data) + 1,
            "employeeId": data.get("employeeId"),
            "date": data.get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
            "time": data.get("time", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "type": data.get("type", "checkin"),
            "fingerprintUsed": data.get("fingerprintUsed", "fingerprint_capture"),
            "status": data.get("status", "present"),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        attendance_data.append(attendance_record)
        
        print(f"📅 Présence enregistrée:")
        print(f"   ID: {attendance_record['id']}")
        print(f"   Employé ID: {attendance_record['employeeId']}")
        print(f"   Type: {attendance_record['type']}")
        print(f"   Date: {attendance_record['date']} {attendance_record['time']}")
        print("=" * 50)
        
        return jsonify({
            "status": "success",
            "message": "Présence enregistrée avec succès",
            "data": attendance_record
        }), 200
        
    except Exception as e:
        print(f"❌ Erreur lors de l'enregistrement de la présence: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Erreur serveur: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("🚀 Démarrage du serveur de test de connectivité")
    print("📡 Endpoint: http://0.0.0.0:8082/api/test")
    print("🔍 GET: Vérifier la connectivité")
    print("📱 POST: Recevoir des données de l'APK")
    print("📊 GET /api/data: Voir toutes les données")
    print("🗑️ POST /api/clear: Effacer les données")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8082, debug=True)
