# subscriptions/views.py

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

# ... (UssdMenuHandlerView and Africa's Talking code remain unchanged) ...
# Omitted for brevity, paste this class to replace your existing one.


# ==================================================
# USSD HANDLER VIEW (This remains the same)
# ==================================================
class UssdMenuHandlerView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        # ... your existing USSD logic ...
        session_id = request.data.get("sessionId")
        phone_number = request.data.get("phoneNumber")
        text = request.data.get("text", "")
        logger.info(f"USSD INCOMING | session={session_id} phone={phone_number} text='{text}'")
        if not phone_number:
            response = "END An error occurred. Please try again."
            return Response(response, content_type="text/plain")
        user, _ = User.objects.get_or_create(phone_number=phone_number, defaults={'username': f'user_{phone_number}'})
        subscription, _ = Subscription.objects.get_or_create(user=user)
        if text == "":
            response = ("CON Welcome to AfyaPlus\n""1. Subscribe (1 Week)\n""2. Check My Status")
        elif text == "1":
            subscription.status = Subscription.Status.ACTIVE
            subscription.valid_until = timezone.now() + timedelta(days=7)
            subscription.save()
            response = "END Subscription successful. Your cover is now active."
        elif text == "2":
            subscription.refresh_from_db()
            is_active = (subscription.status == Subscription.Status.ACTIVE and subscription.valid_until and subscription.valid_until > timezone.now())
            if is_active:
                response = (f"END Your AfyaPlus cover is ACTIVE until {subscription.valid_until:%d-%b-%Y}")
            else:
                response = "END Your AfyaPlus cover is INACTIVE."
        else:
            response = "END Invalid selection."
        return Response(response, content_type="text/plain")


# ==================================================
# SUBSCRIPTION STATUS API (Flutter) - MODIFIED
# ==================================================
class SubscriptionStatusView(APIView):
    """
    Returns subscription status for authenticated users
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Use a try-except block for maximum safety
        try:
            # The user is authenticated. Let's get or create their subscription.
            # This ensures that even a brand new user has a subscription object.
            subscription, created = Subscription.objects.get_or_create(user=request.user)

            # Auto-expire logic (this is good, but let's check for valid_until)
            if (
                subscription.status == Subscription.Status.ACTIVE
                and subscription.valid_until
                and subscription.valid_until < timezone.now()
            ):
                subscription.status = Subscription.Status.INACTIVE
                subscription.save()

            # The serializer correctly turns the subscription object into JSON.
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        
        except Exception as e:
            # If anything at all goes wrong, log it and return a server error.
            logger.error(f"Error in SubscriptionStatusView for user {request.user.username}: {e}")
            return Response({"error": "An error occurred while fetching subscription status."}, status=500)


# ==================================================
# FCM TOKEN SAVING API (Flutter) (This remains the same)
# ==================================================
class SaveFcmTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'FCM token not provided'}, status=400)
        user = request.user
        user.fcm_token = token
        user.save(update_fields=['fcm_token'])
        return Response({'status': 'FCM token saved successfully'}, status=200)

