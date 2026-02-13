from django.apps import AppConfig


class TourismConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tourism'

def ready(self):
    import tourism.signals  # replace `tourism` with your app name
