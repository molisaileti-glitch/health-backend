# subscriptions/views.py

import logging
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from .models import Subscription
from .serializers import SubscriptionSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


# ==================================================
# USSD HANDLER VIEW
# ==================================================
class UssdMenuHandlerView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        session_id = request.data.get("sessionId")
        phone_number = request.data.get("phoneNumber")
        text = request.data.get("text", "")

        logger.info(f"USSD | session={session_id} phone={phone_number} text={text}")

        if not phone_number:
            return Response("END An error occurred.", content_type="text/plain")

        user, _ = User.objects.get_or_create(
            username=f"user_{phone_number}"
        )

        subscription, _ = Subscription.objects.get_or_create(
            user=user,
            defaults={"phone_number": phone_number}
        )

        if text == "":
            response = (
                "CON Welcome to AfyaPlus\n"
                "1. Subscribe (1 Week)\n"
                "2. Check My Status"
            )

        elif text == "1":
            subscription.status = Subscription.Status.ACTIVE
            subscription.start_date = timezone.now()
            subscription.valid_until = timezone.now() + timedelta(days=7)
            subscription.save()

            response = "END Subscription successful. Cover active for 7 days."

        elif text == "2":
            if (
                subscription.status == Subscription.Status.ACTIVE
                and subscription.valid_until
                and subscription.valid_until > timezone.now()
            ):
                response = f"END ACTIVE until {subscription.valid_until:%d-%b-%Y}"
            else:
                response = "END INACTIVE."

        else:
            response = "END Invalid option."

        return Response(response, content_type="text/plain")


# ==================================================
# SUBSCRIPTION STATUS (Flutter)
# ==================================================
class SubscriptionStatusView(APIView):
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


# ==================================================
# SAVE FCM TOKEN (Flutter)
# ==================================================
class SaveFcmTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = request.data.get("token")

        if not token:
            return Response({"error": "Token required"}, status=400)

        subscription, _ = Subscription.objects.get_or_create(user=request.user)
        subscription.fcm_token = token
        subscription.save(update_fields=["fcm_token"])

        return Response({"status": "FCM token saved"})
