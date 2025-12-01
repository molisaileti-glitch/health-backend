from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Request, Offer, DoctorProfile
from .serializers import RequestSerializer, DoctorProfileSerializer

# Handles Doctor Registration
class DoctorRegistrationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # This assumes the Firestore registration is no longer used,
        # and we register the doctor profile in our Django backend.
        serializer = DoctorProfileSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure a doctor can't register twice
            DoctorProfile.objects.update_or_create(
                user=request.user,
                defaults=serializer.validated_data
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Handles GET for all open requests (for Doctors) and POST to create a request (for Patients)
class RequestListCreateView(generics.ListCreateAPIView):
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only return requests that are currently 'open'
        return Request.objects.filter(status='open')

    def perform_create(self, serializer):
        # When a patient POSTs, automatically assign them as the patient
        serializer.save(patient=self.request.user)

# Handles POST for a doctor to create an offer on a specific request
class OfferCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, request_id):
        try:
            target_request = Request.objects.get(id=request_id, status='open')
        except Request.DoesNotExist:
            return Response({"error": "Request not found or is already closed."}, status=status.HTTP_404_NOT_FOUND)

        # Create the offer for the logged-in doctor
        Offer.objects.create(
            request=target_request,
            doctor=request.user,
            price=request.data.get('price'),
            eta_minutes=request.data.get('eta_minutes'),
            message=request.data.get('message', '')
        )
        return Response({"message": "Offer submitted successfully."}, status=status.HTTP_201_CREATED)

# Handles POST for a patient to accept an offer, which closes the loop
class OfferAcceptView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, offer_id):
        try:
            offer_to_accept = Offer.objects.get(id=offer_id, status='pending')
        except Offer.DoesNotExist:
            return Response({"error": "Offer not found or already handled."}, status=status.HTTP_404_NOT_FOUND)

        parent_request = offer_to_accept.request
        # Security Check: Ensure the user accepting is the patient who made the request
        if parent_request.patient != request.user:
            return Response({"error": "You do not have permission to accept this offer."}, status=status.HTTP_403_FORBIDDEN)

        # Use a transaction to ensure all database changes succeed or fail together
        with transaction.atomic():
            parent_request.status = 'closed'
            parent_request.save()

            offer_to_accept.status = 'accepted'
            offer_to_accept.save()

            # Reject all other pending offers for this request
            parent_request.offers.filter(status='pending').update(status='rejected')
        
        # TODO: Send a push notification to the doctor (`offer_to_accept.doctor`)

        # Return the critical info needed for the live map
        return Response({
            "message": "Offer accepted. The request is now closed.",
            "request_id": parent_request.id,
            "patient_location": {
                "latitude": str(parent_request.latitude),
                "longitude": str(parent_request.longitude)
            },
            "doctor_location": { # In a real app, get this from the doctor's last known location
                 "latitude": "0.0", "longitude": "0.0"
            }
        }, status=status.HTTP_200_OK)
