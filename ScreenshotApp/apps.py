from django.apps import AppConfig

class ScreenshotAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ScreenshotApp'  

    def ready(self):
        import ScreenshotApp.signals