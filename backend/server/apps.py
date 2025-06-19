from django.apps import AppConfig

class PawlyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'server'

    def ready(self):
        import server.signals