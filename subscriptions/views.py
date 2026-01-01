import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Subscription
from .serializers import SubscriptionSerializer


logger = logging.getLogger(__name__)
User = get_user_model()

# --------------------------------------------------
# Africa's Talking SDK initialization (SAFE)
# --------------------------------------------------
try:
    import africastalking

    africastalking.initialize(
        username=settings.AFRICASTALKING_USERNAME,
        api_key=settings.AFRICASTALKING_API_KEY,
    )
    payment = africastalking.Payment
except Exception as e:
    logger.critical(f"Africa's Talking SDK init failed: {e}")
    payment = None


# ==================================================
# USSD HANDLER VIEW
# ==================================================
class UssdMenuHandlerView(APIView):
    """
    Handles incoming USSD requests from Africa's Talking
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        session_id = request.data.get("sessionId")
        phone_number = request.data.get("phoneNumber")
        text = request.data.get("text", "")

        logger.info(
            f"USSD INCOMING | session={session_id} phone={phone_number} text='{text}'"
        )

        if not phone_number:
            # Reject requests without a phone number
            response = "END An error occurred. Please try again."
            return Response(response, content_type="text/plain")

        # --- MODIFIED USER LOOKUP ---
        # This is a more robust and direct way to handle user creation.
        # It finds a user by their unique phone number.
        # If the user signed up via Flutter first, their phone number should have been saved.
        # If they use USSD first, an account is created with the phone number as the username.
        user, _ = User.objects.get_or_create(
            phone_number=phone_number,
            defaults={'username': f'user_{phone_number}'} # Creates a more unique default username
        )

        subscription, _ = Subscription.objects.get_or_create(user=user)

        # Main menu
        if text == "":
            response = (
                "CON Welcome to AfyaPlus\n"
                "1. Subscribe (1 Week)\n"
                "2. Check My Status"
            )

        # Subscribe
        elif text == "1":
            subscription.status = Subscription.Status.ACTIVE
            subscription.valid_until = timezone.now() + timedelta(days=7)
            subscription.save()
            response = "END Subscription successful. Your cover is now active."

        # Check status
        elif text == "2":
            # Refresh from DB to ensure status is current
            subscription.refresh_from_db()
            is_active = (
                subscription.status == Subscription.Status.ACTIVE
                and subscription.valid_until
                and subscription.valid_until > timezone.now()
            )

            if is_active:
                response = (
                    f"END Your AfyaPlus cover is ACTIVE until "
                    f"{subscription.valid_until:%d-%b-%Y}"
                )
            else:
                response = "END Your AfyaPlus cover is INACTIVE."

        else:
            response = "END Invalid selection."

        return Response(response, content_type="text/plain")


# ==================================================
# SUBSCRIPTION STATUS API (Flutter)
# ==================================================
class SubscriptionStatusView(APIView):
    """
    Returns subscription status for authenticated users
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # The user is authenticated via the token from the Flutter app.
        # We assume this user record has the correct phone_number set.
        user = request.user
        subscription, _ = Subscription.objects.get_or_create(user=user)

        # Auto-expire logic (this is good)
        if (
            subscription.status == Subscription.Status.ACTIVE
            and subscription.valid_until
            and subscription.valid_until < timezone.now()
        ):
            subscription.status = Subscription.Status.INACTIVE
            subscription.save()

        # The serializer correctly turns the subscription object into JSON.
        # This part of the code is perfect.
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)


# ==================================================
# FCM TOKEN SAVING API (Flutter) --- NEW CLASS
# ==================================================
class SaveFcmTokenView(APIView):
    """
    Saves or updates the FCM token for the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            # If no token is provided in the request body, return a client error
            return Response({'error': 'FCM token not provided'}, status=400)

        # Get the currently authenticated user from the request
        user = request.user
        
        # Save the provided token to the user's record
        user.fcm_token = token
        user.save(update_fields=['fcm_token'])
        
        # Return a success response to the Flutter app
        return Response({'status': 'FCM token saved successfully'}, status=200)
