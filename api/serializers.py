from rest_framework import serializers
from .models import Request, Offer, DoctorProfile

class DoctorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        # --- ADDED 'latitude' and 'longitude' TO THIS LIST ---
        fields = ['full_name', 'phone_number', 'region', 'latitude', 'longitude']

class OfferSerializer(serializers.ModelSerializer):
    # Include the doctor's name from their profile
    doctor_name = serializers.CharField(source='doctor.doctor_profile.full_name', read_only=True)
    doctor_id = serializers.IntegerField(source='doctor.id', read_only=True)

    class Meta:
        model = Offer
        # We only need to send price, eta, and message from the app
        fields = ['id', 'doctor_id', 'doctor_name', 'price', 'eta_minutes', 'message', 'status']
        read_only_fields = ['id', 'doctor_id', 'doctor_name', 'status']

class RequestSerializer(serializers.ModelSerializer):
    # This nests the list of offers within each request, which patient_waiting_page needs
    offers = OfferSerializer(many=True, read_only=True)
    patient_name = serializers.CharField(source='patient.username', read_only=True)

    class Meta:
        model = Request
        fields = ['id', 'patient_name', 'symptoms', 'status', 'created_at', 'offers', 'latitude', 'longitude']
        # The app will send latitude and longitude, but they are not part of the main list view
        extra_kwargs = {
            'latitude': {'write_only': True},
            'longitude': {'write_only': True},
        }
