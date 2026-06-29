#!/usr/bin/env python3
"""
Interface graphique pour tester les lecteurs biométriques
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
from pathlib import Path
import sys

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from modules.fingerprint import USBFingerprintReader, SerialFingerprintReader, FingerprintMatcher
from modules.iris import IrisCamera, IrisSegmentation, IrisMatcher
from modules.database import BiometricDatabase


class BiometricGUI:
    """
    Interface graphique principale
    """
    
    def __init__(self, root):
        """
        Initialise l'interface
        
        Args:
            root: Fenêtre Tkinter
        """
        self.root = root
        self.root.title("🔐 Système Biométrique - Iris & Empreintes")
        self.root.geometry("900x700")
        
        # Variables
        self.db = None
        self.current_user = None
        
        # Composants biométriques
        self.fp_reader = None
        self.iris_camera = None
        
        # Créer l'interface
        self.create_widgets()
        
        # Initialiser la base de données
        self.init_database()
    
    def create_widgets(self):
        """Crée les widgets de l'interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Onglets
        self.create_home_tab()
        self.create_fingerprint_tab()
        self.create_iris_tab()
        self.create_database_tab()
        self.create_settings_tab()
    
    def create_home_tab(self):
        """Crée l'onglet d'accueil"""
        home_frame = ttk.Frame(self.notebook)
        self.notebook.add(home_frame, text="🏠 Accueil")
        
        # Titre
        title = tk.Label(home_frame, text="Système Biométrique", 
                        font=("Arial", 24, "bold"))
        title.pack(pady=20)
        
        subtitle = tk.Label(home_frame, text="Lecteur d'empreintes & Iris",
                           font=("Arial", 14))
        subtitle.pack()
        
        # Statistiques
        stats_frame = ttk.LabelFrame(home_frame, text="📊 Statistiques", padding=20)
        stats_frame.pack(pady=30, padx=20, fill='x')
        
        self.stats_label = tk.Label(stats_frame, text="Chargement...",
                                    font=("Arial", 12), justify='left')
        self.stats_label.pack()
        
        # Bouton de rafraîchissement
        refresh_btn = ttk.Button(stats_frame, text="🔄 Rafraîchir",
                                command=self.update_statistics)
        refresh_btn.pack(pady=10)
        
        # Actions rapides
        actions_frame = ttk.LabelFrame(home_frame, text="⚡ Actions rapides", padding=20)
        actions_frame.pack(pady=10, padx=20, fill='x')
        
        btn_frame = tk.Frame(actions_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="➕ Nouvel utilisateur",
                  command=self.quick_add_user).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="👆 Capturer empreinte",
                  command=self.quick_capture_fingerprint).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="👁️ Capturer iris",
                  command=self.quick_capture_iris).pack(side='left', padx=5)
    
    def create_fingerprint_tab(self):
        """Crée l'onglet empreintes"""
        fp_frame = ttk.Frame(self.notebook)
        self.notebook.add(fp_frame, text="👆 Empreintes")
        
        # Type de connexion
        conn_frame = ttk.LabelFrame(fp_frame, text="Type de connexion", padding=10)
        conn_frame.pack(pady=10, padx=10, fill='x')
        
        self.fp_conn_type = tk.StringVar(value="usb")
        
        ttk.Radiobutton(conn_frame, text="USB", variable=self.fp_conn_type,
                       value="usb").pack(side='left', padx=10)
        ttk.Radiobutton(conn_frame, text="Série", variable=self.fp_conn_type,
                       value="serial").pack(side='left', padx=10)
        
        # Actions
        actions_frame = ttk.LabelFrame(fp_frame, text="Actions", padding=10)
        actions_frame.pack(pady=10, padx=10, fill='x')
        
        btn_frame = tk.Frame(actions_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="🔌 Connecter",
                  command=self.connect_fingerprint).pack(side='left', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="📸 Capturer",
                  command=self.capture_fingerprint).pack(side='left', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="💾 Enregistrer",
                  command=self.enroll_fingerprint).pack(side='left', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="🔍 Vérifier",
                  command=self.verify_fingerprint).pack(side='left', padx=5, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(fp_frame, text="Journal", padding=10)
        log_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.fp_log = tk.Text(log_frame, height=15, wrap='word')
        self.fp_log.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.fp_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.fp_log.config(yscrollcommand=scrollbar.set)
    
    def create_iris_tab(self):
        """Crée l'onglet iris"""
        iris_frame = ttk.Frame(self.notebook)
        self.notebook.add(iris_frame, text="👁️ Iris")
        
        # Caméra
        cam_frame = ttk.LabelFrame(iris_frame, text="Caméra", padding=10)
        cam_frame.pack(pady=10, padx=10, fill='x')
        
        tk.Label(cam_frame, text="Index caméra:").pack(side='left', padx=5)
        
        self.iris_cam_index = tk.StringVar(value="0")
        cam_entry = ttk.Entry(cam_frame, textvariable=self.iris_cam_index, width=5)
        cam_entry.pack(side='left', padx=5)
        
        # Actions
        actions_frame = ttk.LabelFrame(iris_frame, text="Actions", padding=10)
        actions_frame.pack(pady=10, padx=10, fill='x')
        
        btn_frame = tk.Frame(actions_frame)
        btn_frame.pack()
        
        ttk.Button(btn_frame, text="📷 Ouvrir caméra",
                  command=self.open_camera).pack(side='left', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="👁️ Capturer iris",
                  command=self.capture_iris).pack(side='left', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="💾 Enregistrer",
                  command=self.enroll_iris).pack(side='left', padx=5, pady=5)
        
        ttk.Button(btn_frame, text="🔍 Vérifier",
                  command=self.verify_iris).pack(side='left', padx=5, pady=5)
        
        # Log
        log_frame = ttk.LabelFrame(iris_frame, text="Journal", padding=10)
        log_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        self.iris_log = tk.Text(log_frame, height=15, wrap='word')
        self.iris_log.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.iris_log.yview)
        scrollbar.pack(side='right', fill='y')
        self.iris_log.config(yscrollcommand=scrollbar.set)
    
    def create_database_tab(self):
        """Crée l'onglet base de données"""
        db_frame = ttk.Frame(self.notebook)
        self.notebook.add(db_frame, text="💾 Base de données")
        
        # Liste des utilisateurs
        users_frame = ttk.LabelFrame(db_frame, text="Utilisateurs", padding=10)
        users_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Treeview
        columns = ('ID', 'Nom', 'Empreintes', 'Iris')
        self.users_tree = ttk.Treeview(users_frame, columns=columns, show='headings')
        
        for col in columns:
            self.users_tree.heading(col, text=col)
            self.users_tree.column(col, width=100)
        
        self.users_tree.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(users_frame, orient='vertical',
                                 command=self.users_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.users_tree.config(yscrollcommand=scrollbar.set)
        
        # Boutons
        btn_frame = tk.Frame(db_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="➕ Ajouter utilisateur",
                  command=self.add_user_dialog).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🗑️ Supprimer",
                  command=self.delete_user).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Rafraîchir",
                  command=self.refresh_users_list).pack(side='left', padx=5)
    
    def create_settings_tab(self):
        """Crée l'onglet paramètres"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Paramètres")
        
        # Configuration
        config_frame = ttk.LabelFrame(settings_frame, text="Configuration", padding=20)
        config_frame.pack(pady=10, padx=10, fill='both', expand=True)
        
        # Charger config
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
        except:
            config = {}
        
        self.config_text = tk.Text(config_frame, height=20, wrap='word')
        self.config_text.pack(fill='both', expand=True)
        self.config_text.insert('1.0', json.dumps(config, indent=2))
        
        # Boutons
        btn_frame = tk.Frame(settings_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="💾 Sauvegarder",
                  command=self.save_config).pack(side='left', padx=5)
        
        ttk.Button(btn_frame, text="🔄 Recharger",
                  command=self.reload_config).pack(side='left', padx=5)
    
    # Méthodes fonctionnelles
    
    def init_database(self):
        """Initialise la base de données"""
        try:
            self.db = BiometricDatabase()
            self.db.connect()
            self.update_statistics()
            self.refresh_users_list()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur base de données: {e}")
    
    def update_statistics(self):
        """Met à jour les statistiques"""
        if self.db:
            stats = self.db.get_statistics()
            text = f"👥 Utilisateurs: {stats['users']}\n"
            text += f"👆 Empreintes: {stats['fingerprints']}\n"
            text += f"👁️ Iris: {stats['iris']}"
            self.stats_label.config(text=text)
    
    def log_fp(self, message):
        """Ajoute un message au log empreintes"""
        self.fp_log.insert('end', message + '\n')
        self.fp_log.see('end')
    
    def log_iris(self, message):
        """Ajoute un message au log iris"""
        self.iris_log.insert('end', message + '\n')
        self.iris_log.see('end')
    
    def connect_fingerprint(self):
        """Connecte au lecteur d'empreintes"""
        conn_type = self.fp_conn_type.get()
        
        try:
            if conn_type == "usb":
                self.log_fp("Connexion USB...")
                self.fp_reader = USBFingerprintReader()
                if self.fp_reader.connect():
                    self.log_fp("✓ Connecté!")
                else:
                    self.log_fp("❌ Échec connexion")
            else:
                self.log_fp("Connexion série...")
                self.fp_reader = SerialFingerprintReader()
                if self.fp_reader.connect():
                    self.log_fp("✓ Connecté!")
                else:
                    self.log_fp("❌ Échec connexion")
        except Exception as e:
            self.log_fp(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    def capture_fingerprint(self):
        """Capture une empreinte"""
        self.log_fp("Fonctionnalité de capture à implémenter selon votre lecteur")
        messagebox.showinfo("Info", "Consultez la documentation pour adapter à votre matériel")
    
    def enroll_fingerprint(self):
        """Enregistre une empreinte"""
        self.log_fp("Enregistrement empreinte...")
        messagebox.showinfo("Info", "Sélectionnez d'abord un utilisateur dans l'onglet Base de données")
    
    def verify_fingerprint(self):
        """Vérifie une empreinte"""
        self.log_fp("Vérification empreinte...")
        messagebox.showinfo("Info", "Fonctionnalité à implémenter")
    
    def open_camera(self):
        """Ouvre la caméra iris"""
        try:
            cam_index = int(self.iris_cam_index.get())
            self.log_iris(f"Ouverture caméra #{cam_index}...")
            
            self.iris_camera = IrisCamera(camera_index=cam_index)
            if self.iris_camera.connect():
                self.log_iris("✓ Caméra ouverte!")
            else:
                self.log_iris("❌ Échec ouverture")
        except Exception as e:
            self.log_iris(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    def capture_iris(self):
        """Capture un iris"""
        if not self.iris_camera or not self.iris_camera.connected:
            messagebox.showwarning("Attention", "Ouvrez d'abord la caméra")
            return
        
        self.log_iris("Capture iris en cours...")
        
        def capture_thread():
            try:
                capture = self.iris_camera.capture_iris(timeout=30, preview=True)
                if capture:
                    self.log_iris("✓ Iris capturé!")
                else:
                    self.log_iris("❌ Capture annulée ou échouée")
            except Exception as e:
                self.log_iris(f"❌ Erreur: {e}")
        
        threading.Thread(target=capture_thread, daemon=True).start()
    
    def enroll_iris(self):
        """Enregistre un iris"""
        self.log_iris("Enregistrement iris...")
        messagebox.showinfo("Info", "Sélectionnez d'abord un utilisateur")
    
    def verify_iris(self):
        """Vérifie un iris"""
        self.log_iris("Vérification iris...")
        messagebox.showinfo("Info", "Fonctionnalité à implémenter")
    
    def add_user_dialog(self):
        """Dialogue pour ajouter un utilisateur"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nouvel utilisateur")
        dialog.geometry("300x150")
        
        tk.Label(dialog, text="Nom:").pack(pady=10)
        
        name_var = tk.StringVar()
        entry = ttk.Entry(dialog, textvariable=name_var, width=30)
        entry.pack(pady=5)
        entry.focus()
        
        def add():
            name = name_var.get().strip()
            if name:
                try:
                    self.db.add_user(name)
                    self.refresh_users_list()
                    self.update_statistics()
                    dialog.destroy()
                    messagebox.showinfo("Succès", f"Utilisateur '{name}' créé!")
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))
        
        ttk.Button(dialog, text="Ajouter", command=add).pack(pady=10)
    
    def delete_user(self):
        """Supprime l'utilisateur sélectionné"""
        selection = self.users_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez un utilisateur")
            return
        
        item = self.users_tree.item(selection[0])
        user_id = item['values'][0]
        user_name = item['values'][1]
        
        if messagebox.askyesno("Confirmation",
                              f"Supprimer l'utilisateur '{user_name}' et toutes ses données?"):
            try:
                self.db.delete_user(user_id)
                self.refresh_users_list()
                self.update_statistics()
                messagebox.showinfo("Succès", "Utilisateur supprimé")
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
    
    def refresh_users_list(self):
        """Rafraîchit la liste des utilisateurs"""
        # Vider l'arbre
        for item in self.users_tree.get_children():
            self.users_tree.delete(item)
        
        # Charger les utilisateurs
        if self.db:
            users = self.db.list_users()
            
            for user in users:
                # Compter les données biométriques
                fps = len(self.db.get_fingerprints(user['id']))
                iris = len(self.db.get_iris(user['id']))
                
                self.users_tree.insert('', 'end', values=(
                    user['id'],
                    user['name'],
                    fps,
                    iris
                ))
    
    def save_config(self):
        """Sauvegarde la configuration"""
        try:
            config_text = self.config_text.get('1.0', 'end')
            config = json.loads(config_text)
            
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Succès", "Configuration sauvegardée")
        except json.JSONDecodeError as e:
            messagebox.showerror("Erreur", f"JSON invalide: {e}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def reload_config(self):
        """Recharge la configuration"""
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            
            self.config_text.delete('1.0', 'end')
            self.config_text.insert('1.0', json.dumps(config, indent=2))
            
            messagebox.showinfo("Succès", "Configuration rechargée")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def quick_add_user(self):
        """Action rapide: ajouter utilisateur"""
        self.notebook.select(3)  # Onglet base de données
        self.add_user_dialog()
    
    def quick_capture_fingerprint(self):
        """Action rapide: capturer empreinte"""
        self.notebook.select(1)  # Onglet empreintes
        self.capture_fingerprint()
    
    def quick_capture_iris(self):
        """Action rapide: capturer iris"""
        self.notebook.select(2)  # Onglet iris
        self.capture_iris()


def main():
    """Point d'entrée principal"""
    root = tk.Tk()
    app = BiometricGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

