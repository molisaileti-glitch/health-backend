# api/apps.py
try:
    from django.apps import AppConfig
except Exception:
    # Fallback minimal AppConfig for environments where Django is not installed
    class AppConfig:
        pass

class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
