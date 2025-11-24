# api/views.py
import json
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings

from .models import DoctorRequest, Offer, FCMToken
from .serializers import DoctorRequestSerializer, OfferSerializer

# firebase admin messaging (preferred)
import firebase_admin
from firebase_admin import messaging, credentials

# ensure firebase admin initialized
if not firebase_admin._apps:
    key_path = getattr(settings, "FIREBASE_CREDENTIAL_PATH", None)
    if key_path and os.path.exists(key_path):
        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)

def send_push_to_token(token: str, title: str, body: str, data: dict = None):
    """
    Use firebase_admin.messaging to send notification to a single device token
    """
    if not token:
        return
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {}
    )
    try:
        messaging.send(message)
    except Exception as e:
        # fail silently but log
        print("FCM send error:", e)


@api_view(["GET"])
@permission_classes([AllowAny])
def health(request):
    return Response({"ok": True, "message": "API up"})


# Save or update FCM token for current user
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_fcm_token(request):
    token = request.data.get("token")
    if not token:
        return Response({"error": "token missing"}, status=status.HTTP_400_BAD_REQUEST)

    obj, created = FCMToken.objects.update_or_create(user=request.user, defaults={"token": token})
    return Response({"saved": True})


# Create patient request (patient posts request)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_request(request):
    symptoms = request.data.get("symptoms", "")
    lat = request.data.get("latitude")
    lng = request.data.get("longitude")
    address = request.data.get("address", "")

    dr = DoctorRequest.objects.create(
        patient=request.user,
        symptoms=symptoms,
        latitude=lat,
        longitude=lng,
        address=address,
        status="open",
    )

    # Optionally: notify all doctors (if you have doctor tokens) or nearby doctors logic.
    # For MVP we'll not broadcast; doctors poll /doctor/requests/ to see new ones.

    serializer = DoctorRequestSerializer(dr)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# List requests for the authenticated patient (their own requests)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_patient_requests(request):
    qs = DoctorRequest.objects.filter(patient=request.user).order_by("-created_at")
    ser = DoctorRequestSerializer(qs, many=True)
    return Response(ser.data)


# List open requests for doctors to view (doctors will call this)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_open_requests(request):
    qs = DoctorRequest.objects.filter(status="open").order_by("created_at")
    ser = DoctorRequestSerializer(qs, many=True)
    return Response(ser.data)


# Doctor creates an Offer for a patient request
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_offer(request, request_id):
    try:
        dr = DoctorRequest.objects.get(id=request_id)
    except DoctorRequest.DoesNotExist:
        return Response({"error": "request not found"}, status=status.HTTP_404_NOT_FOUND)

    price = request.data.get("price")
    eta = request.data.get("eta_minutes") or request.data.get("eta")
    message = request.data.get("message", "")

    # basic validation
    if price is None or eta is None:
        return Response({"error": "price and eta_minutes required"}, status=status.HTTP_400_BAD_REQUEST)

    offer = Offer.objects.create(
        request=dr,
        doctor=request.user,
        price=int(price),
        eta_minutes=int(eta),
        message=message
    )

    # Notify patient by FCM
    try:
        token_obj = FCMToken.objects.get(user=dr.patient)
        send_push_to_token(
            token_obj.token,
            title="New Offer",
            body=f"A doctor has offered to visit you (TZS {price}).",
            data={"type": "new_offer", "offer_id": str(offer.id), "request_id": str(dr.id)}
        )
    except FCMToken.DoesNotExist:
        pass

    return Response(OfferSerializer(offer).data, status=status.HTTP_201_CREATED)


# Patient accepts an offer
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_offer(request, offer_id):
    try:
        offer = Offer.objects.get(id=offer_id)
    except Offer.DoesNotExist:
        return Response({"error": "offer not found"}, status=status.HTTP_404_NOT_FOUND)

    # make sure the request belongs to the current patient
    if offer.request.patient != request.user:
        return Response({"error": "not allowed"}, status=status.HTTP_403_FORBIDDEN)

    # mark offer accepted and close request
    offer.accepted = True
    offer.save()
    offer.request.status = "accepted"
    offer.request.save()

    # notify doctor who made this offer
    try:
        token_obj = FCMToken.objects.get(user=offer.doctor)
        send_push_to_token(
            token_obj.token,
            title="Offer Accepted",
            body="Your offer was accepted by the patient.",
            data={"type": "offer_accepted", "offer_id": str(offer.id), "request_id": str(offer.request.id)}
        )
    except FCMToken.DoesNotExist:
        pass

    # Optionally notify other doctors that the request is closed (not implemented)
    return Response({"accepted": True})
