from django.apps import AppConfig


class MissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mission'
    
    def ready(self):
        import mission.signals
