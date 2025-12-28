# subscriptions/views.py

import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Subscription
from .serializers import SubscriptionSerializer # Make sure this import is present

# Get the User model you are using in your project
User = get_user_model()
logger = logging.getLogger(__name__)

class UssdMenuHandlerView(APIView):
    """
    This view handles all incoming USSD session requests from Africa's Talking.
    """
    # This MUST be public so Africa's Talking servers can reach it.
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Read the variables from the Africa's Talking POST request
        session_id = request.data.get("sessionId")
        phone_number = request.data.get("phoneNumber")
        text = request.data.get("text")

        logger.info(
            f"INCOMING USSD: SID={session_id}, Phone={phone_number}, Text='{text}'"
        )

        # Find or create a user account tied to this phone number.
        # This is a critical step. We assume the phone number is the username.
        user, _ = User.objects.get_or_create(username=phone_number)

        # Get the subscription object for this user.
        subscription, _ = Subscription.objects.get_or_create(user=user)

        # --- USSD MENU LOGIC ---
        response = ""

        if text == "":
            # This is the FIRST request. Show the main menu.
            response = "CON Welcome to AfyaPlus!\n"
            response += "1. Subscribe (1 Week)\n"
            response += "2. Check My Status"

        elif text == "1":
            # User wants to subscribe.
            # Here, we will end the session and rely on Africa's Talking
            # to handle the payment collection and send us a notification.
            # This is a placeholder for the C2B (Customer to Business) checkout.
            # For now, we simulate a successful payment for testing.

            # --- SIMULATION LOGIC ---
            subscription.status = Subscription.Status.ACTIVE
            subscription.valid_until = timezone.now() + timedelta(days=7)
            subscription.save()
            # --- END SIMULATION ---

            response = f"END Thank you for subscribing. Your AfyaPlus cover is now active."

        elif text == "2":
            # User wants to check their subscription status.
            is_active = (
                subscription.status == Subscription.Status.ACTIVE and
                subscription.valid_until is not None and
                subscription.valid_until > timezone.now()
            )

            if is_active:
                # Format the date for display, e.g., "25-Dec-2025"
                expiry_date = subscription.valid_until.strftime('%d-%b-%Y')
                response = f"END Your AfyaPlus cover is ACTIVE until {expiry_date}."
            else:
                response = "END Your AfyaPlus cover is INACTIVE. Please use option 1 to subscribe."

        else:
            # The user entered an invalid option.
            response = "END Invalid selection. Please try again."

        # The final response must be plain text.
        return Response(response, content_type="text/plain")
    
    class SubscriptionStatusView(APIView):
        """
        Endpoint for the Flutter app to get the user's current subscription status.
        """
        permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        subscription, created = Subscription.objects.get_or_create(user=request.user)

        # Automatically check if an active subscription has expired
        if subscription.status == Subscription.Status.ACTIVE and (subscription.valid_until is None or subscription.valid_until < timezone.now()):
            subscription.status = Subscription.Status.INACTIVE
            subscription.save()

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

