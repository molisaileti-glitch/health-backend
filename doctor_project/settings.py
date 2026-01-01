# doctor_project/settings.py
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "change-this-secret-in-prod")
DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # third party
    "rest_framework",
    "corsheaders",

    # local
    "api",
    "subscriptions", # <-- 1. ADD THIS LINE
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Note: 'XFrameOptionsMiddleware' is often here by default and is good practice.
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "doctor_project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": ["django.template.context_processors.debug", "django.template.context_processors.request", "django.contrib.auth.context_processors.auth", "django.contrib.messages.context_processors.messages"],},
    },
]

WSGI_APPLICATION = "doctor_project.wsgi.application"
# ASGI_APPLICATION is not used by default, but leaving it is fine.
# ASGI_APPLICATION = "doctor_project.asgi.application" 

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = []
AUTH_USER_MODEL = 'subscriptions.CustomUser'

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField' # Recommended for new apps

# CORS — allow your app origins (in prod restrict!)
CORS_ALLOW_ALL_ORIGINS = True

# REST Framework: use your Firebase auth
# IMPORTANT: Since you have a public webhook, we must adjust this slightly
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "api.authentication.FirebaseAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}

# Firebase Admin initialization: expects firebase_key.json in project root
FIREBASE_CREDENTIAL_PATH = os.path.join(BASE_DIR, "serviceAccountKey.json")


# --- 2. ADD THIS NEW SECTION FOR AFYA PLUS AND AFRICA'S TALKING ---
# ---------------------------------------------------------------------
# AFYA PLUS SUBSCRIPTION SETTINGS
# ---------------------------------------------------------------------
# NOTE: Use environment variables for these in production!
AFRICASTALKING_USERNAME = os.environ.get("AFRICASTALKING_USERNAME", "sandbox") # Use 'sandbox' for testing
AFRICASTALKING_API_KEY = os.environ.get("AFRICASTALKING_API_KEY", "atsk_ecd9d3e9863677c557b1bb0762ed79977ea59be738d79d711c09db55f1a16ccf38a2465f")
AFRICASTALKING_PRODUCT_NAME = "AfyaPlus" # The product name you create in your AT account
AFRICASTALKING_CURRENCY_CODE = "TZS"

AFYA_PLUS_ACTIVATION_FEE = 1000.0
AFYA_PLUS_WEEKLY_FEE = 350.0
AFYA_PLUS_GRACE_PERIOD_DAYS = 3 # The number of failed attempts before pausing
# ---------------------------------------------------------------------
