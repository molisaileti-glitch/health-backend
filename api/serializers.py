# api/serializers.py
from rest_framework import serializers
from .models import DoctorRequest, Offer

class OfferSerializer(serializers.ModelSerializer):
    doctor_name = serializers.SerializerMethodField()
    doctor_id = serializers.IntegerField(source="doctor.id", read_only=True)
    doctor_username = serializers.CharField(source="doctor.username", read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "doctor_id", "doctor_username", "price", "eta_minutes", "message", "accepted", "created_at"]

    def get_doctor_name(self, obj):
        return obj.doctor.username

class DoctorRequestSerializer(serializers.ModelSerializer):
    offers = OfferSerializer(many=True, read_only=True)
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    patient_username = serializers.CharField(source="patient.username", read_only=True)

    class Meta:
        model = DoctorRequest
        fields = ["id", "patient_id", "patient_username", "symptoms", "latitude", "longitude", "address", "status", "created_at", "offers"]
