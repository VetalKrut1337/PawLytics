from django.apps import AppConfig

class PawlyticsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pawlytics'

    def ready(self):
        import pawlytics.signals