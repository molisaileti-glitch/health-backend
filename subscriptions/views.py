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

        # Create or get user
        try:
            user, _ = User.objects.get_or_create(
                phone_number=phone_number,
                defaults={"username": phone_number},
            )
        except Exception:
            user, _ = User.objects.get_or_create(username=phone_number)

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
        subscription, _ = Subscription.objects.get_or_create(user=request.user)

        # Auto-expire
        if (
            subscription.status == Subscription.Status.ACTIVE
            and subscription.valid_until
            and subscription.valid_until < timezone.now()
        ):
            subscription.status = Subscription.Status.INACTIVE
            subscription.save()

        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
