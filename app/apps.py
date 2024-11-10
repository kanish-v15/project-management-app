"""apps.py"""

from django.apps import AppConfig

class AppConfig(AppConfig):
    """Appconfig Class"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
