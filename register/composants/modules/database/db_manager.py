"""
Gestionnaire de base de données pour les templates biométriques
Stockage SQLite des empreintes et iris
"""

import sqlite3
import json
import pickle
import time
from pathlib import Path
import numpy as np


class BiometricDatabase:
    """
    Classe pour gérer la base de données biométrique
    """
    
    def __init__(self, db_path='biometric_data.db'):
        """
        Initialise la base de données
        
        Args:
            db_path: Chemin vers le fichier de base de données
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connecte à la base de données"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        print(f"✓ Connecté à la base de données: {self.db_path}")
    
    def disconnect(self):
        """Déconnecte de la base de données"""
        if self.conn:
            self.conn.close()
        print("✓ Déconnecté de la base de données")
    
    def _create_tables(self):
        """Crée les tables si elles n'existent pas"""
        # Table pour les utilisateurs
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        ''')
        
        # Table pour les empreintes
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS fingerprints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                finger_index INTEGER,
                template_data BLOB NOT NULL,
                quality_score REAL,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Table pour les iris
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS iris (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                eye TEXT CHECK(eye IN ('left', 'right', 'unknown')),
                template_data BLOB NOT NULL,
                quality_score REAL,
                created_at REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.conn.commit()
    
    def add_user(self, name):
        """
        Ajoute un nouvel utilisateur
        
        Args:
            name: Nom de l'utilisateur
            
        Returns:
            int: ID de l'utilisateur créé
        """
        timestamp = time.time()
        
        self.cursor.execute('''
            INSERT INTO users (name, created_at, updated_at)
            VALUES (?, ?, ?)
        ''', (name, timestamp, timestamp))
        
        self.conn.commit()
        user_id = self.cursor.lastrowid
        
        print(f"✓ Utilisateur créé: {name} (ID: {user_id})")
        return user_id
    
    def get_user(self, user_id):
        """
        Récupère un utilisateur par ID
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            dict: Informations de l'utilisateur ou None
        """
        self.cursor.execute('''
            SELECT id, name, created_at, updated_at
            FROM users
            WHERE id = ?
        ''', (user_id,))
        
        row = self.cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'updated_at': row[3]
            }
        
        return None
    
    def get_user_by_name(self, name):
        """
        Récupère un utilisateur par nom
        
        Args:
            name: Nom de l'utilisateur
            
        Returns:
            dict: Informations de l'utilisateur ou None
        """
        self.cursor.execute('''
            SELECT id, name, created_at, updated_at
            FROM users
            WHERE name = ?
        ''', (name,))
        
        row = self.cursor.fetchone()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'updated_at': row[3]
            }
        
        return None
    
    def list_users(self):
        """
        Liste tous les utilisateurs
        
        Returns:
            list: Liste des utilisateurs
        """
        self.cursor.execute('''
            SELECT id, name, created_at, updated_at
            FROM users
            ORDER BY name
        ''')
        
        users = []
        for row in self.cursor.fetchall():
            users.append({
                'id': row[0],
                'name': row[1],
                'created_at': row[2],
                'updated_at': row[3]
            })
        
        return users
    
    def add_fingerprint(self, user_id, template, finger_index=None, quality_score=None):
        """
        Ajoute une empreinte pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            template: Template d'empreinte (dict)
            finger_index: Index du doigt (0-9, optionnel)
            quality_score: Score de qualité (0-100, optionnel)
            
        Returns:
            int: ID de l'empreinte créée
        """
        # Sérialiser le template
        template_blob = pickle.dumps(template)
        
        timestamp = time.time()
        
        self.cursor.execute('''
            INSERT INTO fingerprints (user_id, finger_index, template_data, quality_score, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, finger_index, template_blob, quality_score, timestamp))
        
        self.conn.commit()
        fp_id = self.cursor.lastrowid
        
        print(f"✓ Empreinte ajoutée (ID: {fp_id})")
        return fp_id
    
    def get_fingerprints(self, user_id):
        """
        Récupère toutes les empreintes d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            list: Liste des empreintes
        """
        self.cursor.execute('''
            SELECT id, finger_index, template_data, quality_score, created_at
            FROM fingerprints
            WHERE user_id = ?
        ''', (user_id,))
        
        fingerprints = []
        for row in self.cursor.fetchall():
            template = pickle.loads(row[2])
            
            fingerprints.append({
                'id': row[0],
                'finger_index': row[1],
                'template': template,
                'quality_score': row[3],
                'created_at': row[4]
            })
        
        return fingerprints
    
    def get_all_fingerprints(self):
        """
        Récupère toutes les empreintes de la base
        
        Returns:
            list: Liste de tuples (user_id, fingerprint_data)
        """
        self.cursor.execute('''
            SELECT user_id, id, finger_index, template_data, quality_score, created_at
            FROM fingerprints
        ''')
        
        fingerprints = []
        for row in self.cursor.fetchall():
            template = pickle.loads(row[3])
            
            fingerprints.append({
                'user_id': row[0],
                'id': row[1],
                'finger_index': row[2],
                'template': template,
                'quality_score': row[4],
                'created_at': row[5]
            })
        
        return fingerprints
    
    def add_iris(self, user_id, template, eye='unknown', quality_score=None):
        """
        Ajoute un iris pour un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            template: Template d'iris (dict)
            eye: 'left', 'right', ou 'unknown'
            quality_score: Score de qualité (0-1, optionnel)
            
        Returns:
            int: ID de l'iris créé
        """
        # Sérialiser le template
        template_blob = pickle.dumps(template)
        
        timestamp = time.time()
        
        self.cursor.execute('''
            INSERT INTO iris (user_id, eye, template_data, quality_score, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, eye, template_blob, quality_score, timestamp))
        
        self.conn.commit()
        iris_id = self.cursor.lastrowid
        
        print(f"✓ Iris ajouté (ID: {iris_id})")
        return iris_id
    
    def get_iris(self, user_id):
        """
        Récupère tous les iris d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            list: Liste des iris
        """
        self.cursor.execute('''
            SELECT id, eye, template_data, quality_score, created_at
            FROM iris
            WHERE user_id = ?
        ''', (user_id,))
        
        iris_list = []
        for row in self.cursor.fetchall():
            template = pickle.loads(row[2])
            
            iris_list.append({
                'id': row[0],
                'eye': row[1],
                'template': template,
                'quality_score': row[3],
                'created_at': row[4]
            })
        
        return iris_list
    
    def get_all_iris(self):
        """
        Récupère tous les iris de la base
        
        Returns:
            list: Liste de tuples (user_id, iris_data)
        """
        self.cursor.execute('''
            SELECT user_id, id, eye, template_data, quality_score, created_at
            FROM iris
        ''')
        
        iris_list = []
        for row in self.cursor.fetchall():
            template = pickle.loads(row[3])
            
            iris_list.append({
                'user_id': row[0],
                'id': row[1],
                'eye': row[2],
                'template': template,
                'quality_score': row[4],
                'created_at': row[5]
            })
        
        return iris_list
    
    def delete_user(self, user_id):
        """
        Supprime un utilisateur et toutes ses données biométriques
        
        Args:
            user_id: ID de l'utilisateur
        """
        # Supprimer les empreintes
        self.cursor.execute('DELETE FROM fingerprints WHERE user_id = ?', (user_id,))
        
        # Supprimer les iris
        self.cursor.execute('DELETE FROM iris WHERE user_id = ?', (user_id,))
        
        # Supprimer l'utilisateur
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        
        self.conn.commit()
        print(f"✓ Utilisateur {user_id} supprimé")
    
    def get_statistics(self):
        """
        Récupère les statistiques de la base
        
        Returns:
            dict: Statistiques
        """
        # Nombre d'utilisateurs
        self.cursor.execute('SELECT COUNT(*) FROM users')
        num_users = self.cursor.fetchone()[0]
        
        # Nombre d'empreintes
        self.cursor.execute('SELECT COUNT(*) FROM fingerprints')
        num_fingerprints = self.cursor.fetchone()[0]
        
        # Nombre d'iris
        self.cursor.execute('SELECT COUNT(*) FROM iris')
        num_iris = self.cursor.fetchone()[0]
        
        return {
            'users': num_users,
            'fingerprints': num_fingerprints,
            'iris': num_iris
        }
    
    def __enter__(self):
        """Support pour context manager"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage automatique"""
        self.disconnect()

