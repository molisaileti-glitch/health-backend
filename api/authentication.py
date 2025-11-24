# api/authentication.py
import os
from rest_framework import authentication, exceptions
from firebase_admin import auth as firebase_auth
from django.contrib.auth.models import User
from django.conf import settings
import firebase_admin
from firebase_admin import credentials

# initialize firebase admin if not initialized
if not firebase_admin._apps:
    key_path = getattr(settings, "FIREBASE_CREDENTIAL_PATH", None)
    if key_path and os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    else:
        # in dev you can skip init and only use admin if key present
        pass

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using Firebase ID tokens in the Authorization header:
    Authorization: Bearer <idToken>
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            raise exceptions.AuthenticationFailed("Invalid Authorization header format.")

        id_token = parts[1]

        try:
            decoded = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            raise exceptions.AuthenticationFailed(f"Invalid Firebase ID token: {e}")

        uid = decoded.get("uid")
        if not uid:
            raise exceptions.AuthenticationFailed("Invalid token: uid missing")

        # Map Firebase uid -> Django User (username = uid)
        user, _ = User.objects.get_or_create(username=uid)
        return (user, None)
