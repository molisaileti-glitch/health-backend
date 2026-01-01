# api/authentication.py
import os
from rest_framework import authentication, exceptions
from firebase_admin import auth as firebase_auth
from django.conf import settings
import firebase_admin
from firebase_admin import credentials

# --- THIS IS THE CRITICAL CHANGE ---
# Instead of importing the old User model directly, we use get_user_model()
# This function dynamically retrieves the correct user model you defined in settings.py
from django.contrib.auth import get_user_model

# Get your active user model (which is subscriptions.CustomUser)
User = get_user_model()

# initialize firebase admin if not initialized
if not firebase_admin._apps:
    key_path = getattr(settings, "FIREBASE_CREDENTIAL_PATH", None)
    if key_path and os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    else:
        # This will prevent the app from crashing if the key is missing,
        # but authentication will fail.
        print("WARNING: Firebase credential file not found. Firebase auth will not work.")
        pass

class FirebaseAuthentication(authentication.BaseAuthentication):
    """
    Authenticate requests using Firebase ID tokens in the Authorization header:
    Authorization: Bearer <idToken>
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            # No token provided, so no authentication attempt is made.
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            # The header is malformed.
            raise exceptions.AuthenticationFailed("Invalid Authorization header format. Expected 'Bearer <token>'.")

        id_token = parts[1]

        # Check if the firebase app was initialized. If not, auth is impossible.
        if not firebase_admin._apps:
            raise exceptions.AuthenticationFailed("Firebase Admin SDK is not initialized. Check server configuration.")

        try:
            # Verify the token against the Firebase project.
            decoded = firebase_auth.verify_id_token(id_token)
        except Exception as e:
            # The token is invalid, expired, or doesn't match the project.
            raise exceptions.AuthenticationFailed(f"Invalid Firebase ID token: {e}")

        uid = decoded.get("uid")
        if not uid:
            # This should not happen with a valid token, but we check just in case.
            raise exceptions.AuthenticationFailed("Invalid token: uid missing from decoded token.")

        # Map Firebase uid -> Django CustomUser (username = uid)
        # This now correctly uses your CustomUser model.
        try:
            user, created = User.objects.get_or_create(username=uid)

            # Optional: If a new user was created, you can populate fields
            # from the Firebase token, like their email.
            if created:
                if decoded.get('email'):
                    user.email = decoded.get('email')
                    user.save()

            return (user, None)
        except Exception as e:
            # This would catch potential database errors.
            raise exceptions.APIException(f"Error retrieving or creating user in the database: {e}")
