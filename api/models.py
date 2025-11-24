# api/models.py
from django.db import models
from django.contrib.auth.models import User

class FCMToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=512)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} token"

class DoctorRequest(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    symptoms = models.TextField()
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, default="open")  # open, accepted, closed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Req#{self.id} by {self.patient.username}"

class Offer(models.Model):
    request = models.ForeignKey(DoctorRequest, related_name="offers", on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.IntegerField()
    eta_minutes = models.IntegerField()
    message = models.TextField(null=True, blank=True)
    accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer#{self.id} for Req#{self.request.id}"
