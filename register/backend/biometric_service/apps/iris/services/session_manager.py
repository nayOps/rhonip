"""
Gestionnaire global de sessions de capture d'iris
Permet de partager les instances de service et de caméra entre les requêtes
"""

import logging
from threading import Lock
from .capture import IrisCaptureService

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Singleton pour gérer les sessions de capture actives
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._sessions = {}  # {session_id: IrisCaptureService}
        self._sessions_lock = Lock()
        self._initialized = True
        
        logger.info("SessionManager initialisé")
    
    def get_or_create_service(self, session_id):
        """
        Récupère ou crée un service de capture pour une session
        
        Args:
            session_id: ID de la session
            
        Returns:
            IrisCaptureService: Service de capture
        """
        with self._sessions_lock:
            if session_id not in self._sessions:
                logger.info(f"Création d'un nouveau service pour session {session_id}")
                self._sessions[session_id] = IrisCaptureService()
            
            return self._sessions[session_id]
    
    def release_service(self, session_id):
        """
        Libère le service de capture pour une session
        
        Args:
            session_id: ID de la session
        """
        with self._sessions_lock:
            if session_id in self._sessions:
                service = self._sessions[session_id]
                
                # Fermer la caméra si elle est ouverte
                if service.camera and service.camera.connected:
                    service.camera.disconnect()
                
                del self._sessions[session_id]
                logger.info(f"Service libéré pour session {session_id}")
    
    def get_active_sessions(self):
        """
        Récupère la liste des sessions actives
        
        Returns:
            list: Liste des IDs de sessions actives
        """
        with self._sessions_lock:
            return list(self._sessions.keys())
    
    def cleanup_all(self):
        """
        Nettoie toutes les sessions actives
        """
        with self._sessions_lock:
            for session_id in list(self._sessions.keys()):
                self.release_service(session_id)
            
            logger.info("Toutes les sessions ont été nettoyées")


# Instance globale
session_manager = SessionManager()

